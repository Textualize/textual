---
title: "How can I set a transparent app background?"
alt_titles:
  - "Transparent background in the app"
  - "See-through background"
  - "See-through app"
  - "Translucid app background"
  - "Textual apps are opaque but terminal is transparent"
---

Textual does not provide a mechanism to make your applications have a transparent background.
Some terminals _do_ provide this functionality but it is not guaranteed that Textual apps will have a transparent background in those cases.

The reason this may not work in Textual is that we _intentionally_ do not use the ANSI background colours.
For the rationale behind this design decision, refer to the FAQ about why Textual doesn't support ANSI themes.
