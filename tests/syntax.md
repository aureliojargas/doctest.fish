# Some syntax gotchas for the test file parser

Not a command:

> A line with prompt but no prefix.

    A line with the expected prefix, but no prompt.

    >A line missing the required space after the prompt.

A comment as a command, nothing happens:

    > # foo
    >

An empty prompt alone is a noop (even without the trailing space):

    >

Repeated empty prompts are a noop:

    >
    >
    >

An empty prompt after a command is a noop:

    > true
    >

An empty prompt after an output is a noop:

    > echo foo
    foo
    >

A command at the end of the file is executed:

    > echo foo
    foo
