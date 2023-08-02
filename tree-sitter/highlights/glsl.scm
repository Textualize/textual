; inherits: c

[
  "in"
  "out"
  "inout"
  "uniform"
  "shared"
  "layout"
  "attribute"
  "varying"
  "buffer"
  "coherent"
  "readonly"
  "writeonly"
  "precision"
  "highp"
  "mediump"
  "lowp"
  "centroid"
  "sample"
  "patch"
  "smooth"
  "flat"
  "noperspective"
  "invariant"
  "precise"
] @type.qualifier

"subroutine" @keyword.function

(extension_storage_class) @storageclass

(
  (identifier) @variable.builtin
  (#match? @variable.builtin "^gl_")
)
