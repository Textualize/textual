(comment) @comment

["if" "elif"] @conditional
(if (else "else" @conditional))

["while" "for"] @repeat
(while (else "else" @repeat))
(for (else "else" @repeat))

["try" "catch" "finally"] @exception
(try (else "else" @exception))

"use" @include
(import (bareword) @string.special)

(wildcard ["*" "**" "?"] @character.special)

(command argument: (bareword) @parameter)
(command head: (identifier) @function.call)
((command head: (identifier) @keyword.return)
 (#eq? @keyword.return "return"))
((command (identifier) @keyword.operator)
 (#any-of? @keyword.operator "and" "or" "coalesce"))
[
 "+" "-" "*" "/" "%" "<" "<=""==" "!=" ">"
 ">=" "<s" "<=s" "==s" "!=s" ">s" ">=s"
] @function.builtin

[">" "<" ">>" "<>" "|"] @operator

(io_port) @number

(function_definition
  "fn" @keyword.function
  (identifier) @function)

(parameter_list) @parameter
(parameter_list "|" @punctuation.bracket)

["var" "set" "tmp" "del"] @keyword
(variable_declaration
  (lhs (identifier) @variable))

(variable_assignment
  (lhs (identifier) @variable))

(temporary_assignment
  (lhs (identifier) @variable))

(variable_deletion
  (identifier) @variable)


(number) @number
(string) @string

(variable (identifier) @variable)
((variable (identifier) @function)
  (#match? @function ".+\\~$"))
((variable (identifier) @boolean)
 (#any-of? @boolean "true" "false"))
((variable (identifier) @constant.builtin)
 (#any-of? @constant.builtin
  "_" "after-chdir" "args" "before-chdir" "buildinfo" "nil"
  "notify-bg-job-success" "num-bg-jobs" "ok" "paths" "pid"
  "pwd" "value-out-indicator" "version"))

["$" "@"] @punctuation.special
["(" ")" "[" "]" "{" "}"] @punctuation.bracket
";" @punctuation.delimiter
