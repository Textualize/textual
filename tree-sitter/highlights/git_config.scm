; Sections

(section_name) @type

((section_name) @include
 (#eq? @include "include"))

((section_header
   (section_name) @include
   (subsection_name))
 (#eq? @include "includeIf"))

(variable (name) @property)

; Operators

[
 "="
] @operator

; Literals

(integer) @number
[
  (true)
  (false)
] @boolean

(string) @string

((string) @text.uri
 (#lua-match? @text.uri "^[.]?[/]"))

((string) @text.uri
 (#lua-match? @text.uri "^[~]"))

(section_header
  [
    "\""
    (subsection_name)
  ] @string.special)

; Punctuation

[ "[" "]" ] @punctuation.bracket

; Comments

(comment) @comment @spell
