(section_name
  (text) @type) ; consistency with toml
(comment) @comment

[
 "["
 "]"
] @punctuation.bracket

[
 "="
] @operator

(setting (setting_name) @property)
(setting_value) @text ; grammar does not support subtypes
(ERROR (setting_name) @text)
