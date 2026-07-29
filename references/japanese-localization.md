# Japanese Localization Contract

Read this when the product locale is Japanese or when changing dates, calendars, search, validation, numbers, currency, addresses, names, or component-library locale providers.

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

## Japanese IME and search

- Do not dispatch debounced search while `InputEvent.isComposing` is true or between `compositionstart` and `compositionend`.
- Dispatch the final query after composition ends.
- Do not bind Enter to submit/search while it is committing IME composition.
- Cancel stale requests and ensure older responses cannot replace newer Japanese queries.
- Decide normalization (width, kana, case) with the search backend. Never silently normalize only the client if it changes matching semantics.

## Numbers, money, names, and addresses

### Currency

- Format JPY with `Intl.NumberFormat("ja-JP", { style: "currency", currency: "JPY" })`. Do not hardcode `¥` placement or decimal rules.
- **JPY has no decimal places.** Never show `.00` or `¥1,000.00`. The correct display is `¥1,000` or `￥1,000`.
- For non-JPY currencies (USD, EUR), always show the appropriate decimal places and currency symbol. Do not strip decimals from non-JPY currencies because the primary locale is Japanese.

### Phone numbers

- Japanese phone numbers are typically `0X-XXXX-XXXX` or `0XX-XXX-XXXX`. Use a single input with automatic formatting or separate fields with clear labels.
- Accept half-width digits (`03-1234-5678`) and store in half-width. Do not store full-width digits (`０３−１２３４−５６７８`).
- Do not force a country code unless the product serves an international audience. In Japan-only products, `+81` prefix is optional.

### Postal codes

- Japanese postal code format: `XXX-XXXX` (3 digits + hyphen + 4 digits). Example: `100-0001`.
- Accept and store in half-width. Validate the pattern but do not assume you can look up the address from the code.
- If address auto-fill from postal code is a product goal, integrate a third-party address lookup API (e.g., 郵便番号検索 API). Do not build your own lookup.

### Names

- Do not force Western first-name/last-name ordering. The product data model should have separate fields for family name (`姓`) and given name (`名`) in that visual order, unless the domain explicitly specifies Western order.
- Always show `姓` / `名` labels, not `First name` / `Last name`.
- Accept full-width characters for names. Half-width katakana is common in some systems; clarify the requirement with the product owner.
- For search: allow searching by either family name or given name, and by partial match. Japanese users commonly search by family name only.

### Addresses

- Japanese addresses follow this order: postal code → prefecture (`都道府県`) → municipality (`市区町村`) → street/block number → building name.
- Do not rearrange fields to match Western ordering (street → city → state → zip).
- Prefecture field: use a dropdown or autocomplete of all 47 prefectures, not a free-text input.
- Labels in Japanese: `郵便番号` (postal code), `都道府県` (prefecture), `市区町村` (city/ward), `番地` (street/block), `建物名` (building name, optional).

### Furigana / Yomigana

- If the product handles names that will be read aloud, sorted by reading, or searched by pronunciation, add furigana fields: `姓（フリガナ）` and `名（フリガナ）`.
- Store in full-width katakana. Validate that only katakana, long vowels (ー), and spaces are entered.
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

Do not use machine-translated button labels. Every dialog action must be reviewed by a native Japanese speaker or product copy specialist.

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

- Use ASCII-only file names for exports (e.g., `analysis_2024_01_15.csv`), not Japanese characters. Different OS/browser combinations handle Japanese file names inconsistently during download.
- If the product must use Japanese file names, test on Windows (Chrome, Edge), macOS (Safari, Chrome), and Linux.

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

## Minimum locale test pass

1. Switch to Japanese locale and confirm no fallback English in owned UI.
2. Enter text with Japanese IME in search and normal fields.
3. Open and keyboard-operate the calendar.
4. Check date-only, JST timestamp, JPY (no decimals), large numbers, and sorting.
5. Inspect narrow layouts with long Japanese labels and mixed identifiers.
6. Verify screen-reader names/status messages use the active locale.
7. Export a CSV and open in Excel — confirm no mojibake.
8. Submit a form with required-field markers — confirm the marker style is consistent.
9. Use preset date-range filters — confirm natural Japanese labels.
10. Enter a Japanese address (postal code → prefecture → city) — confirm the field order matches Japan Post convention.
