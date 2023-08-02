[
  "require"
  "replace"
  "go"
  "exclude"
  "retract"
  "module"
] @keyword

"=>" @operator

(comment) @comment
(module_path) @text.uri

[
(version)
(go_version)
] @string
