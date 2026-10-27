# Earliest design brief and reproducible comparison

Earliest authenticated full mission located: October25 03:53:41IST, WhatsApp message wamid.HBgMOTE4MDUxNjI1NjY5FQIAEhgUM0EyQjdBQzBCODczMkM2RTI5OEIA. Repeated08:45:13/12:59:34/20:17:50; do not mistake a repeat for the start. Parent routed03:53:58: design authority with audit/research first and coordinated writer handoff; existing functional fixes continued. Existing campaign began October10.

Last commit before earliest brief: 14b7f2fff313d8908cee49604393e66653d950aa (October25 03:32:17IST). Checkpoint 2fc0c62eb01f6195dfcf7506dbe8e67fd98fa696. This is an exact committed comparison; git timestamps do not establish absence of uncommitted work at03:53. It includes concurrent functional fixes as well as redesign and cannot attribute every path exclusively to design. No dated original before screenshot established.

584 files changed, 81292 insertions(+), 449 deletions(-)

## UI paths

- chatify/web/app.js
- chatify/web/appbuilder.js
- chatify/web/appearanceextras.js
- chatify/web/brand.js
- chatify/web/build.css
- chatify/web/build.html
- chatify/web/build.js
- chatify/web/builderstudio.css
- chatify/web/components.css
- chatify/web/configurationhome.css
- chatify/web/fonts/FONTS.md
- chatify/web/fonts/NotoNaskhArabic[wght].ttf
- chatify/web/fonts/NotoSansHebrew[wdth,wght].ttf
- chatify/web/fonts/NotoSansMath-OFL.txt
- chatify/web/fonts/NotoSansMath-Regular.ttf
- chatify/web/gallery.html
- chatify/web/index.html
- chatify/web/loading.css
- chatify/web/motion.css
- chatify/web/navigation.css
- chatify/web/pipeline.js
- chatify/web/reading.js
- chatify/web/refinements.css
- chatify/web/settings.css
- chatify/web/settings.js
- chatify/web/settingsguide.js
- chatify/web/settingstabs.css
- chatify/web/settingstop.js
- chatify/web/style.css
- chatify/web/upgrade.css

## Other non-test paths

- DELIVERABLES.md
- Dockerfile
- chatify/apipicks.py
- chatify/appbuilder.py
- chatify/connectors/arxiv.py
- chatify/connectors/bounded.py
- chatify/connectors/http_json.py
- chatify/connectors/local_files.py
- chatify/connectors/open_sources.py
- chatify/connectors/pubmed.py
- chatify/connectors/web_search.py
- chatify/exports.py
- chatify/generator_design.py
- chatify/models/rerank/README.md
- chatify/models/rerank/config.json
- chatify/models/rerank/model_quint8_avx2.onnx
- chatify/models/rerank/special_tokens_map.json
- chatify/models/rerank/tokenizer.json
- chatify/models/rerank/tokenizer_config.json
- chatify/models/rerank/vocab.txt
- chatify/pipeline.py
- chatify/portable.py
- chatify/prompts.py
- chatify/providers.py
- chatify/rerank.py
- chatify/schema.py
- chatify/server.py
- chatify/stage_contracts.py
- chatify/store.py
- chatify/theme.py
- pyproject.toml
- requirements.txt
- schema/chat-app.schema.json

## Exact census

584 total paths, 30 UI paths, 521 test/evidence paths, 33 other. Full list in post-brief-paths.json.

## Settings mode mechanism

settings.html does not load theme.js. settings.js applies CCTheme only to preview iframe(line340), outer sets data-motion(line742). cc_mode is read in theme.js(line110) for chat/build. Therefore outer settings staying light is not established as a broken shared preference contract. No speculative product change.
