; basic keywords
[
  "assert"
  "in"
  "inherit"
  "let"
  "rec"
  "with"
] @keyword

(variable_expression
  name: (identifier) @keyword
  (#eq? @keyword "derivation")
  (#set! "priority" 101))

; exceptions
(variable_expression
  name: (identifier) @exception
  (#any-of? @exception "abort" "throw")
  (#set! "priority" 101))

; if/then/else
[
  "if"
  "then"
  "else"
] @conditional

; field access default (`a.b or c`)
"or" @keyword.operator

; comments
(comment) @comment

; strings
([ (string_expression) (indented_string_expression) ]
  (#set! "priority" 99)) @string

; paths and URLs
[ (path_expression) (hpath_expression) (spath_expression) (uri_expression) ] @string.special

; escape sequences
(escape_sequence) @string.escape

; delimiters
[
  "."
  ";"
  ","
] @punctuation.delimiter

; brackets
[
  "("
  ")"
  "["
  "]"
  "{"
  "}"
] @punctuation.bracket

; `?` in `{ x ? y }:`, used to set defaults for named function arguments
(formal
  name: (identifier) @parameter
  "?"? @operator)

; `...` in `{ ... }`, used to ignore unknown named function arguments (see above)
(ellipses) @punctuation.special

; universal is the parameter of the function expression
; `:` in `x: y`, used to separate function argument from body (see above)
(function_expression
  universal: (identifier) @parameter
  ":" @punctuation.special)

; function calls
(apply_expression
  function: (variable_expression
    name: (identifier) @function.call))

; basic identifiers
(variable_expression) @variable

(variable_expression
  name: (identifier) @include
  (#eq? @include "import"))

(variable_expression
  name: (identifier) @boolean
  (#any-of? @boolean "true" "false"))

; builtin functions
(variable_expression name: (identifier) @function.builtin (#any-of? @function.builtin
  ; nix eval --impure --expr 'with builtins; filter (x: !(elem x [ "abort" "derivation" "import" "throw" ]) && isFunction builtins.${x}) (attrNames builtins)'
  "add" "addErrorContext" "all" "any" "appendContext" "attrNames" "attrValues" "baseNameOf" "bitAnd" "bitOr" "bitXor" "break" "catAttrs" "ceil" "compareVersions" "concatLists" "concatMap" "concatStringsSep" "deepSeq" "derivationStrict" "dirOf" "div" "elem" "elemAt" "fetchGit" "fetchMercurial" "fetchTarball" "fetchTree" "fetchurl" "filter" "filterSource" "findFile" "floor" "foldl'" "fromJSON" "fromTOML" "functionArgs" "genList" "genericClosure" "getAttr" "getContext" "getEnv" "getFlake" "groupBy" "hasAttr" "hasContext" "hashFile" "hashString" "head" "intersectAttrs" "isAttrs" "isBool" "isFloat" "isFunction" "isInt" "isList" "isNull" "isPath" "isString" "length" "lessThan" "listToAttrs" "map" "mapAttrs" "match" "mul" "parseDrvName" "partition" "path" "pathExists" "placeholder" "readDir" "readFile" "removeAttrs" "replaceStrings" "scopedImport" "seq" "sort" "split" "splitVersion" "storePath" "stringLength" "sub" "substring" "tail" "toFile" "toJSON" "toPath" "toString" "toXML" "trace" "traceVerbose" "tryEval" "typeOf" "unsafeDiscardOutputDependency" "unsafeDiscardStringContext" "unsafeGetAttrPos" "zipAttrsWith"
  ; primops, `__<tab>` in `nix repl`
 "__add" "__filter" "__isFunction" "__split" "__addErrorContext" "__filterSource" "__isInt" "__splitVersion" "__all" "__findFile" "__isList" "__storeDir" "__any" "__floor" "__isPath" "__storePath" "__appendContext" "__foldl'" "__isString" "__stringLength" "__attrNames" "__fromJSON" "__langVersion" "__sub" "__attrValues" "__functionArgs" "__length" "__substring" "__bitAnd" "__genList" "__lessThan" "__tail" "__bitOr" "__genericClosure" "__listToAttrs" "__toFile" "__bitXor" "__getAttr" "__mapAttrs" "__toJSON" "__catAttrs" "__getContext" "__match" "__toPath" "__ceil" "__getEnv" "__mul" "__toXML" "__compareVersions" "__getFlake" "__nixPath" "__trace" "__concatLists" "__groupBy" "__nixVersion" "__traceVerbose" "__concatMap" "__hasAttr" "__parseDrvName" "__tryEval" "__concatStringsSep" "__hasContext" "__partition" "__typeOf" "__currentSystem" "__hashFile" "__path" "__unsafeDiscardOutputDependency" "__currentTime" "__hashString" "__pathExists" "__unsafeDiscardStringContext" "__deepSeq" "__head" "__readDir" "__unsafeGetAttrPos" "__div" "__intersectAttrs" "__readFile" "__zipAttrsWith" "__elem" "__isAttrs" "__replaceStrings" "__elemAt" "__isBool" "__seq" "__fetchurl" "__isFloat" "__sort"
))

; constants
(variable_expression name: (identifier) @constant.builtin (#any-of? @constant.builtin
  ; nix eval --impure --expr 'with builtins; filter (x: !(isFunction builtins.${x} || isBool builtins.${x})) (attrNames builtins)'
  "builtins" "currentSystem" "currentTime" "langVersion" "nixPath" "nixVersion" "null" "storeDir"
))

; string interpolation (this was very annoying to get working properly)
(interpolation "${" @punctuation.special (_) "}" @punctuation.special) @none

(select_expression
  expression: (_) @_expr
  attrpath: (attrpath attr: (identifier) @field)
  (#not-eq? @_expr "builtins")
)
(attrset_expression (binding_set (binding . (attrpath (identifier) @field))))
(rec_attrset_expression (binding_set (binding . (attrpath (identifier) @field))))

; unary operators
(unary_expression operator: _ @operator)

; binary operators
(binary_expression operator: _ @operator)

; integers, also highlight a unary -
[
  (unary_expression "-" (integer_expression))
  (integer_expression)
] @number

; floats, also highlight a unary -
[
  (unary_expression "-" (float_expression))
  (float_expression)
] @float
