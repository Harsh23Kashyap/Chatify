# PeaceChat sources

PeaceChat uses ReliefWeb humanitarian reports as its primary reporting source,
with Crossref research and Wikipedia for additional evidence. Reports do not
by themselves establish that a peace effort succeeded; the answer should name
the reporting organization, date and any limits in the evidence.

Request an approved appname at https://apidoc.reliefweb.int/ and set
`RELIEFWEB_APPNAME` in the environment before starting PeaceChat. On Render,
set it in the service's Environment settings. The value is not an API key,
but it identifies your application's API usage. It is intentionally not
bundled with the example. Never use an unapproved placeholder.

The adapter uses the v2 reports API. Missing appname or API failures are
reported as source errors, not silently replaced with invented evidence.
The old `peace_sources:gdelt` entry point remains available for existing
configurations, but is no longer the default for this example.
