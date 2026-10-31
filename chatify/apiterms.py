"""Source-verified access terms for API services the builder can recommend.

Model-written drafts must not claim prices or availability. Entries here were
read from each provider's own documentation on the recorded date; attach them
to draft API suggestions so the UI shows verified terms instead of model
claims. Unknown services get an honest "not verified" note, never a guess.
"""

VERIFIED = "2026-10-24"

# key: normalized service-name fragments (lowercase, matched against
# suggestion.service or suggestion.name); value: verified facts.
CATALOG = [
    (("wikipedia", "mediawiki"), {
        "terms": "Free, no API key or account. Polite-use etiquette: identify your app with a User-Agent, keep request rates modest.",
        "docs_url": "https://www.mediawiki.org/wiki/API:Etiquette",
        "key_required": False,
        "source": "https://www.mediawiki.org/wiki/API:Etiquette"}),
    (("pubmed", "ncbi", "e-utilities", "eutils"), {
        "terms": "Free. Anonymous use is rate-limited; a free API key (enforced since Dec 2018) raises the allowance. Registration with NCBI, no card.",
        "docs_url": "https://www.ncbi.nlm.nih.gov/books/NBK25500/",
        "key_required": False,
        "key_url": "https://www.ncbi.nlm.nih.gov/account/settings/",
        "source": "https://www.ncbi.nlm.nih.gov/books/NBK25500/"}),
    (("arxiv",), {
        "terms": "Free under arXiv's API Terms of Use; acknowledge with 'Thank you to arXiv for use of its open access interoperability.' Do not use arXiv branding.",
        "docs_url": "https://info.arxiv.org/help/api/index.html",
        "key_required": False,
        "source": "https://info.arxiv.org/help/api/index.html"}),
    (("openalex",), {
        "terms": "Basic use free without a key. A free API key raises the daily budget 10x; heavier use is pay-as-you-go.",
        "docs_url": "https://developers.openalex.org/guides/authentication",
        "key_url": "https://openalex.org/settings/api",
        "key_required": False,
        "source": "https://developers.openalex.org/guides/authentication"}),
    (("crossref",), {
        "terms": "Free REST API, no key. Add a mailto parameter to use the polite pool for more reliable service.",
        "docs_url": "https://www.crossref.org/documentation/retrieve-metadata/rest-api/",
        "key_required": False,
        "source": "https://www.crossref.org/documentation/retrieve-metadata/rest-api/"}),
    (("reliefweb",), {
        "terms": "Free. Every call must carry an appname parameter identifying your application. Caps: 1000 calls per day, 1000 entries per call.",
        "docs_url": "https://reliefweb.int/help/api",
        "key_required": False,
        "source": "https://reliefweb.int/help/api"}),
    (("launch library", "thespacedevs", "space devs", "spacedevs"), {
        "terms": "Free up to 15 unauthenticated requests per hour. Higher rates are paid via the provider's Patreon tiers.",
        "docs_url": "https://thespacedevs.com/llapi",
        "key_required": False,
        "source": "https://thespacedevs.com/llapi"}),
    (("openf1", "open f1"), {
        "terms": "Free, no signup or key. 3 requests/second and 30 requests/minute; historical data (outside live sessions) is free.",
        "docs_url": "https://openf1.org/",
        "key_required": False,
        "source": "https://openf1.org/"}),
    (("jolpica", "ergast"), {
        "terms": "Free, open-source (Apache 2.0) Formula 1 API, the community Ergast successor. Check its docs for current rate limits.",
        "docs_url": "https://github.com/jolpica/jolpica-f1",
        "key_required": False,
        "source": "https://github.com/jolpica/jolpica-f1"}),
    (("open food facts", "openfoodfacts", "world.openfoodfacts"), {
        "terms": "Free. Reads need no key, only a descriptive User-Agent (15 product reads/min/IP); writes require a free account.",
        "docs_url": "https://openfoodfacts.github.io/openfoodfacts-server/api/",
        "key_required": False,
        "source": "https://openfoodfacts.github.io/openfoodfacts-server/api/"}),
    (("open-meteo", "open meteo"), {
        "terms": "Free for NON-COMMERCIAL use under 10,000 calls/day (5,000/hour, 600/minute). Commercial use needs a paid plan.",
        "docs_url": "https://open-meteo.com/en/terms",
        "key_required": False,
        "source": "https://open-meteo.com/en/terms"}),
    (("openrouteservice", "open route service", "open-route"), {
        "terms": "Standard plan free for everyone (0 EUR) with per-endpoint daily and per-minute quotas (e.g. Directions 10,000/day). Heavier use is paid.",
        "docs_url": "https://openrouteservice.org/plans/",
        "key_required": True,
        "key_url": "https://openrouteservice.org/dev/#/signup",
        "source": "https://openrouteservice.org/plans/"}),
    (("gdelt",), {
        "terms": "Free, no key. DOC 2.0 API full-text searches a rolling 3 months of global news; JSON output.",
        "docs_url": "https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/",
        "key_required": False,
        "source": "https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/"}),
]

UNVERIFIED = ("Access terms not verified by Chatify. Check the provider's current "
              "documentation and pricing before relying on this service - quotas and "
              "free tiers change.")


def lookup(service_or_name):
    """Verified terms dict for a service name, or None when unknown."""
    text = (service_or_name or "").lower()
    for keys, entry in CATALOG:
        if any(k in text for k in keys):
            return dict(entry, verified=VERIFIED)
    return None


def attach(suggestion):
    """Attach verified terms to a draft API suggestion in place.

    Known services: verified terms, docs and key facts REPLACE model-written
    claims. Unknown services: an honest unverified note; model URLs stay but
    are never presented as verified.
    """
    entry = lookup(suggestion.get("service") or suggestion.get("name"))
    if entry:
        suggestion["terms"] = entry["terms"]
        suggestion["terms_source"] = entry["source"]
        suggestion["terms_verified"] = entry["verified"]
        suggestion["docs_url"] = entry["docs_url"]
        suggestion["key_required"] = entry["key_required"]
        if entry.get("key_url"):
            suggestion["key_url"] = entry["key_url"]
        else:
            suggestion.pop("key_url", None)
    else:
        suggestion["terms"] = UNVERIFIED
    return suggestion
