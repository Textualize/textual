;;; Identifiers

(identifier) @variable

; ;; If you want type highlighting based on Julia naming conventions (this might collide with mathematical notation)
; ((identifier) @type
;   (match? @type "^[A-Z][^_]"))  ; exception: Highlight `A_foo` sort of identifiers as variables

(macro_identifier) @function.macro
(macro_identifier
  (identifier) @function.macro) ; for any one using the variable highlight

(macro_definition
  name: (identifier) @function.macro)

(quote_expression
  ":" @symbol
  [(identifier) (operator)] @symbol)

(field_expression
  (identifier) @field .)


;;; Function names

;; Definitions

(function_definition
  name: (identifier) @function)
(short_function_definition
  name: (identifier) @function)

(function_definition
  name: (field_expression (identifier) @function .))
(short_function_definition
  name: (field_expression (identifier) @function .))

;; calls

(call_expression
  (identifier) @function.call)
(call_expression
  (field_expression (identifier) @function.call .))

(broadcast_call_expression
  (identifier) @function.call)
(broadcast_call_expression
  (field_expression (identifier) @function.call .))

;; Builtins

((identifier) @function.builtin
  (#any-of? @function.builtin
  "_abstracttype" "_apply_iterate" "_apply_pure" "_call_in_world" "_call_in_world_total"
  "_call_latest" "_equiv_typedef" "_expr" "_primitivetype" "_setsuper!" "_structtype"
  "_typebody!" "_typevar" "applicable" "apply_type" "arrayref" "arrayset" "arraysize"
  "const_arrayref" "donotdelete" "fieldtype" "get_binding_type" "getfield" "ifelse" "invoke" "isa"
  "isdefined" "modifyfield!" "nfields" "replacefield!" "set_binding_type!" "setfield!" "sizeof"
  "svec" "swapfield!" "throw" "tuple" "typeassert" "typeof"))


;;; Parameters

(parameter_list
  (identifier) @parameter)
(optional_parameter .
  (identifier) @parameter)
(slurp_parameter
  (identifier) @parameter)

(typed_parameter
  parameter: (identifier)? @parameter
  type: (_) @type)

(function_expression
  . (identifier) @parameter) ; Single parameter arrow functions


;;; Types

;; Definitions

(abstract_definition
  name: (identifier) @type.definition) @keyword
(primitive_definition
  name: (identifier) @type.definition) @keyword
(struct_definition
  name: (identifier) @type)
(type_clause
  [(identifier) @type
    (field_expression (identifier) @type .)])

;; Annotations

(parametrized_type_expression
  (_) @type
  (curly_expression (_) @type))

(type_parameter_list
  (identifier) @type)

(typed_expression
  (identifier) @type .)

(function_definition
  return_type: (identifier) @type)
(short_function_definition
  return_type: (identifier) @type)

(where_clause
  (identifier) @type)
(where_clause
  (curly_expression (_) @type))

;; Builtins

((identifier) @type.builtin
 (#any-of? @type.builtin
  "Type" "DataType" "Any" "Union" "UnionAll" "Tuple" "NTuple" "NamedTuple"
  "Val" "Nothing" "Some" "Enum" "Expr" "Symbol" "Module" "Function" "ComposedFunction"
  "Number" "Real" "AbstractFloat" "Integer" "Signed" "AbstractIrrational"
  "Fix1" "Fix2" "Missing" "Cmd" "EnvDict" "VersionNumber" "ArgumentError"
  "AssertionError" "BoundsError" "CompositeException" "DimensionMismatch"
  "DivideError" "DomainError" "EOFError" "ErrorException" "InexactError"
  "InterruptException" "KeyError" "LoadError" "MethodError" "OutOfMemoryError"
  "ReadOnlyMemoryError" "OverflowError" "ProcessFailedException" "StackOverflowError"
  "SystemError" "TypeError" "UndefKeywordError" "UndefRefError" "UndefVarError"
  "StringIndexError" "InitError" "ExponentialBackOff" "Timer" "AsyncCondition"
  "ParseError" "QuoteNode" "IteratorSize" "IteratorEltype" "AbstractRange"
  "OrdinalRange" "AbstractUnitRange" "StepRange" "UnitRange" "LinRange" "AbstractDict"
  "Dict" "IdDict" "WeakKeyDict" "ImmutableDict" "AbstractSet" "Set" "BitSet" "Pair"
  "Pairs" "OneTo" " StepRangeLen" "RoundingMode" "Float16" "Float32" "Float64"
  "BigFloat" "Bool" "Int" "Int8" "UInt8" "Int16" "UInt16" "Int32" "UInt32" "Int64"
  "UInt64" "Int128" "UInt128" "BigInt" "Complex" "Rational" "Irrational" "AbstractChar"
  "Char" "SubString" "Regex" "SubstitutionString" "RegexMatch" "AbstractArray"
  "AbstractVector" "AbstractMatrix" "AbstractVecOrMat" "Array" "UndefInitializer"
  "Vector" "Matrix" "VecOrMat" "DenseArray" "DenseVector" "DenseMatrix" "DenseVecOrMat"
  "StridedArray" "StridedVector" "StridedMatrix" "StridedVecOrMat" "BitArray" "Dims"
  "SubArray" "Task" "Condition" "Event" "Semaphore" "AbstractLniock" "ReentrantLock"
  "Channel" "Atomic" "SpinLock" "RawFD" "IOStream" "IOBuffer" "AbstractDisplay" "MIME"
  "TextDisplay" "PartialQuickSort" "Ordering" "ReverseOrdering" "By" "Lt" "Perm"
  "Stateful" "CFunction" "Ptr" "Ref" "Cchar" "Cuchar" "Cshort" "Cstring" "Cushort"
  "Cint" "Cuint" "Clong" "Culong" "Clonglong" "Culonglong" "Cintmax_t" "Cuintmax_t"
  "Csize_t" "Cssize_t" "Cptrdiff_t" "Cwchar_t" "Cwstring" "Cfloat" "Cdouble" "Tmstruct"
  "StackFrame" "StackTrace"))

