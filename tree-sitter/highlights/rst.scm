;; Marks

[
  ".."
  "|"
  "--"
  "__"
  ":"
  "::"
  "bullet"
  "adornment"
  (transition)
] @punctuation.special

;; Resets for injection

(doctest_block) @none

;; Directives

(directive
  name: (type) @function)

(directive
  body: (body (arguments) @parameter))

((directive
  name: (type) @include)
 (#eq? @include "include"))

((directive
   name: (type) @function.builtin)
 (#any-of?
  @function.builtin
  ; https://docutils.sourceforge.io/docs/ref/rst/directives.html
  "attention" "caution" "danger" "error" "hint" "important" "note" "tip" "warning" "admonition"
  "image" "figure"
  "topic" "sidebar" "line-block" "parsed-literal" "code" "math" "rubric" "epigraph" "highlights" "pull-quote" "compound" "container"
  "table" "csv-table" "list-table"
  "contents" "sectnum" "section-numbering" "header" "footer"
  "target-notes"
  "meta"
  "replace" "unicode" "date"
  "raw" "class" "role" "default-role" "title" "restructuredtext-test-directive"))

;; Blocks

[
  (literal_block)
  (line_block)
] @text.literal

(block_quote
  (attribution)? @text.emphasis) @text.literal

(substitution_definition
  name: (substitution) @constant)

(footnote
  name: (label) @constant)

(citation
  name: (label) @constant)

(target
  name: (name)? @constant
  link: (_)? @text.literal)

;; Lists

; Definition lists
(list_item
  (term) @text.strong
  (classifier)? @text.emphasis)

; Field lists
(field (field_name) @constant)

;; Inline markup

(emphasis) @text.emphasis

(strong) @text.strong

(standalone_hyperlink) @text.uri @nospell

(role) @function

((role) @function.builtin
 (#any-of?
  @function.builtin
  ; https://docutils.sourceforge.io/docs/ref/rst/roles.html
  ":emphasis:"
  ":literal:"
  ":code:"
  ":math:"
  ":pep-reference:"
  ":PEP:"
  ":rfc-reference:"
  ":RFC:"
  ":strong:"
  ":subscript:"
  ":sub:"
  ":superscript:"
  ":sup:"
  ":title-reference:"
  ":title:"
  ":t:"
  ":raw:"))

[
 "interpreted_text"
  (literal)
] @text.literal

; Prefix role
((interpreted_text
  (role) @_role
  "interpreted_text" @text.emphasis)
 (#eq? @_role ":emphasis:"))

((interpreted_text
  (role) @_role
  "interpreted_text" @text.strong)
 (#eq? @_role ":strong:"))

((interpreted_text
  (role) @_role
  "interpreted_text" @none)
 (#eq? @_role ":math:"))

; Suffix role
((interpreted_text
  "interpreted_text" @text.emphasis
  (role) @_role)
 (#eq? @_role ":emphasis:"))

((interpreted_text
  "interpreted_text" @text.strong
  (role) @_role)
 (#eq? @_role ":strong:"))

((interpreted_text
  "interpreted_text" @none
  (role) @_role)
 (#eq? @_role ":math:"))

[
  (inline_target)
  (substitution_reference)
  (footnote_reference)
  (citation_reference)
  (reference)
] @text.reference @nospell

;; Others

(title) @text.title

(comment) @comment @spell
(comment "..") @comment

(directive
    name: (type) @_directive
    body: (body
        (content) @spell
        (#not-any-of? @_directive "code" "code-block" "sourcecode")))

(paragraph) @spell

(ERROR) @error
