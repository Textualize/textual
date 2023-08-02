(_) @spell

((tag
  (name) @text.todo @nospell
  ("(" @punctuation.bracket (user) @constant ")" @punctuation.bracket)?
  ":" @punctuation.delimiter)
  (#any-of? @text.todo "TODO" "WIP"))

("text" @text.todo @nospell
 (#any-of? @text.todo "TODO" "WIP"))

((tag
  (name) @text.note @nospell
  ("(" @punctuation.bracket (user) @constant ")" @punctuation.bracket)?
  ":" @punctuation.delimiter)
  (#any-of? @text.note "NOTE" "XXX" "INFO" "DOCS" "PERF" "TEST"))

("text" @text.note @nospell
 (#any-of? @text.note "NOTE" "XXX" "INFO" "DOCS" "PERF" "TEST"))

((tag
  (name) @text.warning @nospell
  ("(" @punctuation.bracket (user) @constant ")" @punctuation.bracket)?
  ":" @punctuation.delimiter)
  (#any-of? @text.warning "HACK" "WARNING" "WARN" "FIX"))

("text" @text.warning @nospell
 (#any-of? @text.warning "HACK" "WARNING" "WARN" "FIX"))

((tag
  (name) @text.danger @nospell
  ("(" @punctuation.bracket (user) @constant ")" @punctuation.bracket)?
  ":" @punctuation.delimiter)
  (#any-of? @text.danger "FIXME" "BUG" "ERROR"))

("text" @text.danger @nospell
 (#any-of? @text.danger "FIXME" "BUG" "ERROR"))

; Issue number (#123)
("text" @number
 (#lua-match? @number "^#[0-9]+$"))

((uri) @text.uri @nospell)
