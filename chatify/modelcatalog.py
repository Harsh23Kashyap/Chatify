"""Small documented examples, never evidence of account or server availability."""
CHECKED = '2026-10-14'
CATALOG = {
 'openai': [('gpt-4.1-mini','Smaller GPT-4.1 model for instruction following and tool use.','https://developers.openai.com/api/docs/models/gpt-4.1-mini')],
 'claude': [('claude-haiku-5-5','For latency-sensitive extraction and classification.','https://platform.claude.com/docs/en/models/overview')],
 'gemini': [('gemini-3.5-flash-lite','Low-latency model for document parsing and simple extraction.','https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite')],
 'deepseek': [('deepseek-flash','Current Flash model with text and visual understanding.','https://api-docs.deepseek.com/updates')],
 'groq': [('openai/gpt-oss-20b','Smaller hosted GPT OSS model.','https://console.groq.com/docs/models')],
 'mistral': [('mistral-small-2603','Hybrid instruction, reasoning and coding model.','https://docs.mistral.ai/models/mistral-small-4-0-26-03')],
 'minimax': [('MiniMax-M2.7','Text model for coding and agent tasks.','https://platform.minimax.io/docs/faq/models')],
 'mimo': [('mimo-v2.6-flash','Flash model listed in the provider catalog.','https://mimo.mi.com/docs/en-US/api/model/list-models')],
 'openrouter': [('meta-llama/llama-3.3-70b-instruct','Multilingual text model for dialogue.','https://openrouter.ai/meta-llama/llama-3.3-70b-instruct')],
 'ollama': [('llama3.2','Small local text model. Download separately before using.','https://ollama.com/library/llama3.2')],
 'openai_compatible': [('llama3.2','Example only. Your server must expose this exact name.','https://ollama.com/library/llama3.2')],
 'mock': [('demo','Offline built-in answers; no model request.','')],
}
CATALOG['claude'] += [('claude-opus-5-5', 'General-purpose Opus model.', 'https://platform.claude.com/docs/en/models/overview'), ('claude-sonnet-5-5', 'Balanced Sonnet model.', 'https://platform.claude.com/docs/en/models/overview'), ('claude-fable-5-1', 'Reasoning model.', 'https://platform.claude.com/docs/en/models/overview')]
CATALOG['gemini'] += [('gemini-3.8-flash', 'Flash text model.', 'https://ai.google.dev/gemini-api/docs/models'), ('gemini-3.6-flash', 'Flash text model.', 'https://ai.google.dev/gemini-api/docs/models'), ('gemini-3.1-pro-preview', 'Pro preview model.', 'https://ai.google.dev/gemini-api/docs/models'), ('gemini-2.5-flash', 'Flash model.', 'https://ai.google.dev/gemini-api/docs/models'), ('gemini-2.5-pro', 'Pro model.', 'https://ai.google.dev/gemini-api/docs/models')]
CATALOG['deepseek'] += [('deepseek-v4-pro', 'Pro text model.', 'https://api-docs.deepseek.com/quick_start/pricing')]
CATALOG['groq'] += [('openai/gpt-oss-120b', 'Larger GPT OSS model.', 'https://console.groq.com/docs/models'), ('llama-3.1-8b-instant', 'Smaller Llama model; access depends on your account.', 'https://console.groq.com/docs/models'), ('llama-3.3-70b-versatile', 'Larger Llama model; access depends on your account.', 'https://console.groq.com/docs/models')]
CATALOG['mistral'] += [('mistral-large-4', 'Large 4 public preview.', 'https://docs.mistral.ai/resources/changelogs'), ('mistral-large-2512', 'Large 3 model.', 'https://docs.mistral.ai/resources/changelogs'), ('ministral-3b-2512', 'Smaller Ministral 3 model.', 'https://docs.mistral.ai/resources/changelogs'), ('ministral-8b-2512', 'Ministral 3 model.', 'https://docs.mistral.ai/resources/changelogs'), ('ministral-14b-2512', 'Larger Ministral 3 model.', 'https://docs.mistral.ai/resources/changelogs')]
CATALOG['minimax'] += [('MiniMax-M3.1-Flash-Preview', 'Flash preview model.', 'https://platform.minimax.io/docs/faq/models'), ('MiniMax-M3', 'Multimodal coding model.', 'https://platform.minimax.io/docs/faq/models'), ('MiniMax-M2.7-highspeed', 'Faster M2.7 inference.', 'https://platform.minimax.io/docs/faq/models'), ('MiniMax-M2.5', 'Coding model.', 'https://platform.minimax.io/docs/faq/models'), ('MiniMax-M2.5-highspeed', 'Faster M2.5 inference.', 'https://platform.minimax.io/docs/faq/models')]
CATALOG['mimo'] += [('mimo-v2.6-pro', 'Pro model.', 'https://mimo.mi.com/docs/en-US/api/model/list-models'), ('mimo-v2.6-pro-ultraspeed', 'Faster Pro model.', 'https://mimo.mi.com/docs/en-US/api/model/list-models'), ('mimo-v2.5', 'Earlier text model.', 'https://mimo.mi.com/docs/en-US/api/model/list-models'), ('mimo-v2.5-pro', 'Earlier Pro model.', 'https://mimo.mi.com/docs/en-US/api/model/list-models')]
CATALOG['openrouter'] += [('openai/gpt-oss-20b', 'GPT OSS text model.', 'https://openrouter.ai/openai/gpt-oss-20b')]
CATALOG['ollama'] += [('qwen3', 'Local Qwen model. Download separately before using.', 'https://ollama.com/library'), ('gemma3', 'Local Gemma model. Download separately before using.', 'https://ollama.com/library'), ('llama3.1', 'Local Llama model. Download separately before using.', 'https://ollama.com/library')]
CATALOG['openai_compatible'] += [('qwen3', 'Example only. Your server must expose this exact name.', 'https://ollama.com/library'), ('gemma3', 'Example only. Your server must expose this exact name.', 'https://ollama.com/library')]
def suggestions(kind):
 return [{'id':name,'description':description,'source':source,'checked':CHECKED} for name,description,source in CATALOG.get(kind,[])]
