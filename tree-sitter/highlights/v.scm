; Includes

[
  "import"
  "module"
] @include

; Keywords

[
  "asm"
  "assert"
  "const"
  "defer"
  "enum"
  "goto"
  "interface"
  "struct"
  "sql"
  "type"
  "union"
  "unsafe"
] @keyword

[
  "as"
  "in"
  "!in"
  "or"
  "is"
  "!is"
] @keyword.operator

[
  "match"
  "if"
  "$if"
  "else"
  "$else"
  "select"
] @conditional

[
  "for"
  "$for"
  "continue"
  "break"
] @repeat

"fn" @keyword.function

"return" @keyword.return

[
  "__global"
  "shared"
  "static"
  "const"
] @storageclass

[
  "pub"
  "mut"
] @type.qualifier

[
  "go"
  "spawn"
  "lock"
  "rlock"
] @keyword.coroutine

; Variables

(identifier) @variable

; Namespace

(module_clause
 (identifier) @namespace)

(import_path
 (import_name) @namespace)

(import_alias
 (import_name) @namespace)

; Literals

[ (true) (false) ] @boolean

(interpreted_string_literal) @string

(string_interpolation) @none

; Types

(struct_declaration
  name: (identifier) @type)

(enum_declaration
  name: (identifier) @type)

(interface_declaration
  name: (identifier) @type)

(type_declaration
  name: (identifier) @type)

(type_reference_expression (identifier) @type)

; Labels

(label_reference) @label

; Fields

(selector_expression field: (reference_expression (identifier) @field))

(field_name) @field

(struct_field_declaration
  name: (identifier) @field)

; Parameters

(parameter_declaration
  name: (identifier) @parameter)

(receiver
  name: (identifier) @parameter)

; Constants

