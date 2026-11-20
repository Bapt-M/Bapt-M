// Bot Telegram « Trail des Crêtes » sur Cloudflare Workers.
// - Toutes les 5 minutes (cron) : lit les duos restants et alerte sous 30, 20, 10, 5, complet.
// - Webhook Telegram : répond tout de suite à /places.
//
// Secrets : TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, WEBHOOK_SECRET
// KV      : STATE (mémorise le dernier palier annoncé)

const EVENT_URL =
  "https://forms.registration4all.com/EventRegistration/Register_Sport_Event.aspx?EventID=233725&RORG=LSCAL";
const RACE_WORDS = ["trail des crêtes", "duo"];
const THRESHOLD = 30;
const STEPS = [30, 20, 10, 5, 0];

// ---------- Lecture de la page ----------

function pageToLines(html) {
  const text = html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<(br|\/div|\/p|\/tr|\/td|\/li|\/h\d|\/span|\/a)[^>]*>/gi, "\n")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(+n))
    .replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCharCode(parseInt(n, 16)))
    .replace(/&amp;/g, "&")
    .replace(/&eacute;/g, "é")
    .replace(/&ecirc;/g, "ê")
    .replace(/&egrave;/g, "è")
    .replace(/&apos;|&#39;/g, "'");
  return text
    .split("\n")
    .map((l) => l.replace(/\s+/g, " ").trim())
    .filter(Boolean);
}

export function findRemaining(html) {
  const lines = pageToLines(html);
  for (let i = 0; i < lines.length; i++) {
    const low = lines[i].toLowerCase();
    if (!RACE_WORDS.every((w) => low.includes(w))) continue;
    const block = [];
    for (const l of lines.slice(i, i + 15)) {
      block.push(l);
      if (l.toLowerCase().includes("inscrire")) break;
    }
    const win = block.join(" | ");
    const m = win.match(/places?\s+disponibles?\s*:\s*(\d+)(?:\s*=\s*(\d+)\s*[ée]quipes?)?/i);
    if (m) return { remaining: m[2] ? +m[2] : Math.floor(+m[1] / 2), snippet: win };
    if (/\b(complet|sold\s*out|liste d'attente)\b/i.test(win)) return { remaining: 0, snippet: win };
  }
  return { remaining: null, snippet: null };
}

async function readRemaining() {
  const res = await fetch(EVENT_URL, {
    headers: { "User-Agent": "Mozilla/5.0", "Accept-Language": "fr-FR,fr;q=0.9" },
  });
  if (!res.ok) throw new Error(`Page HTTP ${res.status}`);
  return findRemaining(await res.text());
}

// ---------- Telegram ----------

async function tg(env, method, params) {
  const res = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/${method}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(params),
  });
  return res.json();
}

const send = (env, text, chatId) =>
  tg(env, "sendMessage", {
    chat_id: chatId || env.TELEGRAM_CHAT_ID,
    text,
    disable_web_page_preview: true,
  });

function placesMessage(remaining) {
  if (remaining === null) return `🤷 Je ne trouve pas le nombre de duos sur la page.\n${EVENT_URL}`;
  if (remaining === 0) return `🚫 Trail des Crêtes : le 65 km Duo est COMPLET.\n${EVENT_URL}`;
  return `🏃 Trail des Crêtes : il reste ${remaining} duos (équipes) en 65 km Duo.\nInscription : ${EVENT_URL}`;
}

// ---------- Vérification planifiée ----------

async function check(env) {
  const state = JSON.parse((await env.STATE.get("state")) || "{}");
  let remaining;
  try {
    ({ remaining } = await readRemaining());
  } catch (e) {
    remaining = null;
    console.log("Lecture impossible :", e.message);
  }
  console.log("Duos restants :", remaining);

  if (remaining === null) {
    if (!state.parseErrorSent) {
      await send(env, `⚠️ Alerte Trail des Crêtes : je ne trouve plus le nombre de duos. À vérifier : ${EVENT_URL}`);
      state.parseErrorSent = true;
    }
  } else {
    state.parseErrorSent = false;
    const reached = STEPS.filter((s) => remaining <= s && (s < THRESHOLD || remaining < THRESHOLD));
    const step = reached.length ? Math.min(...reached) : null;
    if (step !== null && (state.lastStep == null || step < state.lastStep)) {
      await send(
        env,
        remaining === 0
          ? placesMessage(0)
          : `🏃‍♂️🏃‍♀️ Trail des Crêtes : plus que ${remaining} duos dispo en 65 km Duo !\nInscription : ${EVENT_URL}`,
      );
      state.lastStep = step;
    } else if (step === null) {
      state.lastStep = null; // des places ont été libérées
    }
    state.lastRemaining = remaining;
  }
  await env.STATE.put("state", JSON.stringify(state));
}

// ---------- Point d'entrée ----------

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(check(env));
  },

  async fetch(request, env) {
    const url = new URL(request.url);

    // Branche le webhook Telegram : ouvrir /setup?key=WEBHOOK_SECRET une fois
    if (url.pathname === "/setup") {
      if (url.searchParams.get("key") !== env.WEBHOOK_SECRET) return new Response("Clé invalide", { status: 403 });
      const r = await tg(env, "setWebhook", {
        url: `${url.origin}/webhook`,
        secret_token: env.WEBHOOK_SECRET,
        allowed_updates: ["message"],
      });
      await tg(env, "setMyCommands", {
        commands: [{ command: "places", description: "Nombre de duos restants" }],
      });
      return Response.json(r);
    }

    // Messages reçus par le bot
    if (url.pathname === "/webhook" && request.method === "POST") {
      if (request.headers.get("X-Telegram-Bot-Api-Secret-Token") !== env.WEBHOOK_SECRET)
        return new Response("Interdit", { status: 403 });
      const update = await request.json();
      const msg = update.message || {};
      const cmd = (msg.text || "").trim().toLowerCase().split(/[\s@]/)[0];
      if (cmd === "/places" && msg.chat) {
        let remaining = null;
        try {
          ({ remaining } = await readRemaining());
        } catch (e) {
          console.log("Lecture impossible :", e.message);
        }
        await send(env, placesMessage(remaining), msg.chat.id);
      }
      return new Response("ok");
    }

    // Petite page de contrôle
    if (url.pathname === "/") {
      const state = await env.STATE.get("state");
      return new Response(`Bot Trail des Crêtes actif.\nÉtat : ${state || "{}"}`);
    }
    return new Response("Introuvable", { status: 404 });
  },
};
