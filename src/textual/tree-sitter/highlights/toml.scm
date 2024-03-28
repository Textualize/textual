; Properties
;-----------

(bare_key) @toml.type
(quoted_key) @string
(pair (bare_key)) @property

; Literals
;---------

(boolean) @boolean
(comment) @comment
(string) @string
(integer) @number
(float) @float
(offset_date_time) @toml.datetime
(local_date_time) @toml.datetime
(local_date) @toml.datetime
(local_time) @toml.datetime

; Punctuation
;------------

"." @punctuation.delimiter
"," @punctuation.delimiter

"=" @toml.operator

"[" @punctuation.bracket
"]" @punctuation.bracket
"[[" @punctuation.bracket
"]]" @punctuation.bracket
"{" @punctuation.bracket
"}" @punctuation.bracket

(ERROR) @toml.error
