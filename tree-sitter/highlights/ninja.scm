[
  "default"
  "pool"
  "rule"
  "build"
] @keyword

[
  "include"
  "subninja"
] @include

[
  ":"
] @punctuation.delimiter

[
  "="
  "|"
  "||"
  "|@"
] @operator

[
  "$"
  "{"
  "}"
] @punctuation.special

;;
;; Names
;; =====
(pool      name: (identifier) @type)
(rule      name: (identifier) @function)
(let       name: (identifier) @constant)
(expansion       (identifier) @constant)
(build     rule: (identifier) @function)

;;
;; Paths and Text
;; ==============
(path) @string.special
(text) @string

;;
;; Builtins
;; ========
(pool  name: (identifier) @type.builtin
                (#any-of? @type.builtin "console"))
(build rule: (identifier) @function.builtin
                (#any-of? @function.builtin "phony" "dyndep"))

;; Top level bindings
;; ------------------
(manifest
  (let name: ((identifier) @constant.builtin
                 (#any-of? @constant.builtin "builddir"
                                             "ninja_required_version"))))

;; Rules bindings
;; -----------------
(rule
  (body
    (let name: (identifier)  @constant.builtin
               (#not-any-of? @constant.builtin "command"
                                               "depfile"
                                               "deps"
                                               "msvc_deps_prefix"
                                               "description"
                                               "dyndep"
                                               "generator"
                                               "in"
                                               "in_newline"
                                               "out"
                                               "restat"
                                               "rspfile"
                                               "rspfile_content"
                                               "pool"))))

;;
;; Expansion
;; ---------
(expansion
  (identifier) @constant.macro
     (#any-of? @constant.macro "in" "out"))

;;
;; Escape sequences
;; ================
(quote) @string.escape

;;
;; Others
;; ======
[
 (split)
 (comment)
] @comment
