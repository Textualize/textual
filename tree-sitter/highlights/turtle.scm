(string) @string

(lang_tag) @type

[
  "_:"
  "<"
  ">"
  (namespace)
] @namespace

[
  (iri_reference)
  (prefixed_name)
] @variable

(blank_node_label) @variable

"a" @variable.builtin

(integer) @number

[
  (decimal)
  (double)
] @float

(boolean_literal) @boolean

[
  "BASE"
  "PREFIX"
  "@prefix"
  "@base"
] @keyword

[
  "."
  ","
  ";"
] @punctuation.delimiter

[
  "("
  ")"
  "["
  "]"
  (anon)
] @punctuation.bracket

(comment) @comment

(echar) @string.escape


(rdf_literal
  "^^" @type
	datatype: (_ ["<" ">" (namespace)] @type) @type)
