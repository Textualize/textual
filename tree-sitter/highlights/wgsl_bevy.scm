; inherits wgsl

[
 "virtual"
 "override"
] @keyword

[
 "#import"
 "#define_import_path"
 "as"
] @include

"::" @punctuation.delimiter

(function_declaration
  (import_path
    ((identifier) @function .)))

(import_path (identifier) @namespace (identifier))

(struct_declaration
    (preproc_ifdef (struct_member (variable_identifier_declaration (identifier) @field))))
(struct_declaration
    (preproc_ifdef
      (preproc_else (struct_member (variable_identifier_declaration (identifier) @field)))))

(preproc_ifdef
  name: (identifier) @constant.macro)

[
 "#ifdef"
 "#ifndef"
 "#endif"
 "#else"
] @preproc
