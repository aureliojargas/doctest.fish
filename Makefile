test: test-python test-fish test-bash

test-bash:
	./doctester.py docs/bash/*.md

# Hack to test everything in the fish shell. It's necessary since most
# of the tests have a `./doctest.py` call inside them, and there's no
# easy way to change it to `./doctest.py --shell fish`, so we hack the
# original Python script to make fish the default shell.
test-fish:
	cp doctester.py doctester.py.orig.$$$$; \
	sed -i'.bak' -e 's/default="bash",/default="fish",/' doctester.py; \
	./doctester.py docs/fish/*.md docs/bash/syntax.md; \
	mv doctester.py.orig.$$$$ doctester.py; \
	rm doctester.py.bak

test-python:
	# python3 -m unittest test_doctester.py
	python3 -m unittest discover -s tests/
