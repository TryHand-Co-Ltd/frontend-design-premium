"""Check how many eval cases have fixture files vs empty files list."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

root = Path(__file__).resolve().parents[1]
e = json.loads((root / "evals" / "evals.json").read_text(encoding="utf-8"))
cases = e.get('evals', [])
print(f'Total eval cases: {len(cases)}')
print()

no_fixtures = []
for c in cases:
    files = c.get('files', [])
    cid = str(c.get('id', '?'))
    cname = str(c.get('name', c.get('id', '?')))[:50]
    status = '[FILES]' if files else 'no-fixture'
    if not files:
        no_fixtures.append(cid)
    print(f'  {cid:>3}: {cname:50} {status}')

print(f'\nCases WITHOUT fixtures: {len(no_fixtures)}')
print(f'  IDs: {", ".join(no_fixtures[:10])}{"..." if len(no_fixtures) > 10 else ""}')
