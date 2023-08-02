; inherits: c

((identifier) @field
  (#lua-match? @field "^m?_.*$"))

(parameter_declaration
  declarator: (reference_declarator) @parameter)

; function(Foo ...foo)
(variadic_parameter_declaration
  declarator: (variadic_declarator
                (_) @parameter))
; int foo = 0
(optional_parameter_declaration
    declarator: (_) @parameter)

;(field_expression) @parameter ;; How to highlight this?

(((field_expression
     (field_identifier) @method)) @_parent
 (#has-parent? @_parent template_method function_declarator))

(field_declaration
  (field_identifier) @field)

(field_initializer
 (field_identifier) @property)

(function_declarator
  declarator: (field_identifier) @method)

(concept_definition
  name: (identifier) @type.definition)

(alias_declaration
  name: (type_identifier) @type.definition)

(auto) @type.builtin

(namespace_identifier) @namespace
((namespace_identifier) @type
  (#lua-match? @type "^[%u]"))

(case_statement
  value: (qualified_identifier (identifier) @constant))

(using_declaration . "using" . "namespace" . [(qualified_identifier) (identifier)] @namespace)

(destructor_name
  (identifier) @method)

; functions
(function_declarator
  (qualified_identifier
    (identifier) @function))
(function_declarator
  (qualified_identifier
    (qualified_identifier
      (identifier) @function)))
(function_declarator
  (qualified_identifier
    (qualified_identifier
      (qualified_identifier
        (identifier) @function))))
((qualified_identifier
  (qualified_identifier
    (qualified_identifier
      (qualified_identifier
        (identifier) @function)))) @_parent
  (#has-ancestor? @_parent function_declarator))

(function_declarator
  (template_function
    (identifier) @function))

(operator_name) @function
"operator" @function
"static_assert" @function.builtin

(call_expression
  (qualified_identifier
    (identifier) @function.call))
(call_expression
  (qualified_identifier
    (qualified_identifier
      (identifier) @function.call)))
(call_expression
  (qualified_identifier
    (qualified_identifier
      (qualified_identifier
        (identifier) @function.call))))
((qualified_identifier
  (qualified_identifier
    (qualified_identifier
      (qualified_identifier
        (identifier) @function.call)))) @_parent
  (#has-ancestor? @_parent call_expression))

(call_expression
  (template_function
    (identifier) @function.call))
(call_expression
  (qualified_identifier
    (template_function
      (identifier) @function.call)))
(call_expression
  (qualified_identifier
    (qualified_identifier
      (template_function
        (identifier) @function.call))))
(call_expression
  (qualified_identifier
    (qualified_identifier
      (qualified_identifier
        (template_function
          (identifier) @function.call)))))
((qualified_identifier
  (qualified_identifier
    (qualified_identifier
      (qualified_identifier
        (template_function
          (identifier) @function.call))))) @_parent
  (#has-ancestor? @_parent call_expression))

; methods
(function_declarator
  (template_method
    (field_identifier) @method))
(call_expression
  (field_expression
    (field_identifier) @method.call))

; constructors

((function_declarator
  (qualified_identifier
    (identifier) @constructor))
  (#lua-match? @constructor "^%u"))

((call_expression
  function: (identifier) @constructor)
(#lua-match? @constructor "^%u"))
((call_expression
  function: (qualified_identifier
              name: (identifier) @constructor))
(#lua-match? @constructor "^%u"))

((call_expression
  function: (field_expression
              field: (field_identifier) @constructor))
(#lua-match? @constructor "^%u"))

;; constructing a type in an initializer list: Constructor ():  **SuperType (1)**
((field_initializer
  (field_identifier) @constructor
  (argument_list))
 (#lua-match? @constructor "^%u"))


; Constants

(this) @variable.builtin
(null "nullptr" @constant.builtin)

(true) @boolean
(false) @boolean

; Literals

(raw_string_literal)  @string

; Keywords

[
 "try"
 "catch"
 "noexcept"
 "throw"
] @exception


[
 "class"
 "decltype"
 "explicit"
 "friend"
 "namespace"
 "override"
 "template"
 "typename"
 "using"
 "concept"
 "requires"
] @keyword

[
  "co_await"
] @keyword.coroutine

[
 "co_yield"
 "co_return"
] @keyword.coroutine.return

[
 "public"
 "private"
 "protected"
 "virtual"
 "final"
] @type.qualifier

[
 "new"
 "delete"

 "xor"
 "bitand"
 "bitor"
 "compl"
 "not"
 "xor_eq"
 "and_eq"
 "or_eq"
 "not_eq"
 "and"
 "or"
] @keyword.operator

"<=>" @operator

"::" @punctuation.delimiter

(template_argument_list
  ["<" ">"] @punctuation.bracket)

(template_parameter_list
  ["<" ">"] @punctuation.bracket)

(literal_suffix) @operator
