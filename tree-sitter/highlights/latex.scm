;; General syntax
(ERROR) @error

(command_name) @function
(caption
  command: _ @function)

(key_value_pair
  key: (_) @parameter
  value: (_))

[
 (line_comment)
 (block_comment)
 (comment_environment)
] @comment

((line_comment) @preproc
  (#lua-match? @preproc "^%% !TeX"))

[
 (brack_group)
 (brack_group_argc)
] @parameter

[(operator) "="] @operator

"\\item" @punctuation.special

((word) @punctuation.delimiter
(#eq? @punctuation.delimiter "&"))

["[" "]" "{" "}"] @punctuation.bracket ; "(" ")" has no syntactical meaning in LaTeX

;; General environments
(begin
 command: _ @text.environment
 name: (curly_group_text (text) @text.environment.name))

(end
 command: _ @text.environment
 name: (curly_group_text (text) @text.environment.name))

;; Definitions and references
(new_command_definition
 command: _ @function.macro
 declaration: (curly_group_command_name (_) @function))
(old_command_definition
 command: _ @function.macro
 declaration: (_) @function)
(let_command_definition
 command: _ @function.macro
 declaration: (_) @function)

(environment_definition
 command: _ @function.macro
 name: (curly_group_text (_) @text.reference))

(theorem_definition
 command: _ @function.macro
 name: (curly_group_text (_) @text.environment.name))

(paired_delimiter_definition
 command: _ @function.macro
 declaration: (curly_group_command_name (_) @function))

(label_definition
 command: _ @function.macro
 name: (curly_group_text (_) @text.reference))
(label_reference_range
 command: _ @function.macro
 from: (curly_group_text (_) @text.reference)
 to: (curly_group_text (_) @text.reference))
(label_reference
 command: _ @function.macro
 names: (curly_group_text_list (_) @text.reference))
(label_number
 command: _ @function.macro
 name: (curly_group_text (_) @text.reference)
 number: (_) @text.reference)

(citation
 command: _ @function.macro
 keys: (curly_group_text_list) @text.reference)

(glossary_entry_definition
 command: _ @function.macro
 name: (curly_group_text (_) @text.reference))
(glossary_entry_reference
 command: _ @function.macro
 name: (curly_group_text (_) @text.reference))

(acronym_definition
 command: _ @function.macro
 name: (curly_group_text (_) @text.reference))
(acronym_reference
 command: _ @function.macro
 name: (curly_group_text (_) @text.reference))

(color_definition
 command: _ @function.macro
 name: (curly_group_text (_) @text.reference))
(color_reference
 command: _ @function.macro
 name: (curly_group_text (_) @text.reference))

;; Math
[
 (displayed_equation)
 (inline_formula)
] @text.math

(math_environment
  (begin
   command: _ @text.math
   name: (curly_group_text (text) @text.math)))

(math_environment
  (text) @text.math)

(math_environment
  (end
   command: _ @text.math
   name: (curly_group_text (text) @text.math)))

;; Sectioning
(title_declaration
  command: _ @namespace
  options: (brack_group (_) @text.title.1)?
  text: (curly_group (_) @text.title.1))

(author_declaration
  command: _ @namespace
  authors: (curly_group_author_list
             ((author)+ @text.title.1)))

(chapter
  command: _ @namespace
  toc: (brack_group (_) @text.title.2)?
  text: (curly_group (_) @text.title.2))

(part
  command: _ @namespace
  toc: (brack_group (_) @text.title.2)?
  text: (curly_group (_) @text.title.2))

(section
  command: _ @namespace
  toc: (brack_group (_) @text.title.3)?
  text: (curly_group (_) @text.title.3))

(subsection
  command: _ @namespace
  toc: (brack_group (_) @text.title.4)?
  text: (curly_group (_) @text.title.4))

(subsubsection
  command: _ @namespace
  toc: (brack_group (_) @text.title.5)?
  text: (curly_group (_) @text.title.5))

(paragraph
  command: _ @namespace
  toc: (brack_group (_) @text.title.6)?
  text: (curly_group (_) @text.title.6))

(subparagraph
  command: _ @namespace
  toc: (brack_group (_) @text.title.6)?
  text: (curly_group (_) @text.title.6))

;; Beamer frames
(generic_environment
  (begin
    name: (curly_group_text
            (text) @text.environment.name)
    (#any-of? @text.environment.name "frame"))
  .
  (curly_group (_) @text.title))

((generic_command
  command: (command_name) @_name
  arg: (curly_group
          (text) @text.title))
 (#eq? @_name "\\frametitle"))

;; Formatting
((generic_command
  command: (command_name) @_name
  arg: (curly_group (_) @text.emphasis))
  (#eq? @_name "\\emph"))

((generic_command
  command: (command_name) @_name
  arg: (curly_group (_) @text.emphasis))
  (#match? @_name "^(\\\\textit|\\\\mathit)$"))

((generic_command
  command: (command_name) @_name
  arg: (curly_group (_) @text.strong))
  (#match? @_name "^(\\\\textbf|\\\\mathbf)$"))

((generic_command
  command: (command_name) @_name
  .
  arg: (curly_group (_) @text.uri))
 (#match? @_name "^(\\\\url|\\\\href)$"))

;; File inclusion commands
(class_include
  command: _ @include
  path: (curly_group_path) @string)

(package_include
  command: _ @include
  paths: (curly_group_path_list) @string)

(latex_include
  command: _ @include
  path: (curly_group_path) @string)
(import_include
  command: _ @include
  directory: (curly_group_path) @string
  file: (curly_group_path) @string)

(bibtex_include
  command: _ @include
  path: (curly_group_path) @string)
(biblatex_include
  "\\addbibresource" @include
  glob: (curly_group_glob_pattern) @string.regex)

(graphics_include
  command: _ @include
  path: (curly_group_path) @string)
(tikz_library_import
  command: _ @include
  paths: (curly_group_path_list) @string)

(text) @spell
(inline_formula) @nospell
(displayed_equation) @nospell
(key_value_pair) @nospell
(generic_environment
  begin: _ @nospell
  end: _ @nospell)
(citation
  keys: _ @nospell)
(command_name) @nospell
