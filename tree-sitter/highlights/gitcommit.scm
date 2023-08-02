(comment) @comment
(generated_comment) @comment
(title) @text.title
(text) @text
(branch) @text.reference
(change) @keyword
(filepath) @text.uri
(arrow) @punctuation.delimiter

(subject) @text.title @spell
(subject (overflow) @text @spell)
(prefix (type) @keyword @nospell)
(prefix (scope) @parameter @nospell)
(prefix [
    "("
    ")"
    ":"
] @punctuation.delimiter)
(prefix [
    "!"
] @punctuation.special)

(message) @text @spell

(trailer (token) @label)
(trailer (value) @text)

(breaking_change (token) @text.warning)
(breaking_change (value) @text @spell)

(scissor) @comment

(ERROR) @error
