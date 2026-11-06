# WeatherChat

Current conditions and a 3-day daily forecast for a place named in your question.
Weather data by [WeatherAPI.com](https://www.weatherapi.com/).

- Current fields: temperature, feels-like temperature, relative humidity and wind speed.
- Daily fields: high/low temperature, rain chance, total precipitation and maximum wind.
  The 3-day window and "next N days" include today in the named place's timezone.
  Supported time requests: current/now, today, tomorrow, next 1-3 days or an ISO date
  within those three days. Weekdays, named months, hours and other time expressions
  fail closed instead of silently returning current conditions.
- Every answer binds selected native source fields to the exact place, time, timezone,
  units and citation. Forecasts are predictions, including a 0% rain chance, not guarantees.
- Current precipitation is not exposed because its accumulation period was not documented.
  Hourly answers, sunrise/UV, advice and a full-week forecast are not supported here.
- A matching location must come from the question, never the server's IP or assumed location.
  Ambiguous names return candidates without fetching a forecast. Ask one place at a time.
- Retrieved data can be cached for 15 minutes. Each source shows its retrieval time and
  the provider's current-data update time or forecast date. A retrieved timestamp is not
  a guarantee of freshness or accuracy. Do not use this app for safety-critical decisions;
  consult official governmental weather reports and advisories.

## Setup and plan limits

Set `WEATHERAPI_API_KEY` in the server environment. Keep this key private, never in a
question, source URL, shared config, screenshot or exported chat. Outbound API URLs
carry the key only in the server request; public-safe failures omit the URL and body.
A model is also needed: local Ollama by default, or a configured hosted provider.
The gallery uses its existing server-side model configuration.

WeatherAPI Free supports 100,000 calls/month, current weather and three forecast days.
Quota exhaustion stops data; this app has no retry, fallback, top-up or upgrade route.
Signup may begin a no-card, no-obligation Business trial that automatically becomes
Free. Do not call the trial an active Free plan or depend on trial-only capabilities.
No card or payment is needed for this configuration. The operator remains responsible
for the provider's current terms: https://www.weatherapi.com/terms and
https://www.weatherapi.com/pricing . One key is dedicated to this WeatherChat service.

```sh
chatify run apps/weatherchat/app.yaml
PYTHONPATH=.:apps/weatherchat python -m unittest apps.weatherchat.test_weatherapi_preparation tests.test_weather_answer_contract tests.test_weather_host_diagnostics
```

The legacy `weather_sources.py` and its offline fixtures remain for historical
regression evidence only; the active configuration does not call Open-Meteo.
Do not enable its opt-in live test to retry the previously throttled hosted endpoint.

## Acceptance status

Nov 7 source-only check: exactly one Bangalore search and one three-day forecast
request returned current plus daily fields. This is not a model-answer or hosted
acceptance claim. Current changes require independent review and actual hosted
current/tomorrow answer, attribution and persistence verification before completion.

## Historical verification, not current WeatherAPI acceptance

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
