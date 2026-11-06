# WeatherChat

Live weather for any place you name, with the source cited. Built on Chatify.

- Ask: "What is the weather in Bangalore right now?", "Will it rain in Mumbai tomorrow?",
  "How hot is Delhi this week?"
- When a place resolves, answers cite Open-Meteo data retrieved at ask time (cached
  up to 15 minutes; each source shows its Retrieved time): current conditions, today
  and the next hours, tomorrow, and a 7-day forecast, with validity and forecast
  times and the place's own timezone. Units are metric (degrees C, mm, km/h).
  Current conditions are Open-Meteo model data valid at the stated time, not station
  observations; precipitation is reported as the sum over the minutes up to that
  time. When no place resolves, the app says so instead of citing weather, and when
  a name matches several places evenly (for example Cambridge), it lists the
  candidates and fetches no weather for any of them. Answers are model-generated:
  the app checks citations against the sources and labels answers it cannot
  confirm, but labels like "Not independently verified" are part of the UI, not a
  guarantee of correctness.
- The place comes only from your question. If none is named or found, the app asks
  you to name one; it never assumes a location. Renamed cities resolve to their
  current names (Bangalore -> Bengaluru, Bombay -> Mumbai, ...); ambiguous names
  list the alternatives so you can ask again more specifically.

## Data source and its conditions

Weather data: [Open-Meteo](https://open-meteo.com/) free API - no key required.
Location names: GeoNames via Open-Meteo geocoding. Data licence: CC BY 4.0
(attribution required, which is why the footer and every answer credit
"Weather data by Open-Meteo.com").

Open-Meteo's free tier is for **non-commercial use only**, capped at
10,000 calls/day (5,000/hour, 600/minute), with no uptime guarantee; calls are
rate-limited per IP, so shared hosts may be limited earlier. This app is allowed
only while its actual use stays non-commercial (personal, educational,
unpaid open-source demonstration with no ads or subscriptions). If it is ever
run as or inside a commercial product or promotion, the operator must move to an
Open-Meteo paid plan first. Terms: https://open-meteo.com/en/terms -
Licence: https://open-meteo.com/en/license

Forecasts are model predictions, not guarantees; re-ask for the latest conditions.

## Run locally

```sh
chatify run apps/weatherchat/app.yaml     # or: python -m chatify run apps/weatherchat/app.yaml
```

You need a model to answer questions: the default provider is a local Ollama
model (install Ollama and pull llama3.2), or edit `provider` in app.yaml to use a
hosted model with its API key. Hosted/gallery runs override it with the host key.
Only the weather source needs no key or setup.

## Tests

```sh
cd apps/weatherchat
PYTHONPATH=../..:. python3 -m unittest test_weatherchat -v
WEATHERCHAT_LIVE=1 PYTHONPATH=../..:. python3 -m unittest test_weatherchat.LiveTests -v   # hits the real API
```

## Verified 2026-11-05 (baseline 957ddac)

- 31 offline unit regressions pass (`test_weatherchat.py`); the 32nd is a live
  Open-Meteo smoke test, skipped unless WEATHERCHAT_LIVE=1.
- Current-version verification is offline: the deterministic clarification,
  unique per-place item IDs, no-forecast-on-ambiguity, and wording rules are
  covered by the mocked unit regressions above. No real-model run of the current
  connector version has been done.
- Earlier the same day, a prior version of the connector was also exercised
  through the app with a real model (gpt-4o-mini): Bangalore current weather
  (resolved to Bengaluru, Karnataka, Asia/Kolkata), Mumbai rain tomorrow, Delhi
  week temperatures, London today, San Francisco, Chennai humidity, Delhi wind,
  Jaipur sunset time, Bombay -> Mumbai rename, two-place comparisons ("Compare the
  weather in Delhi and Mumbai today" covered both places and stated which were
  covered), "weather between Chennai and Bangalore", compound names like Trinidad
  and Tobago staying one place, multi-turn follow-up ("and will it rain there
  tomorrow?" kept Bangalore), and honest no-evidence guidance for placeless or
  unresolvable questions. Those runs are historical evidence for the prior version,
  not acceptance of the current one: in them, Cambridge still resolved silently to
  England (the deterministic clarification replaced that behavior afterwards), and
  answer wording varied run to run (one run used "recorded" for model precipitation
  data).

Known limits:
- Two-place questions resolve at most two places; a question naming three or more
  gets evidence for the first two resolved, and the model is instructed to say which
  places are covered and which are not.
- Ambiguous names are handled deterministically in the connector: two or more
  strong matches where the top one does not dominate (10x population) return a
  candidate list and no weather. A dominant match (for example London, UK over
  London, Ontario) still resolves, with the alternatives noted in every source.
  Small models may phrase the clarification or the alternatives differently; the
  candidate list and the place note come from the connector, not the model.
- Follow-up place continuity ("there", "and tomorrow?") relies on the model
  history-aware query rewrite; with the offline demo provider each question must
  name its place.
- The answer pipeline occasionally leaks a "Draft:" scaffold prefix into the
  rendered answer (core Chatify behavior, not app-specific).
- Desktop and mobile chat layouts verified with real screenshots during the same
  run.
