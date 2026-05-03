# NicoWay

NicoWay e un piccolo backend personale per monitorare deal di viaggio per una coppia. Non ha frontend web: l'interazione principale passa da Telegram Bot, mentre FastAPI espone endpoint interni utili per debug e amministrazione.

Il tono del bot e caldo e personale: segnala combinazioni volo + hotel quando il prezzo, gli orari e la qualita complessiva meritano attenzione.

## Architettura

- `app/domain`: entita di dominio, value object e scoring.
- `app/application/services`: orchestrazione di ricerche, valutazione deal, notifiche e scheduler.
- `app/infrastructure/db`: SQLAlchemy, repository e migration Alembic.
- `app/infrastructure/providers`: interfacce astratte e provider mock per voli e hotel.
- `app/infrastructure/telegram`: bot Telegram e command handler.
- `app/api`: endpoint FastAPI interni.
- `tests`: test unitari e integrazione leggera con SQLite in memory.

NicoWay non fa scraping fragile. I provider reali vanno aggiunti come adapter che implementano `FlightProvider` o `HotelProvider` e restituiscono `FlightOffer` e `HotelOffer` normalizzati.

## Configurare Telegram

1. Apri Telegram e crea un bot con `@BotFather`.
2. Copia il token.
3. Crea il file `.env`:

```bash
cp .env.example .env
```

4. Imposta `TELEGRAM_BOT_TOKEN` nel file `.env`.

Se il token e vuoto, l'API FastAPI parte comunque e il polling Telegram resta disabilitato.

## Avvio Locale

```bash
cp .env.example .env
docker compose up --build
```

FastAPI sara disponibile su `http://localhost:8000`.

Endpoint utili:

- `GET /health`
- `GET /searches`
- `GET /searches/{id}`
- `POST /searches/{id}/check`
- `GET /deals/{search_id}`

## Comandi Telegram

- `/start`: registra l'utente e presenta NicoWay.
- `/help`: mostra i comandi disponibili.
- `/newsearch`: conversazione guidata per creare una ricerca.
- `/searches`: lista ricerche con stato.
- `/enable <search_id>`: attiva una ricerca.
- `/disable <search_id>`: mette in pausa una ricerca.
- `/delete <search_id>`: elimina una ricerca.
- `/check <search_id>`: forza un controllo manuale.
- `/best <search_id>`: mostra il miglior deal trovato.
- `/settings`: mostra soglie e impostazioni base.

Esempio ricerca:

- Nome: `Scozia 2026`
- Partenza: `FCO`
- Destinazione: `Edimburgo`
- Date: `2026-08-31` / `2026-09-14`
- Flessibilita: `2`
- Adulti: `2`
- Budget totale: `1800`
- Max volo: `350`
- Max hotel/notte: `120`

## Scoring e Notifiche

Lo score considera prezzo volo, prezzo hotel, totale stimato, scali, durata, finestre orarie preferite, rating, stelle e miglioramento rispetto allo storico.

Le soglie configurabili sono:

- `MIN_PRICE_IMPROVEMENT_PERCENT`
- `MIN_SCORE_IMPROVEMENT`
- `NOTIFICATION_COOLDOWN_HOURS`
- `DEFAULT_CHECK_FREQUENCY_MINUTES`

Una notifica viene inviata solo se il deal e sotto budget e rappresenta il primo buon riferimento, un miglioramento prezzo sufficiente o un miglioramento score significativo. Le notifiche identiche recenti vengono bloccate dal cooldown.

## Aggiungere Provider Reali

Per un provider voli:

1. Crea un modulo in `app/infrastructure/providers/flights/`.
2. Implementa `FlightProvider`.
3. Converti la risposta dell'API esterna in `FlightOffer`.
4. Non loggare token o payload sensibili.
5. Sostituisci `MockFlightProvider` nella factory/orchestrazione applicativa.

Per un provider hotel, segui lo stesso schema con `HotelProvider` e `HotelOffer`.

Sono preferibili API ufficiali o servizi terzi con termini chiari. Lo scraping aggressivo di siti complessi non e parte dell'MVP.

## Test e Qualita

```bash
pytest
ruff check .
ruff format .
```

`mypy` e configurato come controllo opzionale:

```bash
mypy app
```

## Roadmap

Fase 1 MVP:

- bot Telegram;
- ricerche configurabili;
- provider mock;
- scoring;
- notifiche;
- storico prezzi.

Fase 2:

- integrazione provider reali tramite API ufficiali;
- supporto multi-destinazione;
- alert su singolo volo;
- alert su pacchetto volo + hotel;
- grafico storico prezzi esportabile;
- suggerimenti "conviene aspettare o comprare".

Fase 3:

- AI assistant per suggerire destinazioni alternative;
- analisi stagionalita;
- suggerimenti su aeroporti vicini;
- classificazione automatica dei deal;
- deploy Kubernetes con Helm chart.
