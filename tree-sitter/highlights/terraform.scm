; inherits: hcl

; Terraform specific references
;
;
; local/module/data/var/output
(expression (variable_expr (identifier) @variable.builtin (#any-of? @variable.builtin "data" "var" "local" "module" "output")) (get_attr (identifier) @field))

; path.root/cwd/module
(expression (variable_expr (identifier) @type.builtin (#eq? @type.builtin "path")) (get_attr (identifier) @variable.builtin (#any-of? @variable.builtin "root" "cwd" "module")))

; terraform.workspace
(expression (variable_expr (identifier) @type.builtin (#eq? @type.builtin "terraform")) (get_attr (identifier) @variable.builtin (#any-of? @variable.builtin "workspace")))

; Terraform specific keywords

; FIXME: ideally only for identifiers under a `variable` block to minimize false positives
((identifier) @type.builtin (#any-of? @type.builtin "bool" "string" "number" "object" "tuple" "list" "map" "set" "any"))
(object_elem val: (expression
  (variable_expr
    (identifier) @type.builtin (#any-of? @type.builtin "bool" "string" "number" "object" "tuple" "list" "map" "set" "any"))))
