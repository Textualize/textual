;; From tree-sitter-python licensed under MIT License
; Copyright (c) 2016 Max Brunsfeld

; Variables
(identifier) @variable

; Reset highlighting in f-string interpolations
(interpolation) @none

;; Identifier naming conventions
((identifier) @type
 (#lua-match? @type "^[A-Z].*[a-z]"))
((identifier) @constant
 (#lua-match? @constant "^[A-Z][A-Z_0-9]*$"))

((identifier) @constant.builtin
 (#lua-match? @constant.builtin "^__[a-zA-Z0-9_]*__$"))

((identifier) @constant.builtin
 (#any-of? @constant.builtin
           ;; https://docs.python.org/3/library/constants.html
           "NotImplemented"
           "Ellipsis"
           "quit"
           "exit"
           "copyright"
           "credits"
           "license"))

((attribute
    attribute: (identifier) @field)
 (#lua-match? @field "^[%l_].*$"))

((assignment
  left: (identifier) @type.definition
  (type (identifier) @_annotation))
 (#eq? @_annotation "TypeAlias"))

((assignment
  left: (identifier) @type.definition
  right: (call
    function: (identifier) @_func))
 (#any-of? @_func "TypeVar" "NewType"))

;; Decorators
((decorator "@" @attribute)
 (#set! "priority" 101))

(decorator
  (identifier) @attribute)
(decorator
  (attribute
    attribute: (identifier) @attribute))
(decorator
  (call (identifier) @attribute))
(decorator
  (call (attribute
          attribute: (identifier) @attribute)))

((decorator
  (identifier) @attribute.builtin)
 (#any-of? @attribute.builtin "classmethod" "property"))

;; Builtin functions
((call
  function: (identifier) @function.builtin)
 (#any-of? @function.builtin
          "abs" "all" "any" "ascii" "bin" "bool" "breakpoint" "bytearray" "bytes" "callable" "chr" "classmethod"
          "compile" "complex" "delattr" "dict" "dir" "divmod" "enumerate" "eval" "exec" "fail" "filter" "float" "format"
          "frozenset" "getattr" "globals" "hasattr" "hash" "help" "hex" "id" "input" "int" "isinstance" "issubclass"
          "iter" "len" "list" "locals" "map" "max" "memoryview" "min" "next" "object" "oct" "open" "ord" "pow"
          "print" "property" "range" "repr" "reversed" "round" "set" "setattr" "slice" "sorted" "staticmethod" "str"
          "struct" "sum" "super" "tuple" "type" "vars" "zip" "__import__"))

;; Function definitions
(function_definition
  name: (identifier) @function)

(type (identifier) @type)
(type
  (subscript
    (identifier) @type)) ; type subscript: Tuple[int]

((call
  function: (identifier) @_isinstance
  arguments: (argument_list
    (_)
    (identifier) @type))
 (#eq? @_isinstance "isinstance"))

((identifier) @type.builtin
 (#any-of? @type.builtin
              ;; https://docs.python.org/3/library/exceptions.html
              "ArithmeticError" "BufferError" "LookupError" "AssertionError" "AttributeError"
              "EOFError" "FloatingPointError" "ModuleNotFoundError" "IndexError" "KeyError"
              "KeyboardInterrupt" "MemoryError" "NameError" "NotImplementedError" "OSError" "OverflowError" "RecursionError"
              "ReferenceError" "RuntimeError" "StopIteration" "StopAsyncIteration" "SyntaxError" "IndentationError" "TabError"
              "SystemError" "SystemExit" "TypeError" "UnboundLocalError" "UnicodeError" "UnicodeEncodeError" "UnicodeDecodeError"
              "UnicodeTranslateError" "ValueError" "ZeroDivisionError" "EnvironmentError" "IOError" "WindowsError"
              "BlockingIOError" "ChildProcessError" "ConnectionError" "BrokenPipeError" "ConnectionAbortedError"
              "ConnectionRefusedError" "ConnectionResetError" "FileExistsError" "FileNotFoundError" "InterruptedError"
              "IsADirectoryError" "NotADirectoryError" "PermissionError" "ProcessLookupError" "TimeoutError" "Warning"
              "UserWarning" "DeprecationWarning" "PendingDeprecationWarning" "SyntaxWarning" "RuntimeWarning"
              "FutureWarning" "UnicodeWarning" "BytesWarning" "ResourceWarning"
              ;; https://docs.python.org/3/library/stdtypes.html
              "bool" "int" "float" "complex" "list" "tuple" "range" "str"
              "bytes" "bytearray" "memoryview" "set" "frozenset" "dict" "type"))

;; Normal parameters
(parameters
  (identifier) @parameter)
;; Lambda parameters
(lambda_parameters
  (identifier) @parameter)
(lambda_parameters
  (tuple_pattern
    (identifier) @parameter))
; Default parameters
(keyword_argument
  name: (identifier) @parameter)
; Naming parameters on call-site
(default_parameter
  name: (identifier) @parameter)
(typed_parameter
  (identifier) @parameter)
(typed_default_parameter
  (identifier) @parameter)
; Variadic parameters *args, **kwargs
(parameters
  (list_splat_pattern ; *args
    (identifier) @parameter))
(parameters
  (dictionary_splat_pattern ; **kwargs
    (identifier) @parameter))


;; Literals
(none) @constant.builtin
[(true) (false)] @boolean
((identifier) @variable.builtin
 (#eq? @variable.builtin "self"))
((identifier) @variable.builtin
 (#eq? @variable.builtin "cls"))

(integer) @number
(float) @float

(comment) @comment @spell

((module . (comment) @preproc)
  (#lua-match? @preproc "^#!/"))

(string) @string
[
  (escape_sequence)
  "{{"
  "}}"
] @string.escape

; doc-strings

(module . (expression_statement (string) @string.documentation @spell))

(function_definition
  body:
    (block
      . (expression_statement (string) @string.documentation @spell)))

; Tokens

[
  "-"
  "-="
  ":="
  "!="
  "*"
  "**"
  "**="
  "*="
  "/"
  "//"
  "//="
  "/="
  "&"
  "&="
  "%"
  "%="
  "^"
  "^="
  "+"
  "+="
  "<"
  "<<"
  "<<="
  "<="
  "<>"
  "="
  "=="
  ">"
  ">="
  ">>"
  ">>="
  "@"
  "@="
  "|"
  "|="
  "~"
  "->"
] @operator

; Keywords
[
  "and"
  "in"
  "not"
  "or"

  "del"
] @keyword.operator

[
  "def"
  "lambda"
] @keyword.function

[
  "async"
  "await"
  "exec"
  "nonlocal"
  "pass"
  "print"
  "with"
  "as"
] @keyword

[
  "async"
  "await"
] @keyword.coroutine

[
  "return"
] @keyword.return

((call
  function: (identifier) @include
  arguments: (argument_list
	(string) @conceal))
  (#eq? @include "load"))

["if" "elif" "else" "match" "case"] @conditional

["for" "while" "break" "continue"] @repeat

["(" ")" "[" "]" "{" "}"] @punctuation.bracket

(interpolation
  "{" @punctuation.special
  "}" @punctuation.special)

(type_conversion) @function.macro

["," "." ":" ";" (ellipsis)] @punctuation.delimiter

;; Error
(ERROR) @error

;; Starlark-specific

;; Assertion calls
(assert_keyword) @keyword

(assert_builtin) @function.builtin

;; Struct definitions
((call
  function: (identifier) @_func
  arguments: (argument_list
    (keyword_argument
	  name: (identifier) @field)))
  (#eq? @_func "struct"))

;; Function calls

(call
  function: (identifier) @function.call)

(call
  function: (attribute
              attribute: (identifier) @method.call))

((call
   function: (identifier) @constructor)
 (#lua-match? @constructor "^[A-Z]"))

((call
  function: (attribute
              attribute: (identifier) @constructor))
 (#lua-match? @constructor "^[A-Z]"))
