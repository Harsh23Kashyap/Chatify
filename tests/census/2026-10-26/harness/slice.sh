#!/bin/bash
# slice.sh FILELIST - run tests 2-lane against CHATIFY_TEST_URL, append TSV rows
cd /home/sandbox/chatify
export PLAYWRIGHT_MODULE=/home/sandbox/pw-runner/node_modules/playwright-core
export CHATIFY_TEST_URL=${CHATIFY_TEST_URL:-http://127.0.0.1:8765}
export CHATIFY_FIXTURE_YAML=${CHATIFY_FIXTURE_YAML:-/home/sandbox/chatify/tests/fixtures/builder-complete.yaml}
TSV=/home/sandbox/census/results.tsv
run_one() {
  local f=$1 t0 dur rc st
  t0=$(date +%s)
  node "tests/$f" > "/home/sandbox/census/${f%.cjs}.log" 2>&1
  rc=$?; dur=$(( $(date +%s) - t0 )); st=PASS; [ $rc -ne 0 ] && st=FAIL
  printf '%s\t%s\t%s\t%s\n' "$f" "$st" "$dur" "$(date -Iseconds)" >> $TSV
}
lane() { while read -r f; do [ -n "$f" ] && run_one "$f"; done; }
split1=$(mktemp); split2=$(mktemp)
awk 'NR%2==1' "$1" > $split1; awk 'NR%2==0' "$1" > $split2
lane < $split1 & lane < $split2 & wait
rm -f $split1 $split2
