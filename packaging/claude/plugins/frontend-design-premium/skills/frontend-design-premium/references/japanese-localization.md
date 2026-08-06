# Japanese Localization Contract

Read this when the product locale is Japanese or when changing Japanese input, dates, calendars, search, validation, numbers, currency, addresses, names, or component-library locale providers. For audience, content, visual, or regulated decisions, also load the corresponding Japan references routed from `SKILL.md §0b`.

## Locale foundation

- Set the document/app language to `ja` and use the library's complete Japanese locale pack.
- Use `ja-JP` for locale-aware formatting and collation.
- Make timezone a domain decision. Use `Asia/Tokyo` for Japan-local business time, but preserve/label source timezone for global or audited timestamps.
- Japanese UI does not imply imperial-era dates. Gregorian is the normal technical default; choose `ja-JP-u-ca-japanese` or `{ calendar: "japanese" }` only when requirements call for era notation.
- Centralize `Intl.DateTimeFormat`, `Intl.NumberFormat`, `Intl.Collator`, and `Intl.RelativeTimeFormat` instances rather than formatting ad hoc in components.

## Required-field markers

- Decide one marker and use it everywhere. Common choices:
  - `（必須）` — explicit Japanese label suffix.
  - `必須` — compact badge/chip next to the label.
  - Red `*` (asterisk) — compact, but may be less scannable for Japanese users; pair with a legend at the top of the form.
- Do **not** mix markers across forms. If one screen uses `（必須）`, every form in the app must use `（必須）`.
- Place the marker after the label text, not before.
- Optional fields should not have a marker. If ambiguity exists, add `（任意）` or `（オプション）` rather than removing all guidance.

## Dates and calendars

- Follow the product's explicit date format. `YYYY/MM/DD` is common in Japanese products, but storage and parsing must never depend on a display string. Store as ISO 8601 (`YYYY-MM-DD`) or a typed `Date` object.
- Keep display format separate from storage format. The backend and database use a fixed canonical format; the frontend formats via `Intl.DateTimeFormat` or the chosen date library.
- Localize month/day labels, navigation buttons, today/clear/apply/cancel labels, input hints, and screen-reader announcements.
- Use a calendar/date-picker with keyboard support, visible focus, selected/today distinction, and focus restoration.
- Confirm the first day of week and holiday/business-day requirements from the chosen date library/product contract; do not assume from language alone.
- Distinguish date-only values from instants. A birthday or business date must not shift because of timezone conversion.
- Make time zone visible where ambiguity affects decisions or audit trails.
- Confirm whether the domain uses calendar year or fiscal year (`年度`), and define the fiscal-year boundary from the business contract.
- Confirm weekday, national-holiday, company-holiday, and business-day behavior from a maintained source; locale alone does not establish operational calendars.

### Preset date-range labels

When offering quick-select ranges in filters or reports, use natural Japanese:

| English | Japanese |
|---------|----------|
| Today | `今日` |
| This week | `今週` |
| This month | `今月` |
| This quarter | `今四半期` |
| This year | `今年` |
| Last 7 days | `過去7日間` |
| Last 30 days | `過去30日間` |
| Custom range | `期間指定` |

Use consistent labels across all filters and reports. Do not mix `今日` in one filter and `本日` in another.

## Japanese IME and interactive input

- Track `compositionstart`, `compositionend`, and `InputEvent.isComposing` for every interaction that reacts while typing—not only search.
- Do not submit, execute a keyboard shortcut, autosave, validate, advance a wizard, select a combobox option, update a character counter, or dispatch remote work while composition is active when that action would consume incomplete text.
- Dispatch the final value after composition ends, then apply the normal debounce/validation policy exactly once.
- Do not bind Enter to submit/search or close a command palette while it is committing IME composition. Avoid shortcut detection based only on `keyCode === 229`; use composition state and actual event semantics.
- Character limits are defined in user-perceived characters or the domain's explicit storage unit. Do not assume JavaScript UTF-16 `.length` matches the requirement.
- Autocomplete and combobox results must not replace the composing text, steal selection, or announce stale suggestions.
- Cancel stale requests and ensure older responses cannot replace newer Japanese queries.
- Decide normalization (full-/half-width, hiragana/katakana, case, diacritics, punctuation, and whitespace) with the backend/domain owner. Never silently normalize only the client if it changes matching, identity, or stored-value semantics.

