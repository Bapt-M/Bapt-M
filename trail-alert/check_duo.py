#!/usr/bin/env python3
"""Surveille les places restantes en Duo du Trail des Crêtes et alerte un groupe Telegram.

Variables d'environnement :
  TELEGRAM_BOT_TOKEN  token du bot (fourni par @BotFather)          [obligatoire]
  TELEGRAM_CHAT_ID    id du groupe (ex. -1001234567890)              [obligatoire]
  EVENT_URL           page d'inscription (valeur par défaut ci-dessous)
  RACE_WORDS          mots du nom de la course (défaut : "trail des crêtes,duo")
  THRESHOLD           seuil d'alerte (défaut : 30)
  STATE_FILE          fichier qui mémorise les alertes déjà envoyées
  DRY_RUN=1           affiche le message au lieu de l'envoyer
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

EVENT_URL = os.environ.get(
    "EVENT_URL",
    "https://forms.registration4all.com/EventRegistration/Register_Sport_Event.aspx"
    "?EventID=233725&RORG=LSCAL",
)
# Mots qui doivent tous figurer dans le nom de la course (séparés par des virgules)
RACE_WORDS = [
    w.strip().lower()
    for w in os.environ.get("RACE_WORDS", "trail des crêtes,duo").split(",")
    if w.strip()
]
THRESHOLD = int(os.environ.get("THRESHOLD", "30"))
STATE_FILE = os.environ.get("STATE_FILE", "state/duo_state.json")
DRY_RUN = os.environ.get("DRY_RUN") == "1"

# Paliers : une alerte au passage sous 30, puis sous 20, 10, 5, et quand c'est complet.
STEPS = sorted({THRESHOLD, 20, 10, 5, 0}, reverse=True)

# Formulations courantes autour du nombre de places
NUM_PATTERNS = [
    r"(\d+)\s*(?:places?|dossards?|spots?|inscriptions?)\s*(?:restantes?|disponibles?|libres?|left|remaining|available)",
    r"(?:restantes?|disponibles?|remaining|available|left)\s*[:\-]?\s*(\d+)",
    r"(?:places?|spots?)\s*(?:restantes?|disponibles?)\s*[:\-]?\s*(\d+)",
]
FULL_PATTERN = r"\b(complet|sold\s*out|full|liste d'attente|waiting list)\b"


def fetch_text() -> str:
    """Rend la page avec un vrai navigateur (le site peut charger les places en JavaScript)."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(locale="fr-FR")
        page.goto(EVENT_URL, wait_until="networkidle", timeout=60_000)
        text = page.inner_text("body")
        browser.close()
    return text


def find_remaining(text: str):
    """Renvoie (nombre de duos restants ou None, extrait de la page).

    Sur la page, chaque course ressemble à :
        Le Trail des Crêtes 65km en DUO
        TRAIL, COURSE NATURE - 65 km -
        7:00
        né(e)s le 02/07/2007 et avant
        PLACES DISPONIBLES: 318 = 159 équipes
        S'INSCRIRE
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for i, line in enumerate(lines):
        low = line.lower()
        if not all(w in low for w in RACE_WORDS):
            continue
        # Bloc de la course : jusqu'au bouton S'INSCRIRE (ou 10 lignes max)
        block = []
        for l in lines[i : i + 10]:
            block.append(l)
            if "inscrire" in l.lower():
                break
        window = " | ".join(block)
        m = re.search(
            r"places?\s+disponibles?\s*:\s*(\d+)(?:\s*=\s*(\d+)\s*[ée]quipes?)?",
            window,
            re.IGNORECASE,
        )
        if m:
            places, teams = int(m.group(1)), m.group(2)
            return (int(teams) if teams else places // 2), window
        if re.search(FULL_PATTERN, window, re.IGNORECASE):
            return 0, window
        for pat in NUM_PATTERNS:
            m = re.search(pat, window, re.IGNORECASE)
            if m:
                return int(m.group(1)) // 2, window
    return None, None


def load_state() -> dict:
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE) or ".", exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)


def telegram_api(method: str, params: dict) -> dict:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    data = urllib.parse.urlencode(params).encode()
    url = f"https://api.telegram.org/bot{token}/{method}"
    with urllib.request.urlopen(url, data=data, timeout=30) as r:
        return json.load(r)


def send_telegram(message: str, chat_id=None) -> None:
    if DRY_RUN:
        print("[DRY_RUN] " + message)
        return
    chat_id = chat_id or os.environ["TELEGRAM_CHAT_ID"]
    res = telegram_api(
        "sendMessage",
        {"chat_id": chat_id, "text": message, "disable_web_page_preview": "true"},
    )
    print("Telegram :", "ok" if res.get("ok") else res)


def places_message(remaining) -> str:
    if remaining is None:
        return f"🤷 Je ne trouve pas le nombre de places Duo sur la page.\n{EVENT_URL}"
    if remaining == 0:
        return f"🚫 Trail des Crêtes : le Duo est COMPLET.\n{EVENT_URL}"
    return f"🏃 Trail des Crêtes : il reste {remaining} duos (équipes) en 65 km Duo.\nInscription : {EVENT_URL}"


def answer_commands(remaining, state: dict) -> None:
    """Répond aux commandes /places reçues depuis la dernière vérification."""
    if DRY_RUN:
        return
    params = {"timeout": 0, "allowed_updates": '["message"]'}
    if state.get("update_offset"):
        params["offset"] = state["update_offset"]
    try:
        updates = telegram_api("getUpdates", params).get("result", [])
    except Exception as e:  # une panne Telegram ne doit pas bloquer l'alerte
        print("getUpdates en échec :", e)
        return
    answered = set()
    for u in updates:
        state["update_offset"] = u["update_id"] + 1
        msg = u.get("message") or {}
        text = (msg.get("text") or "").strip().lower()
        chat_id = (msg.get("chat") or {}).get("id")
        # Accepte /places et /places@NomDuBot (utile dans un groupe)
        if chat_id and text.split("@")[0].split()[0:1] == ["/places"] and chat_id not in answered:
            send_telegram(places_message(remaining), chat_id=chat_id)
            answered.add(chat_id)


def main() -> int:
    state = load_state()
    text = fetch_text()
    remaining, snippet = find_remaining(text)
    answer_commands(remaining, state)
    save_state(state)

    if remaining is None:
        print("Compteur Duo introuvable. Début du texte de la page :\n" + text[:3000])
        if not state.get("parse_error_sent"):
            send_telegram(
                "⚠️ Alerte Trail des Crêtes : je ne trouve plus le nombre de places Duo "
                f"sur la page. À vérifier à la main : {EVENT_URL}"
            )
            state["parse_error_sent"] = True
            save_state(state)
        return 1

    print(f"Duos restants : {remaining}  (extrait : {snippet!r})")
    state["parse_error_sent"] = False
    last_step = state.get("last_step")  # dernier palier déjà annoncé

    # Palier le plus bas atteint
    reached = [s for s in STEPS if remaining <= s and (s < THRESHOLD or remaining < THRESHOLD)]
    step = min(reached) if reached else None

    if step is not None and (last_step is None or step < last_step):
        if remaining == 0:
            msg = places_message(0)
        else:
            msg = (
                f"🏃‍♂️🏃‍♀️ Trail des Crêtes : plus que {remaining} duos dispo en 65 km Duo !\n"
                f"Inscription : {EVENT_URL}"
            )
        send_telegram(msg)
        state["last_step"] = step
    elif step is None and last_step is not None:
        # Des places ont été libérées : on repart de zéro
        state["last_step"] = None

    state["last_remaining"] = remaining
    save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
