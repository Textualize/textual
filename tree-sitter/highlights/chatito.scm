;; Punctuation

[
 "%["
 "@["
 "~["
 "*["
 "]"
 "("
 ")"
] @punctuation.bracket

[":" ","] @punctuation.delimiter

(["\"" "'"] @punctuation.special @conceal
            (#set! conceal ""))

["%" "?" "#"] @character.special

;; Entities

(intent) @namespace

(slot) @type

(variation) @type.qualifier

(alias) @property

(number) @number

(argument
  key: (string) @label
  value: (string) @string)

(escape) @string.escape

;; Import

"import" @include

(file) @string.special

;; Text

(word) @text @spell

;; Comment

(comment) @comment @spell

;; Error

(ERROR) @error
