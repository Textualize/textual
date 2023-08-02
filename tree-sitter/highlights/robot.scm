(argument (dictionary_variable) @string.special)
(argument (list_variable) @string.special)
(argument (scalar_variable) @string.special)
(argument (text_chunk) @string)

(keyword_invocation (keyword) @function)

(test_case_definition (name) @property)

(keyword_definition (body (keyword_setting) @keyword))
(keyword_definition (name) @function)

(variable_definition (variable_name) @variable)

(setting_statement) @keyword

(extra_text) @comment
(section_header) @keyword

(ellipses) @punctuation.delimiter
(comment) @comment
