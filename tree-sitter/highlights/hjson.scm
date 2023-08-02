(true) @boolean
(false) @boolean
(null) @constant.builtin
(number) @number
(pair key: (string) @label)
(pair value: (string) @string)
(array (string) @string)
;  (string_content (escape_sequence) @string.escape)
(ERROR) @error
;  "," @punctuation.delimiter
"[" @punctuation.bracket
"]" @punctuation.bracket
"{" @punctuation.bracket
"}" @punctuation.bracket

(comment) @comment
