; Keywords

[
  "class"
  "clone"
  "delete"
  "enum"
  "extends"
  "rawcall"
  "resume"
  "var"
] @keyword

[
  "function"
] @keyword.function

[
  "in"
  "instanceof"
  "typeof"
] @keyword.operator

[
  "return"
  "yield"
] @keyword.return

((global_variable
   "::"
   (_) @keyword.coroutine)
  (#any-of? @keyword.coroutine "suspend" "newthread"))

; Conditionals

[
  "if"
  "else"
  "switch"
  "case"
  "default"
  "break"
] @conditional

; Repeats

[
  "for"
  "foreach"
  "do"
  "while"
  "continue"
] @repeat

; Exceptions

[
  "try"
  "catch"
  "throw"
] @exception

; Storageclasses

[
  "local"
] @storageclass

; Qualifiers

[
  "static"
  "const"
] @type.qualifier

; Variables

(identifier) @variable

(local_declaration
  (identifier) @variable.local
  . "=")


(global_variable) @variable.global

((identifier) @variable.builtin
  (#any-of? @variable.builtin "base" "this" "vargv"))

; Parameters

(parameter
  . (identifier) @parameter)

; Properties (Slots)

(deref_expression
  "."
  . (identifier) @property)

(member_declaration
  (identifier) @property
  . "=")

((table_slot
  . (identifier) @property
  . ["=" ":"])
  (#set! "priority" 105))

; Types

((identifier) @type
 (#lua-match? @type "^[A-Z]"))

(class_declaration
  (identifier) @type
  "extends"? . (identifier)? @type)

(enum_declaration
  (identifier) @type)

; Attributes

(attribute_declaration
  left: (identifier) @attribute)

; Functions & Methods

(member_declaration
  (function_declaration
    "::"? (_) @method . "(" (_)? ")"))

((function_declaration
   "::"? (_) @function . "(" (_)? ")")
  (#not-has-ancestor? @function member_declaration))

(call_expression
  function: (identifier) @function.call)

(call_expression
  function: (deref_expression
    "." . (identifier) @function.call))

(call_expression
  (global_variable
    "::"
    (_) @function.call))

(_
  (identifier) @function
  "="
  (lambda_expression
    "@" @symbol))

(call_expression
  [
   function: (identifier) @function.builtin
   function: (global_variable "::" (_) @function.builtin)
   function: (deref_expression "." (_) @function.builtin)
  ]
  (#any-of? @function.builtin
   ; General Methods
   "assert" "array" "callee" "collectgarbage" "compilestring"
   "enabledebughook" "enabledebuginfo" "error" "getconsttable"
   "getroottable" "print" "resurrectunreachable" "setconsttable"
   "setdebughook" "seterrorhandler" "setroottable" "type"

   ; Hidden Methods
   "_charsize_" "_intsize_" "_floatsize_" "_version_" "_versionnumber_"

   ; Number Methods
   "tofloat" "tostring" "tointeger" "tochar"

   ; String Methods
   "len" "slice" "find" "tolower" "toupper"

   ; Table Methods
   "rawget" "rawset" "rawdelete" "rawin" "clear"
   "setdelegate" "getdelegate" "filter" "keys" "values"

   ; Array Methods
   "append" "push" "extend" "pop" "top" "insert" "remove" "resize" "sort"
   "reverse" "map" "apply" "reduce"

   ; Function Methods
   "call" "pcall" "acall" "pacall" "setroot" "getroot" "bindenv" "getinfos"

   ; Class Methods
   "instance" "getattributes" "setattributes" "newmember" "rawnewmember"

   ; Class Instance Methods
   "getclass"

   ; Generator Methods
   "getstatus"

   ; Thread Methods
   "call" "wakeup" "wakeupthrow" "getstackinfos"

   ; Weak Reference Methods
   "ref" "weakref"
))

(member_declaration
  "constructor" @constructor)

; Constants

(const_declaration
  "const"
  . (identifier) @constant)

(enum_declaration
  "{"
  . (identifier) @constant)

((identifier) @constant
 (#lua-match? @constant "^_*[A-Z][A-Z%d_]*$"))

; Operators

[
  "+"
  "-"
  "*"
  "/"
  "%"
  "||"
  "&&"
  "|"
  "^"
  "&"
  "=="
  "!="
  "<=>"
  ">"
  ">="
  "<="
  "<"
  "<<"
  ">>"
  ">>>"
  "="
  "<-"
  "+="
  "-="
  "*="
  "/="
  "%="
  "~"
  "!"
  "++"
  "--"
] @operator

; Punctuation

[ "{" "}" ] @punctuation.bracket

[ "[" "]" ] @punctuation.bracket

[ "(" ")" ] @punctuation.bracket

[ "</" "/>" ] @punctuation.bracket

[
  "."
  ","
  ";"
  ":"
] @punctuation.delimiter

[
  "::"
  "..."
] @punctuation.special

; Ternaries

(ternary_expression
  "?" @conditional.ternary
  ":" @conditional.ternary)

; Literals

(string) @string

(verbatim_string) @string.special

(char) @character

(escape_sequence) @string.escape

(integer) @number

(float) @float

(bool) @boolean

(null) @constant.builtin

; Comments

(comment) @comment @spell

((comment) @comment.documentation
  (#lua-match? @comment.documentation "^/[*][*][^*].*[*]/$"))
