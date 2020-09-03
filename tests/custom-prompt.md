This file will run the tests for custom prompts defined in `tests/include/custom-prompt.md`.

When not specifying a custom prompt, no test will be found:

    > ./doctest.fish tests/include/custom-prompt.md
    tests/include/custom-prompt.md: No tests found

When using a custom prompt that is not found in the test file, it's ok:

    > ./doctest.fish --prompt 404 tests/include/custom-prompt.md
    tests/include/custom-prompt.md: No tests found

Now set a valid custom prompt. Only one test is using that prompt:

    > ./doctest.fish --prompt 'prompt$ ' tests/include/custom-prompt.md
    tests/include/custom-prompt.md: OK (1 tests passed)

The same for a prompt with no trailing space:

    > ./doctest.fish --prompt '>' tests/include/custom-prompt.md
    tests/include/custom-prompt.md: OK (1 tests passed)

The same for a prompt with multiple trailing spaces:

    > ./doctest.fish --prompt '@   ' tests/include/custom-prompt.md
    tests/include/custom-prompt.md: OK (1 tests passed)

An empty prompt is an error:

    > ./doctest.fish --prompt '' tests/include/custom-prompt.md
    doctest.fish: Error: The prompt string cannot be empty, set it via --prompt