## Numbers, money, names, and addresses

### Currency

- Format JPY with `Intl.NumberFormat("ja-JP", { style: "currency", currency: "JPY" })`. Do not hardcode `¥` placement or decimal rules.
- **JPY has no decimal places.** Never show `.00` or `¥1,000.00`. The correct display is `¥1,000` or `￥1,000`.
- For non-JPY currencies (USD, EUR), always show the appropriate decimal places and currency symbol. Do not strip decimals from non-JPY currencies because the primary locale is Japanese.
- Tax-inclusive/exclusive display, consumption-tax labels, rounding, invoices, and receipts come from the commerce/accounting contract—not from `ja-JP` formatting. Load `japan-regulated-flows.md` when those decisions affect a regulated flow.

### Phone numbers

- Japanese landline and mobile numbers have multiple valid lengths and groupings; IP phones and international numbers add more. Prefer a proven phone parser or a domain-supplied validation contract over one hardcoded regex.
- Accept common full- and half-width entry, present the normalized value for review when needed, and store the canonical representation defined by the domain contract. Do not silently change an identity/contact value without a documented rule.
- Decide national versus E.164 storage separately from display. Do not reject `+81` or non-Japanese numbers when foreign residents, international contacts, or global accounts are in scope.

### Postal codes

- Domestic Japanese postal code format is `XXX-XXXX` (3 digits + hyphen + 4 digits), for example `100-0001`; provide a separate international-address path when the audience requires it.
- Accept and store in half-width. Validate the pattern but do not assume you can look up the address from the code.
- If address auto-fill from postal code is a product goal, integrate a third-party address lookup API (e.g., 郵便番号検索 API). Do not build your own lookup.

### Names

- Do not force Western first-name/last-name ordering. For Japanese personal names, separate family name (`姓`) and given name (`名`) in that visual order when the domain requires split fields.
- Preserve a path for Latin-script names, mononyms, middle names, legal names, and preferred display names when foreign residents or global identities are in scope. Do not coerce all people into a two-field Kanji model.
- Use labels that match the active language and data contract; do not merely relabel a Western model while keeping Western assumptions.
- Accept the scripts and width forms authorized by the domain, then normalize only for a documented purpose. Never rewrite the user's legal/display name silently.
- For organizations, support legal corporate names and both prefix/suffix forms such as `株式会社〇〇` and `〇〇株式会社`; do not parse company type with naive string removal.
- For search: allow searching by either family name or given name, and by partial match. Japanese users commonly search by family name only.

### Addresses

- Japanese addresses follow this order: postal code → prefecture (`都道府県`) → municipality (`市区町村`) → street/block number → building name.
- Do not rearrange fields to match Western ordering (street → city → state → zip).
- Prefecture field: use a dropdown or autocomplete of all 47 prefectures, not a free-text input.
- Labels in Japanese: `郵便番号` (postal code), `都道府県` (prefecture), `市区町村` (city/ward), `番地` (street/block), `建物名` (building name, optional).
- Postal-code auto-fill is a suggestion. Let the user review and correct every address segment, including building name and nonstandard locality text.
- Preserve the submitted representation when it is legally or operationally significant; a normalized search key must not replace the display or source value.

### Furigana / Yomigana

- If the product handles names that will be read aloud, sorted by reading, or searched by pronunciation, add furigana fields: `姓（フリガナ）` and `名（フリガナ）`.
- Follow the domain's required script and normalization. Do not use an over-restrictive Katakana-only regex without testing middle dots, long-vowel marks, iteration marks, spaces, foreign names, and other valid readings for the audience.
- Furigana is not the same as romanized name (romaji). Do not auto-generate one from the other without product approval.

## Copy and layout