((identifier) @constant
  (#has-ancestor? @constant compile_time_if_expression))

(enum_fetch
  (reference_expression) @constant)

(enum_field_definition
  (identifier) @constant)

(const_definition
  name: (identifier) @constant)

((identifier) @variable.builtin
  (#any-of? @variable.builtin "err" "macos" "linux" "windows"))

; Attributes

(attribute) @attribute

; Functions

(function_declaration
  name: (identifier) @function)

(function_declaration
  receiver: (receiver)
  name: (identifier) @method)

(call_expression
 name: (selector_expression
  field: (reference_expression) @method.call))

(call_expression
 name: (reference_expression) @function.call)

((identifier) @function.builtin
  (#any-of? @function.builtin
    "eprint"
    "eprintln"
    "error"
    "exit"
    "panic"
    "print"
    "println"
    "after"
    "after_char"
    "all"
    "all_after"
    "all_after_last"
    "all_before"
    "all_before_last"
    "any"
    "ascii_str"
    "before"
    "bool"
    "byte"
    "byterune"
    "bytes"
    "bytestr"
    "c_error_number_str"
    "capitalize"
    "clear"
    "clone"
    "clone_to_depth"
    "close"
    "code"
    "compare"
    "compare_strings"
    "contains"
    "contains_any"
    "contains_any_substr"
    "copy"
    "count"
    "cstring_to_vstring"
    "delete"
    "delete_last"
    "delete_many"
    "ends_with"
    "eprint"
    "eprintln"
    "eq_epsilon"
    "error"
    "error_with_code"
    "exit"
    "f32"
    "f32_abs"
    "f32_max"
    "f32_min"
    "f64"
    "f64_max"
    "fields"
    "filter"
    "find_between"
    "first"
    "flush_stderr"
    "flush_stdout"
    "free"
    "gc_check_leaks"
    "get_str_intp_u32_format"
    "get_str_intp_u64_format"
    "grow_cap"
    "grow_len"
    "hash"
    "hex"
    "hex2"
    "hex_full"
    "i16"
    "i64"
    "i8"
    "index"
    "index_after"
    "index_any"
    "index_byte"
    "insert"
    "int"
    "is_alnum"
    "is_bin_digit"
    "is_capital"
    "is_digit"
    "is_hex_digit"
    "is_letter"
    "is_lower"
    "is_oct_digit"
    "is_space"
    "is_title"
    "is_upper"
    "isnil"
    "join"
    "join_lines"
    "keys"
    "last"
    "last_index"
    "last_index_byte"
    "length_in_bytes"
    "limit"
    "malloc"
    "malloc_noscan"
    "map"
    "match_glob"
    "memdup"
    "memdup_noscan"
    "move"
    "msg"
    "panic"
    "panic_error_number"
    "panic_lasterr"
    "panic_optional_not_set"
    "parse_int"
    "parse_uint"
    "pointers"
    "pop"
    "prepend"
    "print"
    "print_backtrace"
    "println"
    "proc_pidpath"
    "ptr_str"
    "push_many"
    "realloc_data"
    "reduce"
    "repeat"
    "repeat_to_depth"
    "replace"
    "replace_each"
    "replace_once"
    "reverse"
    "reverse_in_place"
    "runes"
    "sort"
    "sort_by_len"
    "sort_ignore_case"
    "sort_with_compare"
    "split"
    "split_any"
    "split_into_lines"
    "split_nth"
    "starts_with"
    "starts_with_capital"
    "str"
    "str_escaped"
    "str_intp"
    "str_intp_g32"
    "str_intp_g64"
    "str_intp_rune"
    "str_intp_sq"
    "str_intp_sub"
    "strg"
    "string_from_wide"
    "string_from_wide2"
    "strip_margin"
    "strip_margin_custom"
    "strlong"
    "strsci"
    "substr"
    "substr_ni"
    "substr_with_check"
    "title"
    "to_lower"
    "to_upper"
    "to_wide"
    "tos"
    "tos2"
    "tos3"
    "tos4"
    "tos5"
    "tos_clone"
    "trim"
    "trim_left"
    "trim_pr"
    "try_pop"
    "try_push"
    "utf32_decode_to_buffer"
    "utf32_to_str"
    "utf32_to_str_no_malloc"
    "utf8_char_len"
    "utf8_getchar"
    "utf8_str_len"
    "utf8_str_visible_length"
    "utf8_to_utf32"
    "v_realloc"
    "vbytes"
    "vcalloc"
    "vcalloc_noscan"
    "vmemcmp"
    "vmemcpy"
    "vmemmove"
    "vmemset"
    "vstring"
    "vstring_literal"
    "vstring_literal_with_len"
    "vstring_with_len"
    "vstrlen"
    "vstrlen_char"
    "winapi_lasterr_str"))

; Operators

[
  "++"
  "--"

  "+"
  "-"
  "*"
  "/"
  "%"

  "~"
  "&"
  "|"
  "^"

  "!"
  "&&"
  "||"
  "!="

  "<<"
  ">>"

  "<"
  ">"
  "<="
  ">="

  "+="
  "-="
  "*="
  "/="
  "&="
  "|="
  "^="
  "<<="
  ">>="

  "="
  ":="
  "=="

  "?"
  "<-"
  "$"
  ".."
  "..."
] @operator

; Punctuation

[ "." "," ":" ";" ] @punctuation.delimiter

[ "(" ")" "{" "}" "[" "]" ] @punctuation.bracket

; Literals

(int_literal) @number

(float_literal) @float

[
  (c_string_literal)
  (raw_string_literal)
  (interpreted_string_literal)
  (string_interpolation)
  (rune_literal)
] @string

(string_interpolation
  (braced_interpolation_opening) @punctuation.bracket
  (interpolated_expression) @none
  (braced_interpolation_closing) @punctuation.bracket)

(escape_sequence) @string.escape

[
  (true)
  (false)
] @boolean

(nil) @constant.builtin

(none) @variable.builtin

; Comments

(comment) @comment @spell

(_
  (comment)+ @comment.documentation
  [(function_declaration) (type_declaration) (enum_declaration)])

; Errors

(ERROR) @error
