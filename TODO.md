## Fix variable clash bug

Since tests are run with `eval`, they can interfere with `doctest.fish` execution. For example, when a user test defines variables such as `$prefix` or `$failed_tests`.

One alternative is doing as `clitest` does: prefixing all the variables to avoid conflicts. It used `$tt_*`, but maybe `$__*` could be more readable.

This is implemented in the `variable-prefixes` branch.


## Readme

This flexibility on the prompt identifier can be handy if you need to
disambiguate when the document's formatting markup may conflict with the
prompts. For example, in Markdown, using `>` outside of a code block
means a quoted text. To avoid a quoted text being considered a command,
one alternative is always using the four spaces prefix to create code
blocks (as we do in doctest.fish documentation). Another alternative is
choosing a different prompt identifier.


## --first

- In multifile mode, will abort without processing all files.
- The ending summary line will be weird (or inexistent).


## Read from stdin

NO. Use `/dev/stdin`


## Support \ at EOL for multiline commands

NO

- Parser will get more complex.
- Will have to detect/validate incomplete commands.


## --prefix as regex

Useful to match both Markdown code blocks (4-space indented, non-indented fenced).

Or maybe a dedicated option `--prompt-regex`.

NO

- Parser will get more complex, having to remember the original prefix
- Will have to handle using a different prefix for the command and its output


## --skip

NO

- Test numbers are not used in the output, so `--skip 9` does not make sense
- Test numbers also do not fit well with multiple files


## --exclude, --ignore-file, --ignore-regex

Maybe.


## Unsupported commands

I have this implemented in the `unsupported-commands` branch.


# YAML, alternative

Using `type:` to specify the data type:

```yaml
- line: 1
  type: command
  content: "string match '?' a"
- line: 2
  type: output
  content:
    - "a"
    - "b"
```


## JSON

A generic JSON parser/generator wouldn't make sense because we can't map it to fish data (no dictionaries, no nested lists)

Maybe `string escape --style=json $content` would make sense at least.