- Use Japanese product copy, not untranslated English library defaults.
- Avoid concatenating translated fragments; use full message templates with placeholders.
- Do not rely on English plural grammar. Use count-aware Japanese phrasing designed by the product.
- Test long organization names, mixed Japanese/Latin text, full-width characters, and unbroken identifiers.
- Give form labels persistent visible space; placeholder is an example, not the label.
- Localize accessible labels for icon buttons, pagination, password reveal, clear search, sort direction, and dialogs.

### Dialog action verbs

Use natural Japanese action verbs, not generic translated `OK` / `Cancel`.

| English | Natural Japanese | Avoid |
|---------|-----------------|-------|
| Delete | `削除` | `OK` |
| Save | `保存` | `OK` |
| Cancel | `キャンセル` | — |
| Discard changes | `破棄` or `保存しないで戻る` | `Cancel` |
| Confirm | `確認` | `OK` |
| Apply | `適用` | `OK` |
| Close | `閉じる` | `OK` |
| Send | `送信` | `OK` |
| Add | `追加` | `OK` |
| Remove | `削除` | `OK` |

Do not use machine-translated button labels. Follow `japanese-content-design.md`; critical or high-traffic actions require native Japanese review with relevant domain context.

### Toast and feedback messages

- Toast messages must sound natural in Japanese. Do not directly translate English toast templates.
- Examples of natural Japanese toasts:

| English | Natural Japanese |
|---------|-----------------|
| Analysis saved | `分析を保存しました` |
| Failed to save | `保存に失敗しました` |
| Analysis deleted | `分析を削除しました` |
| Settings updated | `設定を更新しました` |
| Password changed | `パスワードを変更しました` |
| Export started | `エクスポートを開始しました` |

## Export and encoding

### CSV export

- Use **UTF-8 with BOM** — this is the most compatible encoding for Japanese CSV files opened in Microsoft Excel on Windows.
- Shift_JIS is legacy and causes mojibake (garbled characters) in modern tools. Do not use Shift_JIS unless the product explicitly requires compatibility with legacy enterprise systems that cannot read UTF-8 BOM.
- CSV header names must be in Japanese, not English.
- Test the exported CSV by opening it in Excel, Google Sheets, and a text editor.

### File names

- Choose ASCII or Japanese file names from audience and interoperability evidence rather than a blanket rule. Sanitize path separators/control characters and emit standards-compliant download headers.
- Test the chosen naming policy on the supported browser/OS matrix, including Windows Excel workflows when they matter.

## Validation and feedback

- All validation, empty, loading, retry, confirmation, toast, and tooltip copy must be Japanese when the active product locale is Japanese.
- Error messages identify the field/problem and how to correct it. Do not expose raw schema/library messages.
- Dialog action verbs should be specific and natural: avoid generic translated `OK` when `削除`, `保存`, or `キャンセル` communicates the outcome.

### Required-field error example

```html
<!-- Wrong — English placeholder leak -->
<span class="error">This field is required</span>

<!-- Right -->
<span class="error">入力必須項目です</span>

<!-- Better — field-specific -->
<span class="error">メールアドレスを入力してください</span>
```

## Minimum locale and input test pass

1. Switch to Japanese locale and confirm no fallback English in owned UI.
2. Enter text with Japanese IME in search and normal fields; verify Enter, shortcuts, validation, autosave, counters, autocomplete, and command palettes do not consume composition prematurely.
3. Open and keyboard-operate the calendar.
4. Check date-only, JST timestamp, JPY (no decimals), large numbers, and sorting.
5. Inspect narrow layouts with long Japanese labels and mixed identifiers.
6. Verify screen-reader names/status messages use the active locale.
7. Export a CSV and open in Excel — confirm no mojibake.
8. Submit a form with required-field markers — confirm the marker style is consistent.
9. Use preset date-range filters — confirm natural Japanese labels.
10. Enter and review a Japanese address (postal code → prefecture → city → street/block → building); confirm auto-fill remains editable.
11. Exercise full-/half-width, kana, Latin-name, corporate-name, phone, and long-identifier cases from the actual audience contract.
12. Confirm frontend and backend use the same documented normalization, fiscal-year, timezone, tax, and calendar policies where applicable.
