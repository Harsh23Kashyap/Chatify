# Signal Desk reconstruction in progress

This is a NEW reconstruction of the accepted October 30 local news-app example from the preserved original brief and reviewed source mapping. It is not the original saved AI-generated draft or recovered workspace bytes. A bounded development check on October 30 retrieved real NewsAPI excerpts with this native source mapping and produced one direct GPT-4o-mini answer. No current matching video has been restored.

## Scope
Read-only NewsAPI native HTTP connector; no generated Python helper executes. The API key is an X-Api-Key header, never a URL or committed value. The personal OpenAI GPT-4o-mini connection is separate from the news source. Local loopback only. No deployment or public production permission is implied.

## Current checks
Schema validation, synthetic connector checks, current desktop startup and one real native-retrieval/direct-model check passed. A subsequent real current-app pipeline and desktop streaming check produced a source-supported answer with its cited excerpt visible. This is one narrow example, not broad answer-quality proof. A new Build with AI run and matching full usage video remain unverified. Current model documentation marks GPT-4o-mini deprecated even though the request worked on October 30. NewsAPI Developer is local development only, with 24-hour-delayed excerpts and no full articles. Current sources: https://newsapi.org/pricing and https://developers.openai.com/api/docs/models/gpt-4o-mini .

## Before use
Review source-provider terms, API quota and paid model costs. Add your own keys privately in Configuration, never in this YAML or a recording. Keep keys masked. Run from the Chatify repository with `python -m chatify run /path/to/signal-desk/app.yaml --no-browser`, then open the printed local URL. This skeleton must still be checked end to end before it is called ready.
