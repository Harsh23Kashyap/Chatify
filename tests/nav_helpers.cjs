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
