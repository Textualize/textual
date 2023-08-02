; ; Intended for consumption by nvim-treesitter
; ; Default capture names for nvim-treesitter found here:
; ; https://github.com/nvim-treesitter/nvim-treesitter/blob/e473630fe0872cb0ed97cd7085e724aa58bc1c84/lua/nvim-treesitter/highlight.lua#L14-L104
; ; In this file, captures defined later take precedence over captures defined earlier

; Keywords
[
  "ACTION"
  "ASSUME"
  "ASSUMPTION"
  "AXIOM"
  "BY"
  "CASE"
  "CHOOSE"
  "CONSTANT"
  "CONSTANTS"
  "COROLLARY"
  "DEF"
  "DEFINE"
  "DEFS"
  "DOMAIN"
  "ELSE"
  "ENABLED"
  "EXCEPT"
  "EXTENDS"
  "HAVE"
  "HIDE"
  "IF"
  "IN"
  "INSTANCE"
  "LAMBDA"
  "LEMMA"
  "LET"
  "LOCAL"
  "MODULE"
  "NEW"
  "OBVIOUS"
  "OMITTED"
  "ONLY"
  "OTHER"
  "PICK"
  "PROOF"
  "PROPOSITION"
  "PROVE"
  "QED"
  "RECURSIVE"
  "SF_"
  "STATE"
  "SUBSET"
  "SUFFICES"
  "TAKE"
  "TEMPORAL"
  "THEN"
  "THEOREM"
  "UNCHANGED"
  "UNION"
  "USE"
  "VARIABLE"
  "VARIABLES"
  "WF_"
  "WITH"
  "WITNESS"
  (address)
  (all_map_to)
  (assign)
  (case_arrow)
  (case_box)
  (def_eq)
  (exists)
  (forall)
  (gets)
  (label_as)
  (maps_to)
  (set_in)
  (temporal_exists)
  (temporal_forall)
] @keyword

;  Pluscal keywords
[
  (pcal_algorithm_start)
  "algorithm"
  "assert"
  "begin"
  "call"
  "define"
  "end"
  "fair"
  "goto"
  "macro"
  "or"
  "procedure"
  "process"
  "skip"
  "variable"
  "variables"
  "when"
  "with"
] @keyword
[
  "await"
] @keyword.coroutine
(pcal_with ("=") @keyword)
(pcal_process ("=") @keyword)
[
  "if"
  "then"
  "else"
  "elsif"
  (pcal_end_if)
  "either"
  (pcal_end_either)
] @conditional
[
  "while"
  "do"
  (pcal_end_while)
  "with"
  (pcal_end_with)
] @repeat
("return") @keyword.return
("print") @function.macro


; Literals
(binary_number (format) @keyword)
(binary_number (value) @number)
(boolean) @boolean
(boolean_set) @type
(hex_number (format) @keyword)
(hex_number (value) @number)
(int_number_set) @type
(nat_number) @number
(nat_number_set) @type
(octal_number (format) @keyword)
(octal_number (value) @number)
(real_number) @number
(real_number_set) @type
(string) @string
(escape_char) @string.escape
(string_set) @type

; Namespaces
(extends (identifier_ref) @namespace)
(instance (identifier_ref) @namespace)
(module name: (identifier) @namespace)
(pcal_algorithm name: (identifier) @namespace)

; Operators, functions, and macros
(bound_infix_op symbol: (_) @operator)
(bound_nonfix_op symbol: (_) @operator)
(bound_postfix_op symbol: (_) @operator)
(bound_prefix_op symbol: (_) @operator)
((prefix_op_symbol) @operator)
((infix_op_symbol) @operator)
((postfix_op_symbol) @operator)
(function_definition name: (identifier) @function)
(module_definition name: (_) @include)
(operator_definition name: (_) @function.macro)
(pcal_macro_decl name: (identifier) @function.macro)
(pcal_macro_call name: (identifier) @function.macro)
(pcal_proc_decl name: (identifier) @function.macro)
(pcal_process name: (identifier) @function)
(recursive_declaration (identifier) @function.macro)
(recursive_declaration (operator_declaration name: (_) @function.macro))

