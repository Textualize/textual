; inherits: ecma

"require" @include

(import_require_clause source: (string) @text.uri)

[
  "declare"
  "enum"
  "export"
  "implements"
  "interface"
  "type"
  "namespace"
  "override"
  "module"
  "asserts"
  "infer"
  "is"
] @keyword

[
  "keyof"
  "satisfies"
] @keyword.operator

(as_expression "as" @keyword.operator)
(export_statement "as" @keyword.operator)
(mapped_type_clause "as" @keyword.operator)

[
  "abstract"
  "private"
  "protected"
  "public"
  "readonly"
] @type.qualifier

; types

(type_identifier) @type
(predefined_type) @type.builtin

(import_statement "type"
  (import_clause
    (named_imports
      ((import_specifier
          name: (identifier) @type)))))

(template_literal_type) @string

(non_null_expression "!" @operator)

;; punctuation

(type_arguments
  ["<" ">"] @punctuation.bracket)

(type_parameters
  ["<" ">"] @punctuation.bracket)

(object_type
  ["{|" "|}"] @punctuation.bracket)

(union_type
  "|" @punctuation.delimiter)

(intersection_type
  "&" @punctuation.delimiter)

(type_annotation
  ":" @punctuation.delimiter)

(type_predicate_annotation
  ":" @punctuation.delimiter)

(index_signature
  ":" @punctuation.delimiter)

(omitting_type_annotation
  "-?:" @punctuation.delimiter)

(opting_type_annotation
  "?:" @punctuation.delimiter)

"?." @punctuation.delimiter

(abstract_method_signature "?" @punctuation.special)
(method_signature "?" @punctuation.special)
(method_definition "?" @punctuation.special)
(property_signature "?" @punctuation.special)
(optional_parameter "?" @punctuation.special)
(optional_type "?" @punctuation.special)
(public_field_definition [ "?" "!" ] @punctuation.special)
(flow_maybe_type "?" @punctuation.special)

(template_type ["${" "}"] @punctuation.special)

(conditional_type ["?" ":"] @conditional.ternary)

; Variables

(undefined) @variable.builtin

;;; Parameters
(required_parameter (identifier) @parameter)
(optional_parameter (identifier) @parameter)

(required_parameter
  (rest_pattern
    (identifier) @parameter))

;; ({ a }) => null
(required_parameter
  (object_pattern
    (shorthand_property_identifier_pattern) @parameter))

;; ({ a = b }) => null
(required_parameter
  (object_pattern
    (object_assignment_pattern
      (shorthand_property_identifier_pattern) @parameter)))

;; ({ a: b }) => null
(required_parameter
  (object_pattern
    (pair_pattern
      value: (identifier) @parameter)))

;; ([ a ]) => null
(required_parameter
  (array_pattern
    (identifier) @parameter))

;; a => null
(arrow_function
  parameter: (identifier) @parameter)

;; global declaration
(ambient_declaration "global" @namespace)

;; function signatures
(ambient_declaration
  (function_signature
    name: (identifier) @function))

;; method signatures
(method_signature name: (_) @method)

;; property signatures
(property_signature
  name: (property_identifier) @method
  type: (type_annotation
          [
            (union_type (parenthesized_type (function_type)))
            (function_type)
          ]))
