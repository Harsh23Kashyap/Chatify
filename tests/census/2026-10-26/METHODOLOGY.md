# Census counting methodology (versioned correction, 2026-10-26 12:09 IST)

Authoritative progress metric: DISTINCT manifest file keys with a current
qualified status (latest row per key in results.tsv), never appended row
counts. Appended rows include reruns and supersession rows and overcount
progress.

Correction history (preserved, not rewritten):
- 11:45 report stated "236 PASS-latest, awk-reconciled exact". A distinct-key
  recount at 12:07 showed 218 distinct tested keys at that time; the 236 figure
  was an overcount and intermediate deltas derived from it are unreliable.
- 12:07 verified current state three independent ways: 275 distinct tested
  (all PASS-latest, 0 FAIL-latest), 194 queued, zero queue/result overlap,
  275+194 = 469 exactly. This is the accepted baseline going forward.
- Deltas computed from earlier reported counts are not reliable; future
  progress states are always current audited distinct-key counts.

Qualification caveat carried with every report: three flake fixes
(deployment_long_configuration_geometry 091aaa9, appearance_navigation
fixture-pollution harness fix, builder fontstress 8b6f43a) remain
FIXED-PENDING-FULLPASS until a stable full rerun after census completion.
Census coverage 0 FAIL-latest is NOT a 0-fails-clean release claim.
