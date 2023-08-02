; Types

(class_identifier
  (identifier) @type)

(primitive_type) @type.builtin

((class_identifier
   . (identifier) @_first @type.builtin
   (identifier) @type.builtin)
  (#any-of? @_first "android" "dalvik" "java" "kotlinx"))

((class_identifier
   . (identifier) @_first @type.builtin
   .  (identifier) @_second @type.builtin
   (identifier) @type.builtin)
  (#eq? @_first "com")
  (#any-of? @_second "android" "google"))

; Methods

(method_definition
  (method_signature (method_identifier) @method))

(expression
  (opcode) @_invoke
	(body
	  (full_method_signature
      (method_signature (method_identifier) @method.call)))
  (#lua-match? @_invoke "^invoke"))

(method_handle
  (full_method_signature
	(method_signature (method_identifier) @method.call)))

(custom_invoke
  . (identifier) @method.call
  (method_signature (method_identifier) @method.call))

(annotation_value
  (body
    (method_signature (method_identifier) @method.call)))

(annotation_value
  (body
    (full_method_signature
      (method_signature (method_identifier) @method.call))))

(field_definition
	(body
		(method_signature (method_identifier) @method.call)))

(field_definition
	(body
	  (full_method_signature
		  (method_signature (method_identifier) @method.call))))

((method_identifier) @constructor
  (#any-of? @constructor "<init>" "<clinit>"))

"constructor" @constructor

; Fields

[
  (field_identifier)
  (annotation_key)
] @field

((field_identifier) @constant
  (#lua-match? @constant "^[%u_]*$"))

; Variables

(variable) @variable.builtin

(local_directive
  (identifier) @variable)

; Parameters

(parameter) @parameter.builtin
(param_identifier) @parameter

; Labels

[
  (label)
  (jmp_label)
] @label

; Operators

(opcode) @keyword.operator

((opcode) @keyword.return
  (#lua-match? @keyword.return "^return"))

((opcode) @conditional
  (#lua-match? @conditional "^if"))

((opcode) @conditional
  (#lua-match? @conditional "^cmp"))

((opcode) @exception
  (#lua-match? @exception "^throw"))

((opcode) @comment
  (#eq? @comment "nop")) ; haha, anyone get it? ;)

[
  "="
  ".."
] @operator

; Keywords

[
  ".class"
  ".super"
  ".implements"
  ".field"
  ".end field"
  ".annotation"
  ".end annotation"
  ".subannotation"
  ".end subannotation"
  ".param"
  ".end param"
  ".parameter"
  ".end parameter"
  ".line"
  ".locals"
  ".local"
  ".end local"
  ".restart local"
  ".registers"
  ".packed-switch"
  ".end packed-switch"
  ".sparse-switch"
  ".end sparse-switch"
  ".array-data"
  ".end array-data"
  ".enum"
  (prologue_directive)
  (epilogue_directive)
] @keyword

[
  ".source"
] @include

[
  ".method"
  ".end method"
] @keyword.function

[
  ".catch"
  ".catchall"
] @exception

; Literals

(string) @string
(source_directive (string "\"" _ @text.uri "\""))
(escape_sequence) @string.escape

(character) @character

"L" @character.special

(number) @number

[
 (float)
 (NaN)
 (Infinity)
] @float

(boolean) @boolean

(null) @constant.builtin

; Misc

(annotation_visibility) @storageclass

(access_modifier) @type.qualifier

(array_type
  "[" @punctuation.special)

["{" "}"] @punctuation.bracket

["(" ")"] @punctuation.bracket

[
  "->"
  ","
  ":"
  ";"
  "@"
  "/"
] @punctuation.delimiter

(line_directive (number) @text.underline @text.literal)

; Comments

(comment) @comment @spell

(class_definition
  (comment) @comment.documentation)

; Errors

(ERROR) @error
