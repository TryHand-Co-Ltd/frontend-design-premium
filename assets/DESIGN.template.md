---
version: alpha
name: "[Project name]"
description: "[One-sentence product and visual identity]"
colors:
  primary: "#1A1C1E"
  # Replace with your concrete primary hex. Define every color token here.
  # Add more keys as needed: secondary, danger, success, background, ...
  # Do NOT leave colors as an empty map {} — that passes lint but is useless.
# Omitted sections: uncomment and list sections you intentionally skip.
# Do NOT define the section key both in omitted and in the frontmatter.
# - section: spacing
#   reason: "inherited from upstream frontend-design"
# - section: rounded
#   reason: "not applicable to this project"
typography:
  sans:
    fontFamily: "system-ui, sans-serif"
    # Update fontFamily from project evidence (e.g. font stack from tailwind.config, CSS variables, or design tokens)
  mono:
    fontFamily: "ui-monospace, monospace"
rounded:
  DEFAULT: "0.5rem"
  sm: "0.25rem"
  md: "0.5rem"
  lg: "0.75rem"
spacing:
  section-gap: "3rem"
  page-max: "72rem"
components:
  button: { }
  card: { }
  dialog: { }
  # Add every shared component. Empty braces {} mean "tokens defined in prose, not frontmatter".
  # table: { }
  # input: { }
---

# [Project name] Design System

> Replace every bracketed prompt with evidence from the brief, repository, shared components, and rendered product. Remove this note when complete. Do not invent values that are not implemented or intentionally approved.
>
> **IMPORTANT:** Empty frontmatter maps (`colors: {}`) are NOT complete. Either fill concrete values, or uncomment the `omitted:` section above to exclude sections with a reason. Never write `colors: omitted` as a value — that is invalid YAML and will cause lint errors.

## Overview

### Creative North Star

[Describe one specific reference or physical world that communicates the intended look and feel better than generic adjectives.]

### Product context and register

- **Audience and primary job:** [Who uses it and what they need to accomplish.]
- **Usage scene:** [Device, environment, frequency, urgency, and information density.]
- **Register:** [Brand, product, or hybrid; identify routes if hybrid.]
- **Memorable signature:** [The one distinctive move that may carry expression.]
- **Restraint:** [Where familiarity and quiet utility must win.]
- **Anti-references:** [Products/styles/registers this must not resemble, with reasons.]
- **Token ownership/runtime mapping:** [State whether this file generates tokens or mirrors an existing canonical source; link the CSS/Tailwind/theme adapter manifest and drift gate.]

## Colors

[Explain palette character, semantic roles, expressive accents, surfaces, borders, text hierarchy, focus, selection, charts, and light/dark/high-contrast behavior. Reference exact frontmatter tokens.]

## Typography

[Explain families, locale-capable fallbacks, roles, weights, line heights, measure, numeric/technical text, Japanese script behavior, and casing rules. Reference exact tokens.]

## Layout

[Explain grid, max widths, responsive breakpoints, density, spacing rhythm, safe areas, navigation geometry, table/form layout, and layout-stability rules. Do not assume a 4px/8px scale without evidence.]

## Elevation & Depth

[Explain how hierarchy is conveyed: tonal layers, borders, shadows, blur, overlays, sticky surfaces, and dark-mode behavior. State where elevation is forbidden.]

## Shapes

[Explain radius/edge language, control and container shapes, icon containers, dividers, strokes, and any deliberate exceptions. Reference exact rounded tokens.]

## Components

### Foundational visual states

[Document default, hover, focus-visible, active/pressed, selected, disabled, read-only, busy, success, warning, error, and skeleton treatment for shared primitives.]

### Buttons and actions

[Document emphasis × intent hierarchy, sizing, icon placement, destructive separation, and busy geometry.]

### Navigation and data display

[Document navigation surfaces, tabs, breadcrumbs, tables/lists, charts, badges, tags, and responsive transformations.]

### Forms and overlays

[Document fields, search, validation, date/combobox/upload controls, dialogs, drawers, bottom sheets, alerts, toasts, and tooltips.]

### Iconography

[Name the icon family, stroke/fill policy, sizes, optical alignment, and when text labels remain mandatory.]

### Motion

[Define the motion character, feedback/content durations, easing, interruption policy, and reduced-motion behavior. Motion must communicate state rather than decorate routine work.]

### Content and data visualization

[Define product voice, action vocabulary, numeric formatting, chart palette, annotation style, and accessible data alternatives.]

## Do's and Don'ts

- **Do:** [A high-value positive rule that preserves the North Star.]
- **Do:** [A consistency rule tied to actual product evidence.]
- **Don't:** [A specific anti-pattern or wrong register.]
- **Don't:** [A visual choice that would weaken hierarchy, accessibility, or product familiarity.]
