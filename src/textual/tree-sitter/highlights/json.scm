[
 (true)
 (false)
] @boolean

(null) @json.null

(number) @number

(pair key: (string) @json.label)
(pair value: (string) @string)

(array (string) @string)

(string_content) @spell

(ERROR) @json.error

["," ":"] @punctuation.delimiter

[
 "[" "]"
 "{" "}"
] @punctuation.bracket

(("\"" @conceal)
 (#set! conceal ""))

(escape_sequence) @string.escape
((escape_sequence) @conceal
 (#eq? @conceal "\\\"")
 (#set! conceal "\""))
