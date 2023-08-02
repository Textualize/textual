; Variables

(variable) @variable

((variable) @constant.builtin
 (#eq? @constant.builtin "$ENV"))

((variable) @constant.macro
 (#eq? @constant.macro "$__loc__"))

; Properties

(index
   (identifier) @property)

; Labels

(query
   label: (variable) @label)

(query
   break_statement: (variable) @label)

; Literals

(number) @number

(string) @string

[
   "true"
   "false"
] @boolean

("null") @type.builtin

; Interpolation

["\\(" ")"] @character.special

; Format

(format) @attribute

; Functions

(funcdef
   (identifier) @function)

(funcdefargs
   (identifier) @parameter)

[
  "reduce"
  "foreach"
] @function.builtin

; jq -n 'builtins | map(split("/")[0]) | unique | .[]'
((funcname) @function.builtin
 (#any-of? @function.builtin
   "IN"
   "INDEX"
   "JOIN"
   "acos"
   "acosh"
   "add"
   "all"
   "any"
   "arrays"
   "ascii_downcase"
   "ascii_upcase"
   "asin"
   "asinh"
   "atan"
   "atan2"
   "atanh"
   "booleans"
   "bsearch"
   "builtins"
   "capture"
   "cbrt"
   "ceil"
   "combinations"
   "contains"
   "copysign"
   "cos"
   "cosh"
   "debug"
   "del"
   "delpaths"
   "drem"
   "empty"
   "endswith"
   "env"
   "erf"
   "erfc"
   "error"
   "exp"
   "exp10"
   "exp2"
   "explode"
   "expm1"
   "fabs"
   "fdim"
   "finites"
   "first"
   "flatten"
   "floor"
   "fma"
   "fmax"
   "fmin"
   "fmod"
   "format"
   "frexp"
   "from_entries"
   "fromdate"
   "fromdateiso8601"
   "fromjson"
   "fromstream"
   "gamma"
   "get_jq_origin"
   "get_prog_origin"
   "get_search_list"
   "getpath"
   "gmtime"
   "group_by"
   "gsub"
   "halt"
   "halt_error"
   "has"
   "hypot"
   "implode"
   "in"
   "index"
   "indices"
   "infinite"
   "input"
   "input_filename"
   "input_line_number"
   "inputs"
   "inside"
   "isempty"
   "isfinite"
   "isinfinite"
   "isnan"
   "isnormal"
   "iterables"
   "j0"
   "j1"
   "jn"
   "join"
   "keys"
   "keys_unsorted"
   "last"
   "ldexp"
   "leaf_paths"
   "length"
   "lgamma"
   "lgamma_r"
   "limit"
   "localtime"
   "log"
   "log10"
   "log1p"
   "log2"
   "logb"
   "ltrimstr"
   "map"
   "map_values"
   "match"
   "max"
   "max_by"
   "min"
   "min_by"
   "mktime"
   "modf"
   "modulemeta"
   "nan"
   "nearbyint"
   "nextafter"
   "nexttoward"
   "normals"
   "not"
   "now"
   "nth"
   "nulls"
   "numbers"
   "objects"
   "path"
   "paths"
   "pow"
   "pow10"
   "range"
   "recurse"
   "recurse_down"
   "remainder"
   "repeat"
   "reverse"
   "rindex"
   "rint"
   "round"
   "rtrimstr"
   "scalars"
   "scalars_or_empty"
   "scalb"
   "scalbln"
   "scan"
   "select"
   "setpath"
   "significand"
   "sin"
   "sinh"
   "sort"
   "sort_by"
   "split"
   "splits"
   "sqrt"
   "startswith"
   "stderr"
   "strflocaltime"
   "strftime"
   "strings"
   "strptime"
   "sub"
   "tan"
   "tanh"
   "test"
   "tgamma"
   "to_entries"
   "todate"
   "todateiso8601"
   "tojson"
   "tonumber"
   "tostream"
   "tostring"
   "transpose"
   "trunc"
   "truncate_stream"
   "type"
   "unique"
   "unique_by"
   "until"
   "utf8bytelength"
   "values"
   "walk"
   "while"
   "with_entries"
   "y0"
   "y1"
   "yn"))

; Keywords

[
  "def"
  "as"
  "label"
  "module"
  "break"
] @keyword

[
  "import"
  "include"
] @include

[
  "if"
  "then"
  "elif"
  "else"
  "end"
] @conditional

[
  "try"
  "catch"
] @exception

[
  "or"
  "and"
] @keyword.operator

; Operators

[
  "."
  "=="
  "!="
  ">"
  ">="
  "<="
  "<"
  "="
  "+"
  "-"
  "*"
  "/"
  "%"
  "+="
  "-="
  "*="
  "/="
  "%="
  "//="
  "|"
  "?"
  "//"
  "?//"
  (recurse) ; ".."
] @operator

; Punctuation

[
  ";"
  ","
  ":"
] @punctuation.delimiter

[
  "[" "]"
  "{" "}"
  "(" ")"
] @punctuation.bracket

; Comments

(comment) @comment @spell
