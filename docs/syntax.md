# Syntax gotchas

Those are some syntax edge cases, just to make sure the input file parser is working correctly.

## Not a test case

> A line with prompt but no prefix.

    A line with the expected prefix, but no prompt.

    >A line missing the required space after the prompt.

## Comment

When using a comment as a command, nothing happens:

    > # foo
    >


## Prompt alone

A prompt alone is a noop (even without the trailing space):

    >

Repeated prompts are a noop:

    >
    >
    >

A prompt after a command is a noop:

    > true
    >

A prompt after an output is a noop:

    > echo foo
    foo
    >

## Command or output at EOF

A command at the very end of the file is executed:

    > echo foo
    foo
