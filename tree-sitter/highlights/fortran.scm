; Preprocs

(preproc_file_line) @preproc

; Namespaces

(program_statement
  (name) @namespace)

(end_program_statement
  (name) @namespace)

(module_statement
  (name) @namespace)

(end_module_statement
  (name) @namespace)

(submodule_statement
  (name) @namespace)

(end_submodule_statement
  (name) @namespace)

; Includes

[
  "import"
  "include"
  "use"
] @include

(import_statement
  ","
  ["all" "none"] @keyword)

; Attributes

[
  (none)
  "implicit"
  "intent"
] @attribute

(implicit_statement
  "type" @attribute)

; Keywords

[
  "attributes"
  "associate"
  "block"
  "class"
  "classis"
  "contains"
  "default"
  "dimension"
  "endassociate"
  "endenum"
  "endinterface"
  "endmodule"
  "endselect"
  "endsubmodule"
  "endtype"
  "enum"
  "enumerator"
  "equivalence"
  "extends"
  "goto"
  "interface"
  "intrinsic"
  "non_intrinsic"
  "module"
  "submodule"
  "namelist"
  "parameter"
  "quiet"
  "rank"
  "save"
  "selectcase"
  "selectrank"
  "selecttype"
  "sequence"
  "stop"
  "target"
  "type"
  "typeis"
] @keyword

[
  (default)
] @keyword

; Types

[
  (type_name)
] @type

[
  (intrinsic_type)
] @type.builtin

; Qualifiers

[
  "abstract"
  "allocatable"
  "automatic"
  "constant"
  "contiguous"
  "data"
  "deferred"
  "device"
  "external"
  "family"
  "final"
  "generic"
  "global"
  "grid_global"
  "host"
  "initial"
  "local"
  "local_init"
  "managed"
  "nopass"
  "non_overridable"
  "optional"
  "pass"
  "pinned"
  "pointer"
  "private"
  "property"
  "protected"
  "public"
  "shared"
  "static"
  "texture"
  "value"
  "volatile"
  (procedure_qualifier)
] @type.qualifier

[
  "common"
  "in"
  "inout"
  "out"
] @storageclass

; Labels

[
  (statement_label)
  (statement_label_reference)
] @label

[
  "call"
  "endfunction"
  "endprogram"
  "endprocedure"
  "endsubroutine"
  "function"
  "procedure"
  "program"
  "subroutine"
] @keyword.function

[
  "result"
  "return"
] @keyword.return

; Functions

(function_statement
  (name) @function)

(end_function_statement
  (name) @function)

(subroutine_statement
  (name) @function)

(end_subroutine_statement
  (name) @function)

(module_procedure_statement
  (name) @function)

(end_module_procedure_statement
  (name) @function)

(subroutine_call
  (identifier) @function.call)

[
  "character"
  "close"
  "bind"
  "format"
  "open"
  "print"
  "read"
  "write"
] @function.builtin

; Exceptions

[
  "error"
] @exception

; Conditionals

[
  "else"
  "elseif"
  "elsewhere"
  "endif"
  "endwhere"
  "if"
  "then"
  "where"
] @conditional

; Repeats

[
  "do"
  "concurrent"
  "enddo"
  "endforall"
  "forall"
  "while"
  "continue"
  "cycle"
  "exit"
] @repeat

; Variables

(identifier) @variable

; Parameters

(keyword_argument
  name: (identifier) @parameter)

(parameters
  (identifier) @parameter)

; Properties

(derived_type_member_expression
  (type_member) @property)

; Operators

[
  "+"
  "-"
  "*"
  "**"
  "/"
  "="
  "<"
  ">"
  "<="
  ">="
  "=="
  "/="
  "//"
  (assumed_rank)
] @operator

[
  "\\.and\\."
  "\\.or\\."
  "\\.eqv\\."
  "\\.neqv\\."
  "\\.lt\\."
  "\\.gt\\."
  "\\.le\\."
  "\\.ge\\."
  "\\.eq\\."
  "\\.ne\\."
  "\\.not\\."
] @keyword.operator

; Punctuation

[ "[" "]" ] @punctuation.bracket

[ "(" ")" ] @punctuation.bracket

[ "<<<" ">>>" ] @punctuation.bracket

(array_literal
  ["(/" "/)"] @punctuation.bracket)

[
  ":"
  ","
  "/"
  "%"
  "::"
  "=>"
] @punctuation.delimiter

; Literals

(string_literal) @string

(number_literal) @number

(boolean_literal) @boolean

(null_literal) @constant.builtin

; Comments

(comment) @comment @spell

((comment) @comment.documentation
  (#lua-match? @comment.documentation "^!>"))

; Errors

(ERROR) @error
