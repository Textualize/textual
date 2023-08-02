[
  (path_mod)
  "||"
  "&&"
  "="
  "<"
  ">"
  "<="
  ">="
  "+"
  "-"
  "*"
  "/"
  "!"
  "|"
  "^"
] @operator

[
  "_:"
  (namespace)
] @namespace

[
  "UNDEF"
  "a"
] @variable.builtin


[
  "ADD"
  "ALL"
  "AS"
  "ASC"
  "ASK"
  "BIND"
  "BY"
  "CLEAR"
  "CONSTRUCT"
  "COPY"
  "CREATE"
  "DEFAULT"
  "DELETE"
  "DELETE DATA"
  "DELETE WHERE"
  "DESC"
  "DESCRIBE"
  "DISTINCT"
  "DROP"
  "EXISTS"
  "FILTER"
  "FROM"
  "GRAPH"
  "GROUP"
  "HAVING"
  "INSERT"
  "INSERT DATA"
  "INTO"
  "LIMIT"
  "LOAD"
  "MINUS"
  "MOVE"
  "NAMED"
  "NOT"
  "OFFSET"
  "OPTIONAL"
  "ORDER"
  "PREFIX"
  "REDUCED"
  "SELECT"
  "SERVICE"
  "SILENT"
  "UNION"
  "USING"
  "VALUES"
  "WHERE"
  "WITH"
] @keyword

(string) @string
(echar) @string.escape

(integer) @number
[
  (decimal)
  (double)
] @float
(boolean_literal) @boolean

[
  "BASE"
  "PREFIX"
] @keyword

[
  "ABS"
  "AVG"
  "BNODE"
  "BOUND"
  "CEIL"
  "CONCAT"
  "COALESCE"
  "CONTAINS"
  "DATATYPE"
  "DAY"
  "ENCODE_FOR_URI"
  "FLOOR"
  "HOURS"
  "IF"
  "IRI"
  "LANG"
  "LANGMATCHES"
  "LCASE"
  "MD5"
  "MINUTES"
  "MONTH"
  "NOW"
  "RAND"
  "REGEX"
  "ROUND"
  "SECONDS"
  "SHA1"
  "SHA256"
  "SHA384"
  "SHA512"
  "STR"
  "SUM"
  "MAX"
  "MIN"
  "SAMPLE"
  "GROUP_CONCAT"
  "SEPARATOR"
  "COUNT"
  "STRAFTER"
  "STRBEFORE"
  "STRDT"
  "STRENDS"
  "STRLANG"
  "STRLEN"
  "STRSTARTS"
  "STRUUID"
  "TIMEZONE"
  "TZ"
  "UCASE"
  "URI"
  "UUID"
  "YEAR"
  "isBLANK"
  "isIRI"
  "isLITERAL"
  "isNUMERIC"
  "isURI"
  "sameTerm"
] @function.builtin

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
  "{"
  "}"
  (nil)
  (anon)
] @punctuation.bracket

[
  "IN"
  ("NOT" "IN")
] @keyword.operator


(comment) @comment


; Could this be summarized?
(select_clause
  [
    bound_variable: (var)
    "*"
  ] @parameter)
(bind bound_variable: (var) @parameter)
(data_block bound_variable: (var) @parameter)
(group_condition bound_variable: (var) @parameter)

(iri_reference ["<" ">"] @namespace)

(lang_tag) @type
(rdf_literal
  "^^" @type
	datatype: (_ ["<" ">" (namespace)] @type) @type)

(function_call identifier: (_) @function)

(function_call identifier: (iri_reference ["<" ">"] @function))
(function_call identifier: (prefixed_name (namespace) @function))
(base_declaration (iri_reference ["<" ">"] @variable))
(prefix_declaration (iri_reference ["<" ">"] @variable))

[
  (var)
  (blank_node_label)
  (iri_reference)
  (prefixed_name)
] @variable
