# NewsNerd sample on Chatify

This is an app.yaml instance of Chatify 0.1.6, like apps/dietchat-sample. No separate application or backend.

From the Chatify repository root:

```sh
python -m chatify run apps/newsnerd-sample/app.yaml
```

Or with the installed public package:

```sh
chatify-app run apps/newsnerd-sample/app.yaml
```

Opens on http://127.0.0.1:8081. Offline Demo works without keys. Ask "What is NewsNerd?" to test local guide retrieval. This is not live news.

For real news: copy .env.example to .env within apps/newsnerd-sample, fill GNEWS_API_KEY, run local Ollama with qwen2.5:3b, then from the repository root:

```sh
python -m chatify run apps/newsnerd-sample/app-gnews.yaml
```

NewsAPI alternative: fill NEWSAPI_KEY instead and use app-newsapi.yaml. All supported config fields are filled; only secret values are blank. Complete per-field reference in CONFIG-FIELDS.md; stages in PROMPTS.md; API limits/troubleshooting in SETUP.md.

No existing workspace is reset. Local chats persist in this sample's data folder. Both free news plans are local development/testing only, not public deployment. GNews Free is delayed 12 hours; NewsAPI Developer 24 hours. No live API/model test performed; adapter tests use a fixture.
