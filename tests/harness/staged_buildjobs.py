"""Qualification-only safe stage batches. Never imported by the application.

Before make_handler/run, explicitly replace chatify.buildjobs.BuildJobs with
staged_class(batch_size=1). Each start/resume performs at most batch_size real
parts and stops with state=partial, harness_paused=True and no active calls.
Restart with the SAME spend_dir, owner, brief, config and confirmed_sources to
resume retained parts. Do not call product Retry on a harness pause. In one
process use resume_batch(owner,id). Once all parts exist, the next batch runs
normal merge/final-review only. This is staged acceptance, not uninterrupted UI.
All provider calls remain real and all normal validators remain unchanged.
The outer runner must wait for harness_paused or terminal state before exit;
this helper does not cancel/kill a slow call or promise it finishes in120s.
"""
import copy,threading
from chatify.buildjobs import BuildJobs as ProductBuildJobs,PARTS

def staged_class(batch_size=1):
 if type(batch_size) is not int or not 1<=batch_size<=3:raise ValueError('batch_size must be1-3')
 class StagedBuildJobs(ProductBuildJobs):
  def _run(self,job,parts):
   # A batch stops accepting work before it starts. No queued future can
   # begin after the advertised boundary and no active call is abandoned.
   todo=[(k,s) for k,s in parts if k not in job['parts']]
   ready=[(k,s) for k,s in todo if not k.startswith('helper:') or 'api' in job['parts']]
   if not todo:
    job['harness_paused']=False
    return super()._run(job,[])
   for key,spec in ready[:batch_size]:
    try:self._part(job,key,spec);job['errors'].pop(key,None)
    except Exception as exc:job['errors'][key]=str(exc)[:400]
    self._checkpoint(job)
   with self.lock:
    job['state']='partial';job['harness_paused']=True
    job['phase']='Qualification harness paused at a drained stage boundary'
    job['in_retry']=False
    self._checkpoint(job)
  def view(self,owner,ident):
   out=super().view(owner,ident)
   with self.lock:
    job=self._owned(owner,ident);out['harness_paused']=job.get('harness_paused',False);out['active_calls']=len(job.get('active',set()))
   return out
  def resume_batch(self,owner,ident):
   with self.lock:
    job=self._owned(owner,ident)
    if not job.get('harness_paused') or job.get('active'):raise ValueError('Wait for a drained harness pause')
    # Never product Retry, local defaults, cancel or clear a checkpoint.
    job['state']='running';job['harness_paused']=False;job['cancel']=False
    parts=[(k,s) for k,s in PARTS if k not in job['parts']]
   threading.Thread(target=self._run,args=(job,parts),daemon=True).start()
   return self.view(owner,ident)
 return StagedBuildJobs
