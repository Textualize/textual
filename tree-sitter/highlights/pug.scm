(comment) @comment @spell

(tag_name) @tag
((tag_name) @constant.builtin
 ; https://www.script-example.com/html-tag-liste
 (#any-of? @constant.builtin
  "head" "title" "base" "link" "meta" "style"
  "body" "article" "section" "nav" "aside" "h1" "h2" "h3" "h4" "h5" "h6" "hgroup" "header" "footer" "address"
  "p" "hr" "pre" "blockquote" "ol" "ul" "menu" "li" "dl" "dt" "dd" "figure" "figcaption" "main" "div"
  "a" "em" "strong" "small" "s" "cite" "q" "dfn" "abbr" "ruby" "rt" "rp" "data" "time" "code" "var" "samp" "kbd" "sub" "sup" "i" "b" "u" "mark" "bdi" "bdo" "span" "br" "wbr"
  "ins" "del"
  "picture" "source" "img" "iframe" "embed" "object" "param" "video" "audio" "track" "map" "area"
  "table" "caption" "colgroup" "col" "tbody" "thead" "tfoot" "tr" "td" "th "
  "form" "label" "input" "button" "select" "datalist" "optgroup" "option" "textarea" "output" "progress" "meter" "fieldset" "legend"
  "details" "summary" "dialog"
  "script" "noscript" "template" "slot" "canvas"))

(id) @constant
(class) @property

(doctype) @preproc

(content) @none

(tag
  (attributes
    (attribute
      (attribute_name) @tag.attribute
      "=" @operator)))
((tag
   (attributes
     (attribute (attribute_name) @keyword)))
 (#match? @keyword "^(:|v-bind|v-|\\@)"))
(quoted_attribute_value) @string

(include (keyword) @include)
(extends (keyword) @include)
(filename) @string.special

(block_definition (keyword) @keyword)
(block_append (keyword)+ @keyword)
(block_prepend (keyword)+ @keyword)
(block_name) @type

(conditional (keyword) @conditional)
(case
  (keyword) @conditional
  (when (keyword) @conditional)+)

(each (keyword) @repeat)
(while (keyword) @repeat)

(mixin_use
  "+" @punctuation.delimiter
  (mixin_name) @function.call)
(mixin_definition
  (keyword) @keyword.function
  (mixin_name) @function)
(mixin_attributes
  (attribute_name) @parameter)

(filter
  ":" @punctuation.delimiter
  (filter_name) @method.call)
(filter
  (attributes
    (attribute (attribute_name) @parameter)))

[
 "(" ")"
 "#{" "}"
 ;; unsupported
 ; "!{"
 ; "#[" "]"
] @punctuation.bracket

[ "," "." "|" ] @punctuation.delimiter
(buffered_code "=" @punctuation.delimiter)
(unbuffered_code "-" @punctuation.delimiter)
(unescaped_buffered_code "!=" @punctuation.delimiter)
