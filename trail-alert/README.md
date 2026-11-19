# Alerte Telegram – places Duo du Trail des Crêtes

Toutes les 5 minutes, GitHub Actions ouvre la [page d'inscription](https://forms.registration4all.com/EventRegistration/Register_Sport_Event.aspx?EventID=233725&RORG=LSCAL),
lit le nombre de **duos** (équipes) restants au **Trail des Crêtes 65 km en Duo** et poste un message dans le groupe Telegram :

- quand il reste **moins de 30** duos,
- puis à nouveau sous 20, 10 et 5 duos, et quand c'est complet (pas de spam entre deux paliers).

## Mise en place (10 min)

1. **Créer le bot** : sur Telegram, écrire à `@BotFather` → `/newbot` → noter le **token**.
2. **Ajouter le bot au groupe**, puis y envoyer un message quelconque (ex. `/start`).
3. **Récupérer l'id du groupe** : ouvrir `https://api.telegram.org/bot<TOKEN>/getUpdates`
   et repérer `"chat":{"id":-100...}`. C'est le **chat id** (il commence par `-`).
4. **Ajouter les secrets** dans GitHub : *Settings → Secrets and variables → Actions → New repository secret*
   - `TELEGRAM_BOT_TOKEN` = le token
   - `TELEGRAM_CHAT_ID` = l'id du groupe
5. **Tester** : onglet *Actions* → *Alerte places Duo Trail des Crêtes* → *Run workflow*.
   Le journal affiche « Duos restants : N ».

## Commande /places

Envoie `/places` au bot pour connaître le nombre de duos restants.
La réponse arrive à la vérification suivante (toutes les 5 min en théorie ; GitHub retarde souvent
les tâches planifiées, compter 5 à 15 min).

Pour que la commande apparaisse dans le menu du bot : `@BotFather` → `/setcommands` → choisir le bot
→ envoyer `places - Nombre de places Duo restantes`.

## Réglages

Dans `.github/workflows/trail-duo-alert.yml` :
- `THRESHOLD` : seuil d'alerte (30 par défaut)
- `RACE_WORDS` : mots qui repèrent la course sur la page (`trail des crêtes,duo`)
- `THRESHOLD` compte des **duos** (équipes), pas des coureurs
- `cron` : fréquence de vérification

Si la page change de présentation et que le nombre est introuvable, le bot envoie un
avertissement une seule fois dans le groupe, et le journal Actions montre le texte de la page
pour ajuster les motifs dans `check_duo.py`.

Test en local sans envoyer de message :

```bash
pip install playwright && python -m playwright install chromium
DRY_RUN=1 python trail-alert/check_duo.py
```
