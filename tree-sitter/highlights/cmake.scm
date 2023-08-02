(normal_command
  (identifier)
  (argument_list
    (argument (unquoted_argument)) @constant
  )
  (#lua-match? @constant "^[%u@][%u%d_]+$")
)

[
 (quoted_argument)
 (bracket_argument)
] @string

(variable_ref) @none
(variable) @variable

[
 (bracket_comment)
 (line_comment)
] @comment @spell

(normal_command (identifier) @function)

["ENV" "CACHE"] @storageclass
["$" "{" "}" "<" ">"] @punctuation.special
["(" ")"] @punctuation.bracket

[
 (function)
 (endfunction)
 (macro)
 (endmacro)
] @keyword.function

[
 (if)
 (elseif)
 (else)
 (endif)
] @conditional

[
 (foreach)
 (endforeach)
 (while)
 (endwhile)
] @repeat

(normal_command
  (identifier) @repeat
  (#match? @repeat "\\c^(continue|break)$")
)
(normal_command
  (identifier) @keyword.return
  (#match? @keyword.return "\\c^return$")
)

(function_command
  (function)
  (argument_list
    . (argument) @function
    (argument)* @parameter
  )
)

(macro_command
  (macro)
  (argument_list
    . (argument) @function.macro
    (argument)* @parameter
  )
)

(block_def
  (block_command
    (block) @function.builtin
    (argument_list
      (argument (unquoted_argument) @constant)
    )
    (#any-of? @constant "SCOPE_FOR" "POLICIES" "VARIABLES" "PROPAGATE")
  )
  (endblock_command (endblock) @function.builtin)
)
;
((argument) @boolean
  (#match? @boolean "\\c^(1|on|yes|true|y|0|off|no|false|n|ignore|notfound|.*-notfound)$")
)
;
(if_command
  (if)
  (argument_list
    (argument) @keyword.operator
  )
  (#any-of? @keyword.operator "NOT" "AND" "OR"
                              "COMMAND" "POLICY" "TARGET" "TEST" "DEFINED" "IN_LIST"
                              "EXISTS" "IS_NEWER_THAN" "IS_DIRECTORY" "IS_SYMLINK" "IS_ABSOLUTE"
                              "MATCHES"
                              "LESS" "GREATER" "EQUAL" "LESS_EQUAL" "GREATER_EQUAL"
                              "STRLESS" "STRGREATER" "STREQUAL" "STRLESS_EQUAL" "STRGREATER_EQUAL"
                              "VERSION_LESS" "VERSION_GREATER" "VERSION_EQUAL" "VERSION_LESS_EQUAL" "VERSION_GREATER_EQUAL"
  )
)
(elseif_command
  (elseif)
  (argument_list
    (argument) @keyword.operator
  )
  (#any-of? @keyword.operator "NOT" "AND" "OR"
                              "COMMAND" "POLICY" "TARGET" "TEST" "DEFINED" "IN_LIST"
                              "EXISTS" "IS_NEWER_THAN" "IS_DIRECTORY" "IS_SYMLINK" "IS_ABSOLUTE"
                              "MATCHES"
                              "LESS" "GREATER" "EQUAL" "LESS_EQUAL" "GREATER_EQUAL"
                              "STRLESS" "STRGREATER" "STREQUAL" "STRLESS_EQUAL" "STRGREATER_EQUAL"
                              "VERSION_LESS" "VERSION_GREATER" "VERSION_EQUAL" "VERSION_LESS_EQUAL" "VERSION_GREATER_EQUAL"
  )
)

(normal_command
  (identifier) @function.builtin
  (#match? @function.builtin "\\c^(cmake_host_system_information|cmake_language|cmake_minimum_required|cmake_parse_arguments|cmake_path|cmake_policy|configure_file|execute_process|file|find_file|find_library|find_package|find_path|find_program|foreach|get_cmake_property|get_directory_property|get_filename_component|get_property|include|include_guard|list|macro|mark_as_advanced|math|message|option|separate_arguments|set|set_directory_properties|set_property|site_name|string|unset|variable_watch|add_compile_definitions|add_compile_options|add_custom_command|add_custom_target|add_definitions|add_dependencies|add_executable|add_library|add_link_options|add_subdirectory|add_test|aux_source_directory|build_command|create_test_sourcelist|define_property|enable_language|enable_testing|export|fltk_wrap_ui|get_source_file_property|get_target_property|get_test_property|include_directories|include_external_msproject|include_regular_expression|install|link_directories|link_libraries|load_cache|project|remove_definitions|set_source_files_properties|set_target_properties|set_tests_properties|source_group|target_compile_definitions|target_compile_features|target_compile_options|target_include_directories|target_link_directories|target_link_libraries|target_link_options|target_precompile_headers|target_sources|try_compile|try_run|ctest_build|ctest_configure|ctest_coverage|ctest_empty_binary_directory|ctest_memcheck|ctest_read_custom_files|ctest_run_script|ctest_sleep|ctest_start|ctest_submit|ctest_test|ctest_update|ctest_upload)$")
)

(normal_command
  (identifier) @_function
  (argument_list
    . (argument) @variable
  )
  (#match? @_function "\\c^set$")
)

(normal_command
  (identifier) @_function
  (#match? @_function "\\c^set$")
  (argument_list
    . (argument)
    (
    (argument) @_cache @storageclass
    .
    (argument) @_type @type
    (#any-of? @_cache "CACHE")
    (#any-of? @_type "BOOL" "FILEPATH" "PATH" "STRING" "INTERNAL")
    )
  )
)

(normal_command
  (identifier) @_function
  (#match? @_function "\\c^unset$")
  (argument_list
    . (argument)
    (argument) @storageclass
    (#any-of? @storageclass "CACHE" "PARENT_SCOPE")
  )
)

(normal_command
  (identifier) @_function
  (#match? @_function "\\c^list$")
  (argument_list
    . (argument) @constant
    (#any-of? @constant "LENGTH" "GET" "JOIN" "SUBLIST" "FIND")
    . (argument) @variable
    (argument) @variable .
  )
)
(normal_command
  (identifier) @_function
  (#match? @_function "\\c^list$")
  (argument_list
    . (argument) @constant
    . (argument) @variable
    (#any-of? @constant "APPEND" "FILTER" "INSERT"
                        "POP_BACK" "POP_FRONT" "PREPEND"
                        "REMOVE_ITEM" "REMOVE_AT" "REMOVE_DUPLICATES"
                        "REVERSE" "SORT")
  )
)
(normal_command
  (identifier) @_function
  (#match? @_function "\\c^list$")
  (argument_list
    . (argument) @_transform @constant
    . (argument) @variable
    . (argument) @_action @constant
    (#eq? @_transform "TRANSFORM")
    (#any-of? @_action "APPEND" "PREPEND" "TOUPPER" "TOLOWER" "STRIP" "GENEX_STRIP" "REPLACE")
  )
)
(normal_command
  (identifier) @_function
  (#match? @_function "\\c^list$")
  (argument_list
    . (argument) @_transform @constant
    . (argument) @variable
    . (argument) @_action @constant
    . (argument)? @_selector @constant
    (#eq? @_transform "TRANSFORM")
    (#any-of? @_action "APPEND" "PREPEND" "TOUPPER" "TOLOWER" "STRIP" "GENEX_STRIP" "REPLACE")
    (#any-of? @_selector "AT" "FOR" "REGEX")
  )
)
(normal_command
  (identifier) @_function
  (#match? @_function "\\c^list$")
  (argument_list
    . (argument) @_transform @constant
    (argument) @constant .
    (argument) @variable
    (#eq? @_transform "TRANSFORM")
    (#eq? @constant "OUTPUT_VARIABLE")
  )
)

(escape_sequence) @string.escape

((source_file . (line_comment) @preproc)
  (#lua-match? @preproc "^#!/"))
