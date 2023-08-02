(comment) @comment @spell

[
  "("
  ")"
  "{"
  "}"
  "["
  "]"
] @punctuation.bracket

[
  ":"
  ":until"
  "&"
  "&as"
  "?"
] @punctuation.special

(nil) @constant.builtin
(vararg) @punctuation.special

(boolean) @boolean
(number) @number

(string) @string @spell
(escape_sequence) @string.escape

(symbol) @variable

(multi_symbol
   "." @punctuation.delimiter
   (symbol) @field)

(multi_symbol_method
   ":" @punctuation.delimiter
   (symbol) @method.call .)

(list . (symbol) @function.call)
(list . (multi_symbol (symbol) @function.call .))

((symbol) @variable.builtin
 (#lua-match? @variable.builtin "^[$]"))

(binding) @symbol

[
  "fn"
  "lambda"
  "hashfn"
  "#"
] @keyword.function

(fn name: [
 (symbol) @function
 (multi_symbol (symbol) @function .)
])

(lambda name: [
 (symbol) @function
 (multi_symbol (symbol) @function .)
])

[
  "for"
  "each"
] @repeat
((symbol) @repeat
 (#any-of? @repeat
  "while"))

[
  "match"
] @conditional
((symbol) @conditional
 (#any-of? @conditional
  "if" "when"))

[
  "global"
  "local"
  "let"
  "set"
  "var"
  "where"
  "or"
] @keyword
((symbol) @keyword
 (#any-of? @keyword
  "comment" "do" "doc" "eval-compiler" "lua" "macros" "quote" "tset" "values"))

((symbol) @include
 (#any-of? @include
  "require" "require-macros" "import-macros" "include"))

[
  "collect"
  "icollect"
  "accumulate"
] @function.macro

((symbol) @function.macro
 (#any-of? @function.macro
  "->" "->>" "-?>" "-?>>" "?." "doto" "macro" "macrodebug" "partial" "pick-args"
  "pick-values" "with-open"))

; Lua builtins
((symbol) @constant.builtin
 (#any-of? @constant.builtin
  "arg" "_ENV" "_G" "_VERSION"))

((symbol) @function.builtin
 (#any-of? @function.builtin
  "assert" "collectgarbage" "dofile" "error" "getmetatable" "ipairs"
  "load" "loadfile" "next" "pairs" "pcall" "print" "rawequal" "rawget"
  "rawlen" "rawset" "require" "select" "setmetatable" "tonumber" "tostring"
  "type" "warn" "xpcall"))

((symbol) @function.builtin
 (#any-of? @function.builtin
  "loadstring" "module" "setfenv" "unpack"))
