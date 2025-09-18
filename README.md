# PROTRDX

Pipeline quotidien combinant recherche d'actualités, calcul de features, LLM et backtest rapide pour produire un rapport Telegram et une UI de pilotage.

## Configuration

1. Copier `.env.example` vers `.env` et renseigner les secrets.
2. Créer un bot Telegram via [@BotFather](https://core.telegram.org/bots#botfather) et récupérer `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID`.
3. Renseigner les clés API OpenAI et Perplexity/Tavily.
4. Ajuster les paramètres de risque et de scheduler si besoin.

## Démarrage local

```bash
make venv
source .venv/bin/activate
make seed
uvicorn app.backend.main:app --reload
```

Dans un autre terminal pour le front :

```bash
cd app/frontend
npm install
npm run dev
```

L'UI est accessible sur http://localhost:3000. Backend sur http://localhost:8000/docs.

## Docker

```bash
make up
```

## Commandes Makefile

- `make dev` : lance backend (uvicorn) + frontend (Next.js) en parallèle.
- `make fmt` : exécute ruff + mypy.
- `make test` : lance la suite pytest.
- `make seed` : insère les tickers AAPL, NVDA, MSFT, BTC-USD, EURUSD=X.

## API principale

- `POST /api/run` : déclenche le pipeline complet.
- `POST /api/run/{ticker}` : pipeline sur un ticker.
- `GET /api/jobs` : liste des jobs.
- `GET /api/jobs/{id}` : détails + résultats.
- `GET /api/charts/{filename}` : télécharge un PNG généré.
- `GET/POST /api/settings` : lecture/écriture des paramètres.
- `GET/POST/DELETE /api/watchlist` : CRUD sur les tickers.

Headers requis : `x-admin-password`.

### Exemple cURL

```bash
curl -X POST http://localhost:8000/api/run \
  -H "x-admin-password: change_me"
```

## Tests

```bash
make test
```

## Limites connues

- Backtest simplifié (momentum) pour sanity-check uniquement.
- LLM dépend d'OpenAI (`gpt-4o-mini`).
- Mode paper trading, aucune exécution réelle.

## Capture UI

Une fois `npm run dev` lancé, ouvrir http://localhost:3000 et capturer une capture d'écran (ex: via outil système) pour documentation.
