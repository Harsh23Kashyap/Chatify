const BASE=process.env.CHATIFY_TEST_URL||'http://127.0.0.1:8145',OUT=process.env.CHATIFY_TEST_OUTPUT||'/tmp';
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('assert'),fs=require('fs'),{execSync}=require('child_process');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});const p=await b.newPage({viewport:{width:1440,height:1000},acceptDownloads:true});p.setDefaultTimeout(8000);await p.addInitScript(()=>localStorage.setItem('cc_tour','1'));await p.goto(BASE+'/');await p.locator('#list .item').filter({hasText:'Hindi export fixture'}).click();
// Turn 1 (Hindi): Markdown keeps full Unicode.
await p.getByText('More',{exact:true}).nth(0).click();
let wait=p.waitForEvent('download');await p.getByRole('button',{name:'Markdown',exact:true}).nth(0).click();await (await wait).saveAs(OUT+'/cc-hindi-answer.md');assert(fs.readFileSync(OUT+'/cc-hindi-answer.md','utf8').includes('स्रोत के अनुसार नमस्ते'),'Markdown keeps the Hindi answer');
// Turn 1 (Hindi): PDF now renders Devanagari through the bundled Noto fonts - real download, real glyphs.
wait=p.waitForEvent('download');await p.getByRole('button',{name:'PDF',exact:true}).nth(0).click();await (await wait).saveAs(OUT+'/cc-hindi-answer.pdf');
const pdf=fs.readFileSync(OUT+'/cc-hindi-answer.pdf');assert(pdf.slice(0,5).toString()==='%PDF-','valid PDF header');assert(pdf.length>10000,'embedded-font PDF is substantial');
const text=execSync('pdftotext '+JSON.stringify(OUT+'/cc-hindi-answer.pdf')+' -').toString();assert(text.includes('स्रोत के अनुसार नमस्ते'),'PDF text layer carries the Hindi answer');
execSync('pdftoppm -png -r 80 -f 1 -l 1 '+JSON.stringify(OUT+'/cc-hindi-answer.pdf')+' '+JSON.stringify(OUT+'/cc-hindi-answer'));
assert(fs.existsSync(OUT+'/cc-hindi-answer-1.png'),'rendered PDF page evidence');
// Turn 2 (CJK): outside the bundled font coverage - honest rejection toast, no download.
await p.getByText('More',{exact:true}).nth(1).click();
let downloaded=false;p.on('download',()=>{downloaded=true});
await p.getByRole('button',{name:'PDF',exact:true}).nth(1).click();
await p.locator('.toast').first().waitFor();assert((await p.locator('.toast').last().textContent()).includes('Download Markdown for full Unicode'),'unsupported script keeps the honest rejection');
await p.waitForTimeout(400);assert.equal(downloaded,false,'rejection downloads nothing');
console.log('PDF toast:',await p.locator('.toast').last().textContent());
await p.screenshot({path:OUT+'/cc-unicode-pdf-error.png'});
fs.writeFileSync(OUT+'/cc-unicode-export.json',JSON.stringify([{case:'Hindi Markdown download preserves text',status:'PASS',mode:'ACTUAL fixture UI download'},{case:'Hindi PDF renders bundled Devanagari',status:'PASS_REPAIR',detail:'valid %PDF, '+pdf.length+' bytes, pdftotext finds the answer, rendered page saved',mode:'ACTUAL fixture UI download + pdftotext + pdftoppm'},{case:'CJK PDF honest rejection toast',status:'PASS_REPAIR',detail:await p.locator('.toast').last().textContent(),mode:'ACTUAL fixture UI'}],null,2));await b.close();console.log('PASS hindi markdown+pdf glyphs/cjk rejection toast no download')})().catch(e=>{console.error(e);process.exit(1)});
