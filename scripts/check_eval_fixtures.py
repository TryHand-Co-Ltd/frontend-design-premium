"""Check eval fixture coverage and report missing fixture paths."""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

root = Path(__file__).resolve().parents[1]
eval_root = root / 'evals'
e = json.loads((eval_root / 'evals.json').read_text(encoding='utf-8'))
cases = e.get('evals', [])
print(f'Total eval cases: {len(cases)}')
print()

no_fixtures = []
missing_fixtures = []
for c in cases:
    files = c.get('files', [])
    cid = str(c.get('id', '?'))
    cname = str(c.get('name', c.get('id', '?')))[:50]
    missing = [path for path in files if not (eval_root / path).is_file()]
    missing_fixtures.extend(f'eval #{cid}: {path}' for path in missing)
    status = '[MISSING]' if missing else ('[FILES]' if files else 'no-fixture')
    if not files:
        no_fixtures.append(cid)
    print(f'  {cid:>3}: {cname:50} {status}')

print(f'\nCases WITHOUT fixtures: {len(no_fixtures)}')
print(f'  IDs: {", ".join(no_fixtures[:10])}{"..." if len(no_fixtures) > 10 else ""}')
if missing_fixtures:
    print('\nMissing fixture paths:')
    for item in missing_fixtures:
        print(f'  {item}')
    raise SystemExit(1)