((identifier) @variable.builtin
  (#any-of? @variable.builtin "begin" "end")
  (#has-ancestor? @variable.builtin index_expression))

((identifier) @variable.builtin
  (#any-of? @variable.builtin "begin" "end")
  (#has-ancestor? @variable.builtin range_expression))

;;; Keywords

[
  "global"
  "local"
  "macro"
  "struct"
  "end"
] @keyword


(compound_statement
  ["begin" "end"] @keyword)
(quote_statement
  ["quote" "end"] @keyword)
(let_statement
  ["let" "end"] @keyword)

(if_statement
  ["if" "end"] @conditional)
(elseif_clause
  "elseif" @conditional)
(else_clause
  "else" @conditional)
(if_clause
  "if" @conditional) ; `if` clause in comprehensions
(ternary_expression
  ["?" ":"] @conditional.ternary)

(try_statement
  ["try" "end"] @exception)
(finally_clause
  "finally" @exception)
(catch_clause
  "catch" @exception)

(for_statement
  ["for" "end"] @repeat)
(while_statement
  ["while" "end"] @repeat)
(for_clause
  "for" @repeat)
[
  (break_statement)
  (continue_statement)
] @repeat

(module_definition
  ["module" "baremodule" "end"] @include)
(import_statement
  ["import" "using"] @include)
(import_alias
  "as" @include)
(export_statement
  "export" @include)

(macro_definition
  ["macro" "end" @keyword])

(function_definition
  ["function" "end"] @keyword.function)
(do_clause
  ["do" "end"] @keyword.function)
(return_statement
  "return" @keyword.return)

[
  "const"
  "mutable"
] @type.qualifier


;;; Operators & Punctuation

[
  "="
  "∈"
  (operator)
] @operator

(adjoint_expression "'" @operator)
(range_expression ":" @operator)

((operator) @keyword.operator
  (#any-of? @keyword.operator "in" "isa"))

(for_binding "in" @keyword.operator)

(where_clause "where" @keyword.operator)
(where_expression "where" @keyword.operator)

[
  ","
  "."
  ";"
  "::"
  "->"
] @punctuation.delimiter

[
  "..."
] @punctuation.special

["(" ")" "[" "]" "{" "}"] @punctuation.bracket


;;; Literals

(boolean_literal) @boolean
(integer_literal) @number
(float_literal) @float

((identifier) @float
  (#any-of? @float "NaN" "NaN16" "NaN32"
                   "Inf" "Inf16" "Inf32"))

((identifier) @constant.builtin
  (#any-of? @constant.builtin "nothing" "missing"))

(character_literal) @character
(escape_sequence) @string.escape

(string_literal) @string
(prefixed_string_literal
  prefix: (identifier) @function.macro) @string

(command_literal) @string.special
(prefixed_command_literal
  prefix: (identifier) @function.macro) @string.special

((string_literal) @string.documentation
  . [
      (module_definition)
      (abstract_definition)
      (struct_definition)
      (function_definition)
      (short_function_definition)
      (assignment)
      (const_statement)
    ])

[
  (line_comment)
  (block_comment)
] @comment @spell
