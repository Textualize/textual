(comment) @comment @spell

(conditional
 (_ [
  "ifeq"
  "else"
  "ifneq"
  "ifdef"
  "ifndef"
 ] @conditional)
 "endif" @conditional)

(rule (targets
       (word) @function.builtin
       (#any-of? @function.builtin
        ".DEFAULT"
        ".SUFFIXES"
        ".DELETE_ON_ERROR"
        ".EXPORT_ALL_VARIABLES"
        ".IGNORE"
        ".INTERMEDIATE"
        ".LOW_RESOLUTION_TIME"
        ".NOTPARALLEL"
        ".ONESHELL"
        ".PHONY"
        ".POSIX"
        ".PRECIOUS"
        ".SECONDARY"
        ".SECONDEXPANSION"
        ".SILENT"
        ".SUFFIXES")))

(rule ["&:" ":" "::"] @operator)

(export_directive "export" @keyword)
(override_directive "override" @keyword)
(include_directive ["include" "-include"] @include)

(variable_assignment
 name: (word) @symbol
 [
  "?="
  ":="
  "::="
; ":::="
  "+="
  "="
 ] @operator)

(shell_assignment
 name: (word) @symbol
 "!=" @operator)

(define_directive
 "define" @keyword
 name: (word) @symbol
 [
  "="
  ":="
  "::="
; ":::="
  "?="
  "!="
 ]? @operator
 "endef" @keyword)

(variable_assignment
 (word) @variable.builtin (#any-of? @variable.builtin
  ".DEFAULT_GOAL"
  ".EXTRA_PREREQS"
  ".FEATURES"
  ".INCLUDE_DIRS"
  ".RECIPEPREFIX"
  ".SHELLFLAGS"
  ".VARIABLES"
  "MAKEARGS"
  "MAKEFILE_LIST"
  "MAKEFLAGS"
  "MAKE_RESTARTS"
  "MAKE_TERMERR"
  "MAKE_TERMOUT"
  "SHELL"
 ))

; Use string to match bash
(variable_reference (word) @string) @operator

(shell_function
 ["$" "(" ")"] @operator
 "shell" @function.builtin)

(function_call ["$" "(" ")"] @operator)
(substitution_reference ["$" "(" ")"] @operator)

(function_call [
 "subst"
 "patsubst"
 "strip"
 "findstring"
 "filter"
 "filter-out"
 "sort"
 "word"
 "words"
 "wordlist"
 "firstword"
 "lastword"
 "dir"
 "notdir"
 "suffix"
 "basename"
 "addsuffix"
 "addprefix"
 "join"
 "wildcard"
 "realpath"
 "abspath"
 "error"
 "warning"
 "info"
 "origin"
 "flavor"
 "foreach"
 "if"
 "or"
 "and"
 "call"
 "eval"
 "file"
 "value"
 ] @function.builtin)
