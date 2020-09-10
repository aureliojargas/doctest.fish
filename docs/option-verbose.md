# Option --verbose

When using the verbose mode, extra messages are shown, listing all the executed tests.

    > ./doctest.fish -v docs/include/ok-fail.md | sed 's/^$/./'
    docs/include/ok-fail.md:1: [ ok ] echo ok-1
    docs/include/ok-fail.md:3: [ ok ] echo ok-2
    .
    docs/include/ok-fail.md:5: [fail] echo fail-3
    @@ -1 +1 @@
    -xxx
    +fail-3
    .
    docs/include/ok-fail.md:7: [ ok ] echo ok-4
    .
    docs/include/ok-fail.md:9: [fail] echo fail-5
    @@ -1 +1 @@
    -xxx
    +fail-5
    .
    .
    docs/include/ok-fail.md:11: [fail] echo fail-6
    @@ -1 +1 @@
    -xxx
    +fail-6
    .
    docs/include/ok-fail.md: 3 of 6 tests FAILED

> Note that `sed` was used to avoid having blank lines in the output, adding a dot to them. This is to avoid broken tests due the text editor's automatic removal of trailing spaces, that would remove the 4-space prefix from those blank output lines.
