# Japanese Visual and Layout Contract

Read this for Japanese-facing visual work, including landing pages. It refines upstream aesthetic direction for Japanese script and the target audience; it does not prescribe a universal Japanese style.

## Typography foundation

- Put a Japanese-capable family before generic fallbacks and verify every licensed weight. Avoid a Latin-first stack that produces mismatched Kanji, kana, punctuation, and numerals.
- Use approximately `16px` as the default body baseline. Smaller text requires a bounded dense-data reason and must remain readable at zoom.
- Japanese prose generally needs more line height than Latin prose. Define separate styles for prose, controls, dense tables, and numeric/technical content.
- Do not use italic as the default emphasis primitive. Prefer weight, color, border, label, or structure with sufficient contrast.
- Test Kanji, hiragana, katakana, Latin text, full-/half-width characters, symbols, and digits together. Font fallback must not change control geometry unexpectedly.

## Composition and line breaking

- Test Japanese line-breaking and kinsoku behavior. Opening punctuation must not be stranded at line end; closing punctuation and small kana must not be stranded at line start.
- Set prose measure using representative full-width Japanese characters, not a Latin-only `ch` assumption. Validate at real viewport widths instead of relying on one numeric limit.
- Use semantic `<ruby>` and `<rt>` when furigana is required. Do not fake ruby with superscript spans or absolute positioning.
- Do not insert manual `<br>` tags merely to make one Japanese sample look balanced; verify localization and responsive reflow.
- Keep important identifiers, dates, prices, and units readable across wrapping boundaries. Never truncate a legally or operationally significant value without a full-value path.

## Density and hierarchy

- Derive density from task frequency, comparison need, user expertise, device, and accessibility—not from a stereotype that Japanese interfaces are always dense.
- Dense B2B tables may use compact rows and restrained line height when scanability, focus, targets, and full values remain usable.
- Consumer, public-service, unfamiliar, and high-consequence flows usually need stronger grouping, explicit progress, and more correction guidance.
- Visual hierarchy may be information-rich without becoming noisy: use headings, grouping, alignment, labels, whitespace, and disclosure before adding color or decoration.

## Cultural decoration

Sakura, red-sun motifs, washi, brush type, anime, “Zen” minimalism, and ceremonial language are not defaults. Use cultural imagery only when the brand, campaign, or researched audience calls for it. Product evidence and accessibility override upstream pressure to take an aesthetic risk.

## Required visual checks

- Render long Japanese labels and body copy at narrow and wide viewports.
- Test 200% zoom/reflow, user font replacement where practical, and fallback-font loading/failure.
- Inspect mixed-script baseline, punctuation, numbers, units, badges, tables, form labels, and buttons.
- Capture representative `ja-JP` visual regression states when the project has visual testing.
- Check that no English-only casing, italics, letter spacing, or sentence-length assumption leaks into Japanese styles.
