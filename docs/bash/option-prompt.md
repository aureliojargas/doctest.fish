# Option --prompt

By default, when looking for command lines inside the input files, doctester.py expects all the commands to be preceded by the following prompt: `'$ '` (dollar sign followed by a single space).

You are free to use any other prompt identifier in your test files, just make sure you inform it via `--prompt` when calling doctester.py.

## Using a custom prompt

For example, there's a [docs/include/prompt-custom.md](../include/prompt-custom.md) example file in this repository that uses `prompt$` (followed by a space) as the custom prompt for the command lines. Here's its contents:

    prompt$ echo foo
    foo

When calling doctester.py on that file without specifying a custom prompt, no test will be found:

    $ python3 -m doctester docs/include/prompt-custom.md
    docs/include/prompt-custom.md: No commands found :(

The same happens if you specify a custom prompt that is not found in the test file:

    $ python3 -m doctester --prompt 404 docs/include/prompt-custom.md
    docs/include/prompt-custom.md: No commands found :(

So just make sure you are informing the correct prompt string in `--prompt` and the tests will be found:

    $ python3 -m doctester --prompt 'prompt$ ' docs/include/prompt-custom.md
    docs/include/prompt-custom.md: Found 1 commands. PASSED

## Trailing spaces

The trailing space in prompt identifiers is usual, but it is not required.

In [docs/include/prompt-no-space.md](../include/prompt-no-space.md) there's an example of a prompt which is just a single `$`, with no trailing space.

    $ python3 -m doctester --prompt '$' docs/include/prompt-no-space.md
    docs/include/prompt-no-space.md: Found 1 commands. PASSED

If you to have multiple trailing spaces in your prompt identifier, this is also allowed. The example in [docs/include/prompt-extra-spaces.md](../include/prompt-extra-spaces.md) uses three spaces after `>`:

    $ python3 -m doctester --prompt '$   ' docs/include/prompt-extra-spaces.md
    docs/include/prompt-extra-spaces.md: Found 1 commands. PASSED

## Empty prompt

Custom prompts are allowed, but you have to have something as a prompt identifier, otherwise doctester.py cannot find the command lines to be tested.

Trying to inform an empty prompt is an error:

    $ python3 -m doctester --prompt '' docs/include/prompt-custom.md
    doctester: Error: The prompt string cannot be empty, set it via --prompt

## See also

Note that when searching for commands to be tested, doctester.py tries to find a combination of `prefix+prompt`. Check the [--prefix option](option-prefix.md) to set a custom prefix.
