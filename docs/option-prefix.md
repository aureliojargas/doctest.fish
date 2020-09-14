# Option --prefix

By default, when looking for commands and output lines inside the input files, doctest.fish expects those special lines to be prefixed (indented) by four spaces. Example:

```markdown
This is a sample Markdown text. The following is a 4-spaces
indented code block, showing a command and its output:

    > echo foo
    foo

And there comes another paragraph.
```

You are free to use any other prefix in your test files (it's not limited to whitespace characters), or even no prefix at all, just make sure you inform it via `--prefix` when calling doctest.fish.

## Using a custom prefix

For example, there's a [docs/include/prefix-tab.md](include/prefix-tab.md) example file in this repository that uses a tab character (`\t`) as the custom prefix for the command lines.

When calling doctest.fish on that file without specifying a custom prefix, no test will be found:

    > ./doctest.fish docs/include/prefix-tab.md
    docs/include/prefix-tab.md: No tests found

The same happens if you specify a custom prefix that is not found in the test file:

    > ./doctest.fish --prefix '@@' docs/include/prefix-tab.md
    docs/include/prefix-tab.md: No tests found

So just make sure you are informing the correct prefix string in `--prefix` and the tests will be found:

    > ./doctest.fish --prefix \t docs/include/prefix-tab.md
    docs/include/prefix-tab.md: 1 tests PASSED

> Note that no quotes are used around `\t`, so Fish will correctly expand that to a tab character instead of `\` followed by a `t`.

## Empty prefix

It's valid to use an empty prefix for those cases when there's no indentation at all for the test commands. Markdown fenced blocks are an example.

    > ./doctest.fish --prefix '' docs/include/prefix-none.md
    docs/include/prefix-none.md: 1 tests PASSED

It's important to note that in this case, you must **always "close" the last command's output with a prompt**, otherwise doctest.fish has no way to know that this is the end of the output. Example:

```
> echo foo
foo
>
```

## See also

Note that when searching for commands to be tested, doctest.fish tries to find a combination of `prefix+prompt`. Check the [--prompt option](option-prompt.md) to set a custom prompt.
