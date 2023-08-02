;; Fish highlighting

;; Operators

[
 "&&"
 "||"
 "|"
 "&"
 ".."
 "!"
 (direction)
 (stream_redirect)
] @operator

;; match operators of test command
(command
  name: (word) @function.builtin (#eq? @function.builtin "test")
  argument: (word) @operator (#match? @operator "^(!?\\=|-[a-zA-Z]+)$"))

;; match operators of [ command
(command
  name: (word) @punctuation.bracket (#eq? @punctuation.bracket "[")
  argument: (word) @operator (#match? @operator "^(!?\\=|-[a-zA-Z]+)$"))

[
 "not"
 "and"
 "or"
] @keyword.operator

;; Conditionals

(if_statement
[
 "if"
 "end"
] @conditional)

(switch_statement
[
 "switch"
 "end"
] @conditional)

(case_clause
[
 "case"
] @conditional)

(else_clause
[
 "else"
] @conditional)

(else_if_clause
[
 "else"
 "if"
] @conditional)

;; Loops/Blocks

(while_statement
[
 "while"
 "end"
] @repeat)

(for_statement
[
 "for"
 "end"
] @repeat)

(begin_statement
[
 "begin"
 "end"
] @repeat)

;; Keywords

[
 "in"
 (break)
 (continue)
] @keyword

"return" @keyword.return

;; Punctuation

[
 "["
 "]"
 "{"
 "}"
 "("
 ")"
] @punctuation.bracket

"," @punctuation.delimiter

;; Commands

(command
  argument: [
             (word) @parameter (#lua-match? @parameter "^[-]")
            ]
)

(command_substitution "$" @punctuation.bracket)

; non-builtin command names
(command name: (word) @function.call)

; derived from builtin -n (fish 3.2.2)
(command
  name: [
        (word) @function.builtin
        (#any-of? @function.builtin "." ":" "_" "alias" "argparse" "bg" "bind" "block" "breakpoint" "builtin" "cd" "command" "commandline" "complete" "contains" "count" "disown" "echo" "emit" "eval" "exec" "exit" "fg" "functions" "history" "isatty" "jobs" "math" "printf" "pwd" "random" "read" "realpath" "set" "set_color" "source" "status" "string" "test" "time" "type" "ulimit" "wait")
        ]
)

;; Functions

(function_definition ["function" "end"] @keyword.function)

(function_definition
  name: [
        (word) (concatenation)
        ]
@function)

(function_definition
  option: [
          (word)
          (concatenation (word))
          ] @parameter (#lua-match? @parameter "^[-]")
)

;; Strings

[(double_quote_string) (single_quote_string)] @string
(escape_sequence) @string.escape

;; Variables

(variable_name) @variable
(variable_expansion) @constant

;; Nodes

[(integer) (float)] @number
(comment) @comment
(comment) @spell

((word) @boolean
(#any-of? @boolean "true" "false"))

((program . (comment) @preproc)
  (#lua-match? @preproc "^#!/"))

;; Error

(ERROR) @error
