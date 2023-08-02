; Keywords

(scheme) @keyword

; Methods

(method) @method

; Constants

(const_spec) @constant

; Variables

(identifier) @variable

; Fields

(pair name: (identifier) @field)

; Parameters

(query_param (key) @parameter)

; Operators

[
  "="
  "?"
  "&"
  "@"
] @operator

; Literals

(string) @string

(target_url) @string @text.uri

(number) @number

; (boolean) @boolean

(null) @constant.builtin

; Punctuation

[ "{{" "}}" ] @punctuation.bracket

[
  ":"
] @punctuation.delimiter

; Comments

(comment) @comment @spell

; Errors

(ERROR) @error
