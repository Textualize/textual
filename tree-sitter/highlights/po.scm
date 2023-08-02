; Keywords

[
  "msgctxt"
  "msgid"
  "msgid_plural"
  "msgstr"
  "msgstr_plural"
] @keyword

; Punctuation

[ "[" "]" ] @punctuation.bracket

; Literals

(string) @string

(escape_sequence) @string.escape

(number) @number

; Comments

(comment) @comment @spell

(comment (reference (text) @string.special.path))

(comment (flag (text) @preproc))

; Errors

(ERROR) @error
