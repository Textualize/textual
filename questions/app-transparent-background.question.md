---
title: "How can I set a transparent app background?"
alt_titles:
  - "Transparent background in the app"
  - "See-through background"
  - "See-through app"
  - "Translucid app background"
  - "Textual apps are opaque but terminal is transparent"
---

Textual does not use the ANSI background colors that some terminals use.
As a consequence, even if your terminal supports transparent backgrounds, it is not guaranteed that Textual apps will have their background transparent.

The decision of not using ANSI background colors is intentional and it is because we need to ensure Textual apps look consistently good on all terminals.
For the full rationale behind this design decision, refer to the FAQ about why Textual doesn't support ANSI themes.
