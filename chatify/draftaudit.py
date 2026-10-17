"""Small deterministic draft observations, not a security verifier or sandbox."""
import ast,re
from urllib.parse import urlsplit

def findings(raw):
 notes=[]
 for kind,draft in raw.get('helper_drafts',{}).items():
  try:tree=ast.parse(draft.get('code',''))
  except (SyntaxError,TypeError):continue
  destinations=set()
  for node in ast.walk(tree):
   if isinstance(node,ast.Constant) and isinstance(node.value,str):
    for url in re.findall(r'https?://[^\s\"\'<>]+',node.value):
     host=urlsplit(url).hostname
     if host:destinations.add(host)
  if destinations:notes.append('Helper '+kind+' contains literal destinations: '+', '.join(sorted(destinations))+'. Not verified or authorized by this inventory. Review every request destination before running; dynamically built destinations may be missed.')
 answer=raw.get('pipeline_prompts',{}).get('text',{}).get('answer','')
 if re.search(r'\b(?:ignore|disregard|bypass)\s+(?:the\s+)?(?:retrieved\s+|provided\s+|numbered\s+)?(?:passages|evidence|sources)\b',answer,re.I):
  notes.append('Answer prompt contains literal source-bypass wording. This is a text occurrence, not evidence that the instruction is unsafe: quoted examples and negated instructions can match. Review its context yourself. This check misses paraphrased attacks and does not check citation rules; it is not safety verification.')
 return notes
