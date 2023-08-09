;; Forked from tree-sitter-regex
;; The MIT License (MIT) Copyright (c) 2014 Max Brunsfeld
[
 "("
 ")"
 "(?"
 "(?:"
 "(?<"
 ">"
 "["
 "]"
 "{"
 "}"
] @regex.punctuation.bracket

(group_name) @property

;; These are escaped special characters that lost their special meaning
;; -> no special highlighting
(identity_escape) @string.regex

(class_character) @constant

[
 (control_letter_escape)
 (character_class_escape)
 (control_escape)
 (start_assertion)
 (end_assertion)
 (boundary_assertion)
 (non_boundary_assertion)
] @string.escape

[ "*" "+" "?" "|" "=" "!" ] @regex.operator
