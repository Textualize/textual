(None) @constant.builtin
(asset_path) @text.uri
(attribute_property) @property
(bool) @boolean
(comment) @comment @spell
(custom) @function.builtin
(float) @float
(integer) @number
(orderer) @function.call
(prim_path) @string.special
(relationship_type) @type
(string) @string
(uniform) @function.builtin
(variant_set_definition) @keyword

;; Prefer namespace highlighting, if any.
;;
;; e.g. `rel fizz` - `fizz` uses `@identifier`
;; e.g. `rel foo:bar:fizz` - `foo` and `bar` use `@namespace` and `fizz` uses `@identifier`
;;
(identifier) @variable
(namespace_identifier) @namespace
(namespace_identifier
  (identifier) @namespace
)

[
  "class"
  "def"
  "over"
] @keyword.function

["(" ")" "[" "]" "{" "}"] @punctuation.bracket
[":" ";" "."] @punctuation.delimiter

[
  "="
] @operator

(attribute_type) @type
(
 ;; Reference: https://openusd.org/release/api/sdf_page_front.html
 (attribute_type) @type.builtin
 (#any-of? @type.builtin
  ;; Scalar types
  "asset" "asset[]"
  "bool" "bool[]"
  "double" "double[]"
  "float" "float[]"
  "half" "half[]"
  "int" "int[]"
  "int64" "int64[]"
  "string" "string[]"
  "timecode" "timecode[]"
  "token" "token[]"
  "uchar" "uchar[]"
  "uint" "uint[]"
  "uint64" "uint64[]"

  ;; Dimensioned Types
  "double2" "double2[]"
  "double3" "double3[]"
  "double4" "double4[]"
  "float2" "float2[]"
  "float3" "float3[]"
  "float4" "float4[]"
  "half2" "half2[]"
  "half3" "half3[]"
  "half4" "half4[]"
  "int2" "int2[]"
  "int3" "int3[]"
  "int4" "int4[]"
  "matrix2d" "matrix2d[]"
  "matrix3d" "matrix3d[]"
  "matrix4d" "matrix4d[]"
  "quatd" "quatd[]"
  "quatf" "quatf[]"
  "quath" "quath[]"

  ;; Extra Types
  "color3f" "color3f[]"
  "normal3f" "normal3f[]"
  "point3f" "point3f[]"
  "texCoord2f" "texCoord2f[]"
  "vector3d" "vector3d[]"
  "vector3f" "vector3f[]"
  "vector3h" "vector3h[]"

  "dictionary"

  ;; Deprecated Types
  "EdgeIndex" "EdgeIndex[]"
  "FaceIndex" "FaceIndex[]"
  "Matrix4d" "Matrix4d[]"
  "PointIndex" "PointIndex[]"
  "PointFloat" "PointFloat[]"
  "Transform" "Transform[]"
  "Vec3f" "Vec3f[]"
 )
)

(
 (identifier) @keyword
 (#any-of? @keyword

  ;; Reference: https://openusd.org/release/api/sdf_page_front.html
  ;; LIVRPS names
  "inherits"
  "payload"
  "references"
  "specializes"
  "variantSets"
  "variants"

  ; assetInfo names
  "assetInfo"
  "identifier"
  "name"
  "payloadAssetDependencies"
  "version"

  ;; clips names
  "clips"

  "active"
  "assetPaths"
  "manifestAssetPath"
  "primPath"
  "templateAssetPath"
  "templateEndTime"
  "templateStartTime"
  "templateStride"
  "times"

  ;; customData names
  "customData"

  "apiSchemaAutoApplyTo"
  "apiSchemaOverridePropertyNames"
  "className"
  "extraPlugInfo"
  "isUsdShadeContainer"
  "libraryName"
  "providesUsdShadeConnectableAPIBehavior"
  "requiresUsdShadeEncapsulation"
  "skipCodeGeneration"

  ;; Layer metadata names
  "colorConfiguration"
  "colorManagementSystem"
  "customLayerData"
  "defaultPrim"
  "doc"
  "endTimeCode"
  "framesPerSecond"
  "owner"
  "startTimeCode"
  "subLayers"

  ;; Prim metadata
  "instanceable"
 )
)

;; Common attribute metadata
(
 (layer_offset
  (identifier) @keyword
  (#any-of? @keyword

   "offset"
   "scale"
  )
 )
)

;; Docstrings in USD
(metadata
 (comment)*
 (string) @comment.documentation
)
