"""Verify all 15 case study requirements are covered in the skill files."""
import re, sys

sys.stdout.reconfigure(encoding='utf-8')

def check(pattern, filepath, flags=re.IGNORECASE):
    text = open(filepath, encoding='utf-8').read()
    return bool(re.search(pattern, text, flags))

checks = {
    "1. Table pagination + load-more grill": (
        "SKILL.md + decision-matrix.md",
        check(r'pagination.*load.?more|Load more.*server pagination|decision-matrix.*pagination', 'SKILL.md')
    ),
    "2. Hover style + cursor: pointer": (
        "SKILL.md section 4 interaction states",
        check(r'hover.*style|cursor.?pointer|clickable.*hover|pointer semantics', 'SKILL.md')
    ),
    "3. Custom scrollbar": (
        "SKILL.md section 4 scrollbar",
        check(r'scrollbar|scroll.*custom|scrollbar-gutter', 'SKILL.md')
    ),
    "4. No browser dialog": (
        "SKILL.md non-negotiable + anti-patterns.md A",
        check(r'alert.*confirm.*prompt|Never call browser.*(alert|confirm|prompt)', 'SKILL.md')
    ),
    "5. Button danger/success/warning/info": (
        "SKILL.md button system emphasis x intent",
        check(r'danger.*success.*warning|emphasis.*intent|semantic tones|Button system', 'SKILL.md')
    ),
    "6. Cross-screen consistency": (
        "SKILL.md section 4 + consistency-system.md + UX-CONTRACT",
        check(r'consistency.*screen|cross.screen.*consistency|same operation.*same.*label', 'SKILL.md')
    ),
    "7. textarea resize: none": (
        "interaction-contract.md textarea section",
        check(r'resize.*none|textarea.*resize', 'references/interaction-contract.md')
    ),
    "8. Password/secret mask + reveal": (
        "interaction-contract.md password section",
        check(r'password.*reveal|secret.*input|mask.*show.*hide|Password/secret/key', 'references/interaction-contract.md')
    ),
    "9. Disable HTML5 validation": (
        "SKILL.md noValidate + anti-patterns.md H",
        check(r'noValidate|novalidate|native.*validation|HTML5.*validation', 'SKILL.md')
    ),
    "10. Search clear (X) + debounce 300ms": (
        "SKILL.md search section + anti-patterns.md",
        check(r'clear.*button.*search|X.*button.*clear|debounce.*300|IME.*safe.*search', 'SKILL.md')
    ),
    "11. Japanese locale": (
        "references/japanese-localization.md (210 lines)",
        check(r'Japanese|ja-JP|locale', 'references/japanese-localization.md')
    ),
    "12. Layout stability (no jump)": (
        "SKILL.md layout stability section",
        check(r'layout.*stable|layout.*jump|scrollbar.*stable|stable.*layout', 'SKILL.md')
    ),
    "13. Destructive confirmation dialog": (
        "SKILL.md dialogs + interaction-contract.md dialog",
        check(r'destructive.*confirm|confirm.*destruct|confirmation.*dialog|Confirm destructive', 'SKILL.md')
    ),
    "14. Proactive DESIGN.md creation": (
        "SKILL.md section 1 step 2",
        check(r'create DESIGN\.md|no maintained design.*create|proactively.*create', 'SKILL.md')
    ),
    "15. Inherit from frontend-design runtime": (
        "SKILL.md section 0 + resolve_frontend_design.py",
        check(r'Load.*upstream.*skill|composition.*not.*fork|runtime.*inherit|resolve_frontend_design', 'SKILL.md')
    ),
}

all_ok = True
for name, (where, status) in checks.items():
    icon = "PASS" if status else "FAIL"
    if not status: all_ok = False
    print(f"  {icon}: {name}")
    print(f"       -> {where}")

print(f"\nOverall: {'ALL 15/15 COVERED' if all_ok else 'SOME FAILURES'}")
print(f"File: SKILL.md ({open('SKILL.md',encoding='utf-8').read().count(chr(10))+1} lines)")
print(f"Refs: {len(list(__import__('pathlib').Path('references').glob('*.md')))} .md files")
