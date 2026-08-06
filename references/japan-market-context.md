# Japan Market Context

Read this when the product serves people in Japan, operates in the Japanese market, or handles Japan-specific identity, address, payment, commerce, public-service, or legal flows. This applies even when the interface language is English.

## Separate the three decisions

Do not collapse these into a single `ja-JP` switch:

- **Japanese locale:** language, formatting, collation, component locale packs, and input behavior.
- **Japan market:** local data, business conventions, trust expectations, support, payments, and regulatory obligations.
- **Japanese content and visual design:** writing register, typography, information hierarchy, density, and presentation for the target audience.

A product can require any one or all three. Record each decision and its evidence in `DESIGN.md` or `UX-CONTRACT.md` when those artifacts are in scope.

## Market gate

Before visual direction or implementation, identify:

1. **Market boundary:** Japan-only, Japan-first, or global with Japan support.
2. **Audience:** native Japanese users, foreign residents, bilingual teams, older adults, children, or a mixed audience.
3. **Domain and risk:** consumer, B2B/admin, government, finance, healthcare, commerce, education, or another regulated domain.
4. **Usage scene:** smartphone consumer flow, desktop operations, kiosk, assisted service, or specialist device.
5. **Decision stakes:** frequency, urgency, information density, trust, reversibility, and legal consequences.
6. **Evidence:** target-user research, domain contracts, comparable Japanese products, official systems, and authoritative regulation.

If the audience or domain is materially ambiguous, ask only the question that changes the contract. Do not infer “Japanese users” from language alone.

## Evidence precedence

Use this order when sources disagree:

1. Research with the actual target users and maintained product/business contracts.
2. Authoritative Japanese law, regulator guidance, and domain policy.
3. Established conventions in comparable Japanese products serving the same audience and task.
4. Official Japanese design systems and accessibility guidance.
5. This skill and upstream visual defaults.

An official design system is a baseline, not a universal Japan theme. Preserve the product's own information architecture and style guide when evidence supports it.

## Register interaction

- A Japan-targeted marketing or content page still loads `japanese-content-design.md` and `japanese-visual-layout.md` when Japanese-facing. It does not inherit application-only CRUD, async, or UX-CONTRACT requirements merely because it targets Japan.
- A Japan-market product with an English UI still loads this file and any relevant data or regulated-flow contracts.
- For Japanese-facing product UI, upstream English-specific defaults such as sentence case, mandatory active voice, terse non-apologetic errors, or aesthetic risk are advisory only. Target-user comprehension, domain trust, natural Japanese, and task evidence take precedence.
- Distinctiveness must come from the product and audience, not cultural decoration.

## Anti-stereotype guardrail

Never equate Japan-native UX with sakura, a red sun, washi texture, brush fonts, anime, “Zen” minimalism, or universally dense screens. Never add those cues without product evidence. Density is a task decision: comparison-heavy B2B work may be compact; consumer, public-service, and older-adult flows often need more guidance and space.

## Exit evidence

Japan-market framing is complete only when the market, audience, domain, device context, language policy, evidence sources, and unresolved high-risk decisions are explicit. If regulated or legal behavior lacks an authoritative source, load `japan-regulated-flows.md` and escalate rather than inventing policy.
