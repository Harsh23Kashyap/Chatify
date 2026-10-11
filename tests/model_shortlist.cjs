// Run with node tests/model_shortlist.cjs. Tests the production selector directly.
const assert=require('assert'),fs=require('fs'),vm=require('vm'),path=require('path');
const src=fs.readFileSync(path.join(__dirname,'../customchat/web/settings.js'),'utf8');
const begin=src.indexOf('function modelShortlist('),end=src.indexOf('async function loadModels(',begin);
const ctx={};vm.createContext(ctx);vm.runInContext(src.slice(begin,end),ctx);
const ids=['gpt-6.1-sol','gpt-6-astra','gpt-6-luna','gpt-6-sol','gpt-5.6-sol','gpt-5-mini','gpt-5-nano','gpt-4.1','gpt-4.1-mini','gpt-4o-mini','gpt-4o-mini-tts','gpt-4o-transcribe','gpt-5-codex','gpt-5.6-terra'];
const pick=ctx.modelShortlist('openai',ids);assert.equal(pick.length,10);assert(pick.includes('gpt-4o-mini'));assert(pick.includes('gpt-5-nano'));assert(pick.every(x=>ids.includes(x)));assert(!pick.some(x=>/tts|transcribe|codex/.test(x)));
assert.equal(ctx.modelShortlist('gemini',['gemini-3.8-flash','gemini-embedding-001','gemini-tts']).length,1);
assert.equal(ctx.modelShortlist('claude',Array.from({length:30},(_,i)=>'claude-sonnet-'+i)).length,10);
assert.equal(ctx.modelShortlist('ollama',Array.from({length:30},(_,i)=>'local-'+i)).length,30);
assert.equal(ctx.modelShortlist('openai',[]).length,0);console.log('PASS shortlist bounds, known IDs, affordable generations, exclusions, empty and local lists');
