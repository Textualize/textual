[
  (local_var)
  (global_var)
] @variable

(type) @type
(type_keyword) @type.builtin

(type [
    (local_var)
    (global_var)
  ] @type)

(global_type
  (local_var) @type.definition)

(argument) @parameter

(_ inst_name: _ @keyword.operator)

[
  "catch"
  "filter"
] @keyword.operator

[
  "to"
  "nuw"
  "nsw"
  "exact"
  "unwind"
  "from"
  "cleanup"
  "swifterror"
  "volatile"
  "inbounds"
  "inrange"
] @keyword
(icmp_cond) @keyword
(fcmp_cond) @keyword

(fast_math) @keyword

(_ callee: _ @function)
(function_header name: _ @function)

[
  "declare"
  "define"
] @keyword.function
(calling_conv) @keyword.function

[
  "target"
  "triple"
  "datalayout"
  "source_filename"
  "addrspace"
  "blockaddress"
  "align"
  "syncscope"
  "within"
  "uselistorder"
  "uselistorder_bb"
  "module"
  "asm"
  "sideeffect"
  "alignstack"
  "inteldialect"
  "unwind"
  "type"
  "global"
  "constant"
  "externally_initialized"
  "alias"
  "ifunc"
  "section"
  "comdat"
  "any"
  "exactmatch"
  "largest"
  "nodeduplicate"
  "samesize"
  "distinct"
  "attributes"
  "vscale"
] @keyword


[
  "no_cfi"
  (dso_local)
  (linkage_aux)
  (visibility)
] @type.qualifier

[
  "thread_local"
  "localdynamic"
  "initialexec"
  "localexec"
  (unnamed_addr)
  (dll_storage_class)
] @storageclass

(attribute_name) @attribute

(function_header [
    (linkage)
    (calling_conv)
    (unnamed_addr)
  ] @keyword.function)

(number) @number
(comment) @comment
(string) @string
(cstring) @string
(label) @label
(_ inst_name: "ret" @keyword.return)
(float) @float

[
  (struct_value)
  (array_value)
  (vector_value)
] @constructor

[
  "("
  ")"
  "["
  "]"
  "{"
  "}"
  "<"
  ">"
  "<{"
  "}>"
] @punctuation.bracket

[
  ","
  ":"
] @punctuation.delimiter

[
  "="
  "|"
  "x"
  "..."
] @operator

[
  "true"
  "false"
] @boolean

[
  "undef"
  "poison"
  "null"
  "none"
  "zeroinitializer"
] @constant.builtin

(ERROR) @error