; Constants and variables
(constant_declaration (identifier) @constant)
(constant_declaration (operator_declaration name: (_) @constant))
(pcal_var_decl (identifier) @variable)
(pcal_with (identifier) @parameter)
((".") . (identifier) @attribute)
(record_literal (identifier) @attribute)
(set_of_records (identifier) @attribute)
(variable_declaration (identifier) @variable)

; Parameters
(choose (identifier) @parameter)
(choose (tuple_of_identifiers (identifier) @parameter))
(lambda (identifier) @parameter)
(module_definition (operator_declaration name: (_) @parameter))
(module_definition parameter: (identifier) @parameter)
(operator_definition (operator_declaration name: (_) @parameter))
(operator_definition parameter: (identifier) @parameter)
(pcal_macro_decl parameter: (identifier) @parameter)
(pcal_proc_var_decl (identifier) @parameter)
(quantifier_bound (identifier) @parameter)
(quantifier_bound (tuple_of_identifiers (identifier) @parameter))
(unbounded_quantification (identifier) @parameter)

; Delimiters
[
  (langle_bracket)
  (rangle_bracket)
  (rangle_bracket_sub)
  "{"
  "}"
  "["
  "]"
  "]_"
  "("
  ")"
] @punctuation.bracket
[
  ","
  ":"
  "."
  "!"
  ";"
  (bullet_conj)
  (bullet_disj)
  (prev_func_val)
  (placeholder)
] @punctuation.delimiter

; Proofs
(assume_prove (new (identifier) @parameter))
(assume_prove (new (operator_declaration name: (_) @parameter)))
(assumption name: (identifier) @constant)
(pick_proof_step (identifier) @parameter)
(proof_step_id "<" @punctuation.bracket)
(proof_step_id (level) @label)
(proof_step_id (name) @label)
(proof_step_id ">" @punctuation.bracket)
(proof_step_ref "<" @punctuation.bracket)
(proof_step_ref (level) @label)
(proof_step_ref (name) @label)
(proof_step_ref ">" @punctuation.bracket)
(take_proof_step (identifier) @parameter)
(theorem name: (identifier) @constant)

; Comments and tags
(block_comment "(*" @comment)
(block_comment "*)" @comment)
(block_comment_text) @comment
(comment) @comment
(single_line) @comment
(_ label: (identifier) @label)
(label name: (_) @label)
(pcal_goto statement: (identifier) @label)

; Reference highlighting with the same color as declarations.
; `constant`, `operator`, and others are custom captures defined in locals.scm
((identifier_ref) @constant (#is? @constant constant))
((identifier_ref) @function (#is? @function function))
((identifier_ref) @function.macro (#is? @function.macro macro))
((identifier_ref) @include (#is? @include import))
((identifier_ref) @parameter (#is? @parameter parameter))
((identifier_ref) @variable (#is? @variable var))
((prefix_op_symbol) @constant (#is? @constant constant))
((prefix_op_symbol) @function.macro (#is? @function.macro macro))
((prefix_op_symbol) @parameter (#is? @parameter parameter))
((infix_op_symbol) @constant (#is? @constant constant))
((infix_op_symbol) @function.macro (#is? @function.macro macro))
((infix_op_symbol) @parameter (#is? @parameter parameter))
((postfix_op_symbol) @constant (#is? @constant constant))
((postfix_op_symbol) @function.macro (#is? @function.macro macro))
((postfix_op_symbol) @parameter (#is? @parameter parameter))
(bound_prefix_op symbol: (_) @constant (#is? @constant constant))
(bound_prefix_op symbol: (_) @function.macro (#is? @function.macro macro))
(bound_prefix_op symbol: (_) @parameter (#is? @parameter parameter))
(bound_infix_op symbol: (_) @constant (#is? @constant constant))
(bound_infix_op symbol: (_) @function.macro (#is? @function.macro macro))
(bound_infix_op symbol: (_) @parameter (#is? @parameter parameter))
(bound_postfix_op symbol: (_) @constant (#is? @constant constant))
(bound_postfix_op symbol: (_) @function.macro (#is? @function.macro macro))
(bound_postfix_op symbol: (_) @parameter (#is? @parameter parameter))
(bound_nonfix_op symbol: (_) @constant (#is? @constant constant))
(bound_nonfix_op symbol: (_) @function.macro (#is? @function.macro macro))
(bound_nonfix_op symbol: (_) @parameter (#is? @parameter parameter))
