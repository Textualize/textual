;; Variables

(list (symbol) @variable)

(cons (symbol) @variable)

(scope (symbol) @variable)

(symbind (symbol) @variable)

;; Constants

((symbol) @constant
  (#lua-match? @constant "^_*[A-Z][A-Z0-9_]*$"))

;; Functions

(list
  . (symbol) @function)

;; Namespaces

(symbind
  (symbol) @namespace
  . (keyword))

;; Includes

((symbol) @include
  (#any-of? @include "use" "import" "load"))

;; Keywords

((symbol) @keyword
  (#any-of? @keyword "do" "doc"))

;; Special Functions

; Keywords construct a symbol

(keyword) @constructor

((list
  . (symbol) @keyword.function
  . (symbol) @function
  (symbol)? @parameter)
  (#any-of? @keyword.function "def" "defop" "defn" "fn"))

((cons
  . (symbol) @keyword.function
  . (symbol) @function
  (symbol)? @parameter)
  (#any-of? @keyword.function "def" "defop" "defn" "fn"))

((symbol) @function.builtin
  (#any-of? @function.builtin "dump" "mkfs" "json" "log" "error" "now" "cons" "wrap" "unwrap" "eval" "make-scope" "bind" "meta" "with-meta" "null?" "ignore?" "boolean?" "number?" "string?" "symbol?" "scope?" "sink?" "source?" "list?" "pair?" "applicative?" "operative?" "combiner?" "path?" "empty?" "thunk?" "+" "*" "quot" "-" "max" "min" "=" ">" ">=" "<" "<=" "list->source" "across" "emit" "next" "reduce-kv" "assoc" "symbol->string" "string->symbol" "str" "substring" "trim" "scope->list" "string->fs-path" "string->cmd-path" "string->dir" "subpath" "path-name" "path-stem" "with-image" "with-dir" "with-args" "with-cmd" "with-stdin" "with-env" "with-insecure" "with-label" "with-port" "with-tls" "with-mount" "thunk-cmd" "thunk-args" "resolve" "start" "addr" "wait" "read" "cache-dir" "binds?" "recall-memo" "store-memo" "mask" "list" "list*" "first" "rest" "length" "second" "third" "map" "map-pairs" "foldr" "foldl" "append" "filter" "conj" "list->scope" "merge" "apply" "id" "always" "vals" "keys" "memo" "succeeds?" "run" "last" "take" "take-all" "insecure!" "from" "cd" "wrap-cmd" "mkfile" "path-base" "not"))

((symbol) @function.macro
  (#any-of? @function.macro "op" "current-scope" "quote" "let" "provide" "module" "or" "and" "curryfn" "for" "$" "linux"))

;; Conditionals

((symbol) @conditional
  (#any-of? @conditional "if" "case" "cond" "when"))

;; Repeats

((symbol) @repeat
  (#any-of? @repeat "each"))

;; Operators

((symbol) @operator (#any-of? @operator "&" "*" "+" "-" "<" "<=" "=" ">" ">="))

;; Punctuation

[ "(" ")" ] @punctuation.bracket

[ "{" "}" ] @punctuation.bracket

[ "[" "]" ] @punctuation.bracket

((symbol) @punctuation.delimiter
  (#eq? @punctuation.delimiter "->"))

;; Literals

(string) @string

(escape_sequence) @string.escape

(path) @text.uri @string.special

(number) @number

(boolean) @boolean

[
  (ignore)
  (null)
] @constant.builtin

[
  "^"
] @character.special

;; Comments

(comment) @comment @spell
