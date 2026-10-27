# Stop model calls on ordinary starter loads

Hosted smoke verification after deploying ea81165 found changed starter text without an intentional question. Source showed that app.js automatically POSTs /api/suggestions, whose cold-cache path called provider.complete. Read-only app budget showed model=1 and no question usage on October 27; the wrapper increments before dispatch, so this is one metered model attempt, not proof of billing or exact causation. No verified dollar meter exists. No secrets recorded, intentional questions/build calls or settings changes made.

The local guard serves configured examples or deterministic fallback only, without consulting old generated caches, invoking inference or consuming model quota. It keeps private recent questions owner-scoped and temporary-chat history empty. This intentionally removes automatic model-generated starters; configured starters remain usable.

The new no-inference regression contract fails on pre-fix code (one explicit fail, two errors including the HTTP boundary). Fixed suggestions suite: 8 passed. Budget suite: 10 passed. These are local no-network provider doubles, not provider qualification. A separate system-Python core run had 77 tests, two failures and one error all at PDF export because its documents extra was absent; that run is not green and is not claimed as regression proof. Existing installed-documents evidence is separate.

No guarded-code commit, push, CI run or redeploy is claimed by this result. Current hosted deployment remains ea81165 and retains the automatic starter-generation path until an authorized follow-up deployment. Prior failures are retained.

Follow-up using the already-qualified Python 3.12 documents environment: all 77 core checks passed; all 8 starter checks passed there too. System-Python missing-extra output remains preserved in core-system-missing-extra.log. The ordinary push workflow, not these targeted checks, owns later complete offline CI status.
