# E2E Audit Prompt

Reusable prompt for running a static contract audit of any frontend project against `frontend-design-premium` (v1.0+).

## Usage

Copy the block below, replace `TARGET_PROJECTS` with the actual paths, and give to any agent using the skill.

---

```text
Bạn là agent dùng skill `frontend-design-premium` (v1.0) + upstream `frontend-design`.
NHIỆM VỤ: audit-only trên project thật — KHÔNG edit, KHÔNG commit, KHÔNG refactor.

Targets (Windows):
1) D:/Workspace/project-a
2) D:/Workspace/project-b

Cho MỖI project:
A. Register gate: product/admin vs marketing (tách route group nếu mixed).
B. Đọc DESIGN.md / UX-CONTRACT.md nếu có; chạy:
   npx -p @google/design.md designmd lint <DESIGN.md> (nếu có)
C. Grep anti-patterns (exclude node_modules/.next/dist/tests khi hợp lý):
   - (?:window\.)?(?:alert|confirm|prompt)\s*\(
   - reportValidity
   - clickable div/span onClick (không role)
   - password without reveal (type="password" mà không show/hide toggle)
   - form without noValidate
   - search debounce / clear X / isComposing (IME-safe)
   - scrollbar custom + scrollbar-gutter
   - prefers-reduced-motion
   - table/list paging strategy (paginate vs load-more vs infinite)
   - document.title / 404 / 403
D. So với case study gốc: table paging, hover+cursor pointer, custom scrollbar, no native dialogs.
E. Ghi rõ: (1) bug của app, (2) gap của skill, (3) false positive.

OUTPUT (một report):
- Scorecard 5 project
- P0/P1/P2 findings kèm path:line
- Skill gaps đề xuất (không implement)
- Kết luận: skill sẵn sàng dogfood? blocker còn lại?
```
