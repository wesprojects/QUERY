#!/bin/bash
# The whole suite (CLAUDE.md workflow step 2). One line per test file with its verdict, then a total; the script exits 1 when any file failed.
# A file fails when it exits non-zero (every test sets the exit code on a failed check, a page error or a reported problem, and a crash exits 1)
# or prints a line starting "FAIL". Each file's full output is kept in test/run_<name>.log.
export NODE_PATH="$(npm root -g)"
cd "$(dirname "$0")/.."
failed=()
for t in test ui3 ui5 ui6 ui7 ui8 ui9 ui10 ui11 ui2022 uireview guidex plan ws2 outputs wsoverlap wsstress final dims caps elevpick handle join corner capbtn overlap capdxf cap3d; do
  out=$(node test/$t.js 2>&1); code=$?; echo "$out" > test/run_$t.log
  nfail=$(echo "$out" | grep -c '^FAIL')
  summary=$(echo "$out" | grep -E 'ALL PASS|FAILURES|^TOTAL|CLEAN|PROBLEMS|GAPS|with problems|with errors|no page errors|no console errors' | tail -1)
  if [ "$code" -ne 0 ] || [ "$nfail" -gt 0 ]; then failed+=("$t"); echo "$t: FAILED (exit $code, $nfail FAIL lines) $summary"; else echo "$t: ok  $summary"; fi
done
echo
if [ ${#failed[@]} -gt 0 ]; then echo "${#failed[@]} FILE(S) FAILED: ${failed[*]}"; exit 1; fi
echo "ALL 28 FILES PASSED"
