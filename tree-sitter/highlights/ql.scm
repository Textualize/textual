[
  "as"
  "by"
  "class"
  "extends"
  "from"
  "implies"
  "in"
  "module"
  "newtype"
  "order"
  "select"
  "where"

  (predicate)
  (result)
  (specialId)
] @keyword

[
  "and"
  "not"
  "or"
] @keyword.operator

[
  "avg"
  "any"
  "count"
  "concat"
  "exists"
  "max"
  "min"
  "instanceof"
  "rank"
  "sum"
  "strictconcat"
  "strictcount"
  "strictsum"
] @function.builtin

"import" @include

[
  "if"
  "then"
  "else"
] @conditional

[
  "forall"
  "forex"
] @repeat

[
  "asc"
  "desc"
] @type.qualifier

[
  (true)
  (false)
] @boolean

[
  (this)
  (super)
] @variable.builtin

[
  "boolean"
  "float"
  "int"
  "date"
  "string"
] @type.builtin

(annotName) @attribute

[
  "<"
  "<="
  "="
  ">"
  ">="
  "-"
  "!="
  "/"
  "*"
  "%"
  "+"
  "::"
] @operator

[
  "("
  ")"
  "{"
  "}"
  "["
  "]"
] @punctuation.bracket

[
  ","
  "|"
] @punctuation.delimiter

(moduleExpr (simpleId) @namespace)
(module name: (moduleName) @namespace)

(dataclass name: (className) @type)
(typeExpr name: (className) @type)

(datatype name: (className) @type.definition)

(importModuleExpr qualName: (simpleId) @variable)
(varName) @variable

(integer) @number
(float) @float

(string) @string

(aritylessPredicateExpr (literalId) @function)
(memberPredicate name: (predicateName) @function)
(classlessPredicate name: (predicateName) @function)
(charpred (className) @function)

[
  (line_comment)
  (block_comment)
] @comment @spell

(qldoc) @comment.documentation
