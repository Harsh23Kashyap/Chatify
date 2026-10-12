"""Small documented examples, never evidence of account or server availability."""
CHECKED = '2026-10-12'
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
def suggestions(kind):
 return [{'id':name,'description':description,'source':source,'checked':CHECKED} for name,description,source in CATALOG.get(kind,[])]
