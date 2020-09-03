Using a tab as a prefix:

	> echo foo
	foo

Using no prefix. In this case, you must always "close" the last command's output with an empty prompt, otherwise doctest.fish has no way to know that this is the end of the output.

> echo foo
foo
>
