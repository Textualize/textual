(string) @string
(number) @number
(comment) @comment

(function_call
    function: (identifier) @function)

[
  (NULL)
  (TRUE)
  (FALSE)
] @constant.builtin

([
  (type_cast
   (type (identifier) @type.builtin))
  (create_function_statement
   (type (identifier) @type.builtin))
  (create_function_statement
   (create_function_parameters
     (create_function_parameter (type (identifier) @type.builtin))))
  (create_type_statement
    (type_spec_composite (type (identifier) @type.builtin)))
  (create_table_statement
   (table_parameters
     (table_column (type (identifier) @type.builtin))))
 ]
 (#match?
   @type.builtin
    "^(bigint|BIGINT|int8|INT8|bigserial|BIGSERIAL|serial8|SERIAL8|bit|BIT|varbit|VARBIT|boolean|BOOLEAN|bool|BOOL|box|BOX|bytea|BYTEA|character|CHARACTER|char|CHAR|varchar|VARCHAR|cidr|CIDR|circle|CIRCLE|date|DATE|float8|FLOAT8|inet|INET|integer|INTEGER|int|INT|int4|INT4|interval|INTERVAL|json|JSON|jsonb|JSONB|line|LINE|lseg|LSEG|macaddr|MACADDR|money|MONEY|numeric|NUMERIC|decimal|DECIMAL|path|PATH|pg_lsn|PG_LSN|point|POINT|polygon|POLYGON|real|REAL|float4|FLOAT4|smallint|SMALLINT|int2|INT2|smallserial|SMALLSERIAL|serial2|SERIAL2|serial|SERIAL|serial4|SERIAL4|text|TEXT|time|TIME|time|TIME|timestamp|TIMESTAMP|tsquery|TSQUERY|tsvector|TSVECTOR|txid_snapshot|TXID_SNAPSHOT|enum|ENUM|range|RANGE)$"))

(identifier) @variable

[
  "::"
  "<"
  "<="
  "<>"
  "="
  ">"
  ">="
] @operator

[
  "("
  ")"
  "["
  "]"
] @punctuation.bracket

[
  ";"
  "."
] @punctuation.delimiter

[
  (type)
  (array_type)
] @type

[
 (primary_key_constraint)
 (unique_constraint)
 (null_constraint)
] @keyword

[
  "AND"
  "AS"
  "AUTO_INCREMENT"
  "CREATE"
  "CREATE_DOMAIN"
  "CREATE_OR_REPLACE_FUNCTION"
  "CREATE_SCHEMA"
  "TABLE"
  "TEMPORARY"
  "CREATE_TYPE"
  "DATABASE"
  "FROM"
  "GRANT"
  "GROUP_BY"
  "IF_NOT_EXISTS"
  "INDEX"
  "INNER"
  "INSERT"
  "INTO"
  "IN"
  "JOIN"
  "LANGUAGE"
  "LEFT"
  "LOCAL"
  "NOT"
  "ON"
  "OR"
  "ORDER_BY"
  "OUTER"
  "PRIMARY_KEY"
  "PUBLIC"
  "RETURNS"
  "SCHEMA"
  "SELECT"
  "SESSION"
  "SET"
  "TABLE"
  "TIME_ZONE"
  "TO"
  "UNIQUE"
  "UPDATE"
  "USAGE"
  "VALUES"
  "WHERE"
  "WITH"
  "WITHOUT"
] @keyword
