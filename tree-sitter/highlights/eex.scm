[
  "%>"
  "--%>"
  "<%!--"
  "<%"
  "<%#"
  "<%%="
  "<%="
] @tag.delimiter

; EEx comments are highlighted as such
(comment) @comment

; Tree-sitter parser errors
(ERROR) @error
