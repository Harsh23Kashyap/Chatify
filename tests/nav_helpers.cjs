/* Shared settings-navigation helpers for the current product contract:
   settings opens on the Build with AI hero (cfgtop-builder), manual nav lives
   behind CCSettingsTop 'manual', advanced-only sections need #cfgmode advanced,
   and #menu shows one group's links at a time behind .category-tabs. */
async function ensureManualAdvanced(p){
  await p.waitForFunction(()=>!!window.CCSettingsTop);
  await p.evaluate(()=>window.CCSettingsTop.set('manual'));
  await p.waitForTimeout(150);
  if(await p.evaluate(()=>document.body.classList.contains('simple'))){
    await p.locator('#cfgmode [data-m=advanced]').click();
    await p.waitForTimeout(300);
  }
}
async function openSettingsSection(p,group,hash){
  await ensureManualAdvanced(p);
  await p.locator('.category-tabs button[data-group="'+group+'"]').click();
  await p.waitForTimeout(150);
  await p.locator('#menu a[href="'+hash+'"]').click();
  await p.waitForTimeout(150);
}
module.exports={ensureManualAdvanced,openSettingsSection};
/* CCDialog replaced native confirm() (8a586fd): click-triggered confirms must
   open dialog.cc-cdlg and press its labelled button; native dialog handlers
   never fire. beforeunload dialogs remain native and are NOT covered here. */
async function confirmCCDialog(p,okText){
  const dlg=p.locator('dialog.cc-cdlg[open]');
  await dlg.waitFor();
  await dlg.getByRole('button',{name:okText,exact:true}).click();
  await dlg.waitFor({state:'detached'}).catch(()=>{});
}
async function dismissCCDialog(p){
  const dlg=p.locator('dialog.cc-cdlg[open]');
  await dlg.waitFor();
  const text=await dlg.innerText();
  await dlg.locator('.cc-cdlg-cancel').click();
  return text;
}
async function promptCCDialog(p,value,okText){
  const dlg=p.locator('dialog.cc-cdlg[open]');
  await dlg.waitFor();
  await dlg.locator('.cc-cdlg-input').fill(value);
  await dlg.getByRole('button',{name:okText,exact:true}).click();
  await dlg.waitFor({state:'detached'}).catch(()=>{});
}
module.exports={ensureManualAdvanced,openSettingsSection,confirmCCDialog,dismissCCDialog,promptCCDialog};

/* A retained-draft fixture must exist in the real owner-scoped store too.
   Mocking only GET used to make the following real review correctly fail
   with "Draft not found". Seed through the public draft endpoint using the
   route request's owner cookie, and return the server's canonical record. */
async function fulfillRetainedFixture(route,record){
  const url=new URL(route.request().url());
  const id=url.searchParams.get('id');
  const headers={...route.request().headers(),'content-type':'application/json'};
  delete headers['content-length'];
  const response=await route.fetch({url:url.origin+'/api/settings/build/draft',method:'POST',headers,postData:JSON.stringify({...record,id})});
  if(!response.ok())throw Error('Could not retain synthetic fixture: '+response.status()+' '+await response.text());
  await route.fulfill({response});
}
module.exports.fulfillRetainedFixture=fulfillRetainedFixture;

/* The manual editor now selects steps from a native details picker. Use
   native clicks so keyboard/focus assertions still exercise the live UI. */
async function openPromptPicker(p){
  const picker=p.locator('#sec-prompts .manual-step-picker');
  await picker.waitFor({state:'attached'});
  if(!await picker.evaluate(n=>n.open))await picker.locator(':scope>summary').click();
}
async function choosePromptStep(p,choice){
  await openPromptPicker(p);
  await choice.click();
}
module.exports.openPromptPicker=openPromptPicker;
module.exports.choosePromptStep=choosePromptStep;

/* Completed job fixtures stand in for BuildJobs, which retains completed
   drafts before the UI requests owner-scoped review. Keep that side of the
   fixture contract real rather than stubbing review or weakening ownership. */
async function fulfillCompletedFixture(route,data){
  if(data.state==='done'&&data.yaml){
    const url=new URL(route.request().url());
    const headers={...route.request().headers(),'content-type':'application/json'};
    delete headers['content-length'];
    const saved=await route.fetch({url:url.origin+'/api/settings/build/draft',method:'POST',headers,postData:JSON.stringify({id:data.id,yaml:data.yaml})});
    if(!saved.ok())throw Error('Could not retain completed synthetic job: '+saved.status()+' '+await saved.text());
  }
  await route.fulfill({json:data});
}
module.exports.fulfillCompletedFixture=fulfillCompletedFixture;
