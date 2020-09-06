# Option --help

    > ./doctest.fish -h | head -n 1; echo $status
    usage: doctest.fish [options] <file ...>
    0
    > ./doctest.fish --help | head -n 1; echo $status
    usage: doctest.fish [options] <file ...>
    0
