; inherits: ecma,jsx

;;; Parameters
(formal_parameters (identifier) @parameter)

(formal_parameters
  (rest_pattern
    (identifier) @parameter))

;; ({ a }) => null
(formal_parameters
  (object_pattern
    (shorthand_property_identifier_pattern) @parameter))

;; ({ a = b }) => null
(formal_parameters
  (object_pattern
    (object_assignment_pattern
      (shorthand_property_identifier_pattern) @parameter)))

;; ({ a: b }) => null
(formal_parameters
  (object_pattern
    (pair_pattern
      value: (identifier) @parameter)))

;; ([ a ]) => null
(formal_parameters
  (array_pattern
    (identifier) @parameter))

;; ({ a } = { a }) => null
(formal_parameters
  (assignment_pattern
    (object_pattern
      (shorthand_property_identifier_pattern) @parameter)))

;; ({ a = b } = { a }) => null
(formal_parameters
  (assignment_pattern
    (object_pattern
      (object_assignment_pattern
        (shorthand_property_identifier_pattern) @parameter))))

;; a => null
(arrow_function
  parameter: (identifier) @parameter)

;; optional parameters
(formal_parameters
  (assignment_pattern
    left: (identifier) @parameter))

;; punctuation
(optional_chain) @punctuation.delimiter
