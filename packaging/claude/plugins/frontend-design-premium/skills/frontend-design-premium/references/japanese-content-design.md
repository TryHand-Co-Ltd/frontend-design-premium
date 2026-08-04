# Japanese Content Design

Read this for any Japanese-facing surface, including marketing pages. Natural Japanese content is a product contract, not the final translation pass.

## Voice and register

- Choose one writing register per surface: `です・ます調`, `である調`, or a concise UI register. Record intentional changes between brand, help, legal, and product copy.
- Do not translate English sentence structure literally. Japanese may omit subjects, foreground context, or use a different information order.
- Do not apply “active voice” mechanically. Prefer the form that makes the actor, outcome, and responsibility clear for the domain.
- Use domain-appropriate nouns consistently: `ユーザー`, `利用者`, `お客様`, `会員`, and `管理者` are not interchangeable.
- Create a glossary and banned-term list when multiple screens, writers, or regulated terms are involved.
- Use `やさしい日本語` only when the audience requires it, especially public services and foreign-resident support; validate it with representative users.

## Script, punctuation, and terminology

- Define preferred Kanji, hiragana, katakana, loanwords, numerals, units, full-width punctuation, brackets, `・`, and `〜` usage in the product style guide.
- Avoid mixed spellings for the same action or concept. Component-library copy, help, notifications, email, and accessibility labels use the same glossary.
- Do not concatenate translated fragments. Write complete messages with placeholders so particles and word order remain natural.
- Avoid unexplained abbreviations and English leakage. Keep unavoidable technical identifiers visually and semantically distinct.

## Actions and guidance

- Buttons state the result: `保存する`, `登録する`, `内容を確認する`, `注文を確定する`, or the established concise equivalent. Do not default to `OK`.
- Distinguish review from commitment. `内容を確認する` must not perform the final purchase or irreversible submission.
- Labels remain visible; placeholders provide examples, not field names or required-state instructions.
- Required and optional markers follow one documented system. For Japanese public-service and form-heavy contexts, prefer explicit `必須` / `任意` guidance over a lone Western-style asterisk unless established evidence says otherwise.

## Errors, empty states, and confirmation

- Errors identify what happened, where possible, and how to recover. Do not expose raw schemas, codes, or untranslated library messages.
- Avoid both extremes: cold machine fragments and long ritual apologies. Use an apology only when it serves the relationship, severity, and product voice.
- Preserve entered values and point to the first invalid field. Summary and inline messages must agree.
- Empty and no-result states explain whether there is no data, no match, missing permission, or a load failure; do not use one generic sentence for all four.
- Confirmation copy names the object, consequence, ability to revise, and exact committing action.

## Review gate

Critical Japanese copy requires review by a native Japanese reviewer with relevant domain context. The gate applies to purchase/contract commitment, identity and consent, privacy, billing, destructive actions, public-service guidance, safety, and high-traffic acquisition copy. Machine translation, linting, and the presence of Japanese characters do not satisfy this gate.

Verify copy in rendered context with long organization names, mixed scripts, narrow screens, accessible names, validation timing, and real interaction states. Record who reviewed critical copy or report the review as an unresolved release risk.
