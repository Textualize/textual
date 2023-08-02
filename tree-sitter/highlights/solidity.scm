; Pragma

[
  "pragma"
  "solidity"
] @preproc

(solidity_pragma_token
  "||" @symbol)
(solidity_pragma_token
  "-" @symbol)

(solidity_version_comparison_operator) @operator

(solidity_version) @text.underline @string.special

; Literals

[
 (string)
 (yul_string_literal)
] @string

(hex_string_literal
  "hex" @symbol
  (_) @string)

(unicode_string_literal
  "unicode" @symbol
  (_) @string)

[
 (number_literal)
 (yul_decimal_number)
 (yul_hex_number)
] @number

(yul_boolean) @boolean

; Variables

[
  (identifier)
  (yul_identifier)
] @variable

; Types

(type_name (identifier) @type)
(type_name (user_defined_type (identifier) @type))
(type_name "mapping" @function.builtin)

[
  (primitive_type)
  (number_unit)
] @type.builtin

(contract_declaration name: (identifier) @type)
(struct_declaration name: (identifier) @type)
(struct_member name: (identifier) @field)
(enum_declaration name: (identifier) @type)
(emit_statement . (identifier) @type)
; Handles ContractA, ContractB in function foo() override(ContractA, contractB) {}
(override_specifier (user_defined_type) @type)

; Functions and parameters

(function_definition
  name: (identifier) @function)
(modifier_definition
  name: (identifier) @function)
(yul_evm_builtin) @function.builtin

; Use constructor coloring for special functions
(constructor_definition "constructor" @constructor)

(modifier_invocation (identifier) @function)

; Handles expressions like structVariable.g();
(call_expression . (member_expression (identifier) @method.call))

; Handles expressions like g();
(call_expression . (identifier) @function.call)

; Function parameters
(event_paramater name: (identifier) @parameter)
(parameter name: (identifier) @parameter)

; Yul functions
(yul_function_call function: (yul_identifier) @function.call)

; Yul function parameters
(yul_function_definition . (yul_identifier) @function (yul_identifier) @parameter)

(meta_type_expression "type" @keyword)

(member_expression property: (identifier) @field)
(call_struct_argument name: (identifier) @field)
(struct_field_assignment name: (identifier) @field)
(enum_value) @constant

; Keywords

[
  "contract"
  "interface"
  "library"
  "is"
  "struct"
  "enum"
  "event"
  "assembly"
  "emit"
  "override"
  "modifier"
  "var"
  "let"
  "emit"
  "fallback"
  "receive"
  (virtual)
] @keyword

; FIXME: update grammar
; (block_statement "unchecked" @keyword)

(event_paramater "indexed" @keyword)

[
  "public"
  "internal"
  "private"
  "external"
  "pure"
  "view"
  "payable"
  (immutable)
] @type.qualifier

[
  "memory"
  "storage"
  "calldata"
  "constant"
] @storageclass

[
  "for"
  "while"
  "do"
  "break"
  "continue"
] @repeat

[
  "if"
  "else"
  "switch"
  "case"
  "default"
] @conditional

(ternary_expression
  "?" @conditional.ternary
  ":" @conditional.ternary)

[
  "try"
  "catch"
  "revert"
] @exception

[
  "return"
  "returns"
  (yul_leave)
] @keyword.return

"function" @keyword.function

[
  "import"
  "using"
] @include
(import_directive "as" @include)
(import_directive "from" @include)
((import_directive source: (string) @text.underline)
  (#offset! @text.underline 0 1 0 -1))

; Punctuation

[ "{" "}" ] @punctuation.bracket

[ "[" "]" ] @punctuation.bracket

[ "(" ")" ] @punctuation.bracket

[
  "."
  ","
  ":"
  ; FIXME: update grammar
  ; (semicolon)
  "->"
  "=>"
] @punctuation.delimiter

; Operators

[
  "&&"
  "||"
  ">>"
  ">>>"
  "<<"
  "&"
  "^"
  "|"
  "+"
  "-"
  "*"
  "/"
  "%"
  "**"
  "="
  "<"
  "<="
  "=="
  "!="
  "!=="
  ">="
  ">"
  "!"
  "~"
  "-"
  "+"
  "++"
  "--"
  ":="
] @operator

[
  "delete"
  "new"
] @keyword.operator

(import_directive "*" @character.special)

; Comments

(comment) @comment @spell

((comment) @comment.documentation
  (#lua-match? @comment.documentation "^///[^/]"))
((comment) @comment.documentation
  (#lua-match? @comment.documentation "^///$"))

((comment) @comment.documentation
  (#lua-match? @comment.documentation "^/[*][*][^*].*[*]/$"))

; Errors

(ERROR) @error
