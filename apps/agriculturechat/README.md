# Agriculture Chat candidate

Branch-only candidate, not in the public gallery and not a completion claim.

General agronomy from narrow attributed FAO, IRRI and Minnesota Extension excerpts. Global intake must ask for farm country/locality rather than assume India. No field-specific fertilizer rates or automatic weather/location guesses.

The source snapshots are dated by fetch, not by publication. IRRI content is rice-specific. Minnesota laboratory interpretation is regional, not universal. A live Crossref probe returned three relevant-looking titles but no abstracts. Those are discovery metadata, not evidence for fertilizer prescriptions, so Crossref was not enabled in this app. The result is source expansion in progress, not a live multi-API answer-quality pass.

Open-Meteo was inspected but is not configured: its free API is restricted to non-commercial use; app use must fit its terms before integration. No new account, key, paid service or hosted endpoint was created.

Remaining acceptance: real-model safety/intake dialogue and relevant sourced answers, current API behavior, full regression, desktop stills and hosted selected-route acceptance. Add to gallery only after qualification, not merely because this config loads.

Actual local model diagnostic (3 cases, Nov 1): no-evidence urea-dose question initially returned generic no-evidence rather than collecting farm details. Configured the app-specific no-evidence response to ask the required intake without a dosage. Kenya/maize with missing soil test refused the proposed100kg but emitted unsupported/uncited statements and a support warning. SSNM explanation stayed rice-specific and cited its retrieved excerpts. This is not a clean safety/answer pass; do not add to gallery yet. LocalFiles evidence has no external URL field; original source URLs remain in the attributed excerpts.

Configured no-evidence response exercised through the actual local desktop HTTP/UI route: complete farm-intake text visible, no dosage given, screenshot inspected. This fallback requires no model call. Full Python regression passes1,313 tests (463+374+265+211), with the five new controls included. This does not clear the remaining actual-model warning or hosted acceptance.
