[ (line_comment) (block_comment) ] @comment

(label_decl) @label

(string) @string

(instruction opcode: _ @function.call)

[ "pins" "x" "y" "null" "isr" "osr" "osre" "status" "pc" "exec" ] @constant.builtin
(wait_source [ "irq" "gpio" "pin" ] @constant.builtin)

(out_target "pindirs" @constant.builtin)
(set_target "pindirs" @constant.builtin)
(directive "pindirs" @attribute)

(condition [ "--" "!=" ] @operator)
(expression [ "+" "-" "*" "/" "|" "&" "^" "::" ] @operator)
(not) @operator

[ (optional) (irq_modifiers) ] @type.qualifier

[ "block" "noblock" "rel" ] @attribute

[ "iffull" "ifempty" ] @conditional

"public" @storageclass

(integer) @number

(directive (identifier) @variable)
(directive (symbol_def (identifier) @variable))
(value (identifier) @variable)

(directive directive: _ @preproc)
