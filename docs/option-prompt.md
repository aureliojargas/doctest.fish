This file will run the tests for custom prompts defined in `docs/include/custom-prompt.md`.

When not specifying a custom prompt, no test will be found:

    > ./doctest.fish docs/include/custom-prompt.md
    docs/include/custom-prompt.md: No tests found

When using a custom prompt that is not found in the test file, it's ok:

    > ./doctest.fish --prompt 404 docs/include/custom-prompt.md
    docs/include/custom-prompt.md: No tests found

Now set a valid custom prompt. Only one test is using that prompt:

    > ./doctest.fish --prompt 'prompt$ ' docs/include/custom-prompt.md
    docs/include/custom-prompt.md: 1 tests PASSED

The same for a prompt with no trailing space:

    > ./doctest.fish --prompt '>' docs/include/custom-prompt.md
    docs/include/custom-prompt.md: 1 tests PASSED

The same for a prompt with multiple trailing spaces:

    > ./doctest.fish --prompt '@   ' docs/include/custom-prompt.md
    docs/include/custom-prompt.md: 1 tests PASSED

An empty prompt is an error:

    > ./doctest.fish --prompt '' docs/include/custom-prompt.md
    doctest.fish: Error: The prompt string cannot be empty, set it via --prompt
