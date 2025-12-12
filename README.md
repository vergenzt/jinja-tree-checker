# jinja-tree-checker

AST type checker for Jinja templates and macros

## Vision

```toml
# file: pyproject.toml

[project]
name = "my-project-which-uses-jinja"
...

[dependency-groups]
dev = [
  "jinja-tree-checker",
  "tree-sitter-sql",  # https://github.com/DerekStride/tree-sitter-sql
]

[tool.jinja-tree-checker]
tree-sitter-grammar = "sql"
files = ["**/*.sql"]
```

```jinja-sql
# file: macros/fizzbuzz.sql
{%- macro fizzbuzz(n) %}
  {#-
  @param n: sql._expression
  @return sql._expression
  -#}
  coalesce(
    nullif(
      case {{n}} % 3 when 0 then 'Fizz' else '' end ||
      case {{n}} % 5 when 0 then 'Buzz' else '' end,
      ''
    ),
    {{n}}::text
  )
{%- endmacro %}
```

```jinja-sql
# file: models/fizzbuzz.sql
select
  {{ fizzbuzz('n') }}
from
  generate_series(1, 100) as nums(n)
```

```console
$ jinja-tree-checker
No issues found
```

```diff
 # file: macros/fizzbuzz.sql
 {%- macro fizzbuzz(n) %}
   {#-
   @param n: sql._expression
   @return sql._expression
   -#}
   coalesce(
     nullif(
       case {{n}} % 3 when 0 then 'Fizz' else '' end ||
       case {{n}} % 5 when 0 then 'Buzz' else '' end,
       ''
     ),
     {{n}}::text
-  )
+  ) as fizzbuzz_result
 {%- endmacro %}
```

```console
$ jinja-tree-checker
syntax error: macros/fizzbuzz.sql:13:5: unexpected keyword `as` for return type `sql._expression`, expected: END
```

```diff
 # file: macros/fizzbuzz.sql
 {%- macro fizzbuzz(n) %}
   {#-
   @param n: sql._expression
-  @return sql._expression
+  @return sql.select_expression  # one or more columns with or without aliases
   -#}
   coalesce(
     nullif(
       case {{n}} % 3 when 0 then 'Fizz' else '' end ||
       case {{n}} % 5 when 0 then 'Buzz' else '' end,
       ''
     ),
     {{n}}::text
   ) as fizzbuzz_result
 {%- endmacro %}
```

```console
$ jinja-tree-checker
No issues found
```