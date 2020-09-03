test:
	fish -c 'for file in tests/*.md; ./doctest.fish $$file; end'
