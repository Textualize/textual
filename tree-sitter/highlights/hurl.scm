; highlights.scm

[
  "[QueryStringParams]"
  "[FormParams]"
  "[MultipartFormData]"
  "[Cookies]"
  "[Captures]"
  "[Asserts]"
  "[Options]"
  "[BasicAuth]"
  (key_string)
  (json_key_string)
] @property

[
  "\\"
  (regex_escaped_char)
  (quoted_string_escaped_char)
  (key_string_escaped_char)
  (value_string_escaped_char)
  (oneline_string_escaped_char)
  (multiline_string_escaped_char)
  (filename_escaped_char)
  (json_string_escaped_char)
] @string.escape

[
  "status"
  "url"
  "header"
  "cookie"
  "body"
  "xpath"
  "jsonpath"
  "regex"
  "variable"
  "duration"
  "sha256"
  "md5"
  "bytes"
] @function.builtin

[
  "null"
  "cacert"
  "compressed"
  "location"
  "insecure"
  "path-as-is"
  "proxy"
  "max-redirs"
  "retry"
  "retry-interval"
  "retry-max-count"
  (variable_option "variable")
  "verbose"
  "very-verbose"
] @constant.builtin

(boolean) @boolean

(variable_name) @variable

[
  "not"
  "equals"
  "notEquals"
  "greaterThan"
  "greaterThanOrEquals"
  "lessThan"
  "lessThanOrEquals"
  "startsWith"
  "endsWith"
  "contains"
  "matches"
  "exists"
  "includes"
  "isInteger"
  "isFloat"
  "isBoolean"
  "isString"
  "isCollection"
] @keyword.operator

[
  "=="
  "!="
  ">"
  ">="
  "<"
  "<="
] @operator

[
  (integer)
  (status)
] @number

[
  (float)
  (json_number)
] @float

[ ":" "," ] @punctuation.delimiter

[ "[" "]" "{" "}" "{{" "}}" ] @punctuation.bracket

[
  (value_string)
  (quoted_string)
  (json_string)
] @string


[
  "base64,"
  "file,"
  "hex,"
  (file_value)
  (version)
] @string.special

(regex) @string.regex

(multiline_string_type) @type

(comment) @comment @spell

(filter) @attribute

(method) @type.builtin
