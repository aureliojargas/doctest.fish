# Error output (stderr)

Please read the full documentation for error output in 
[docs/bash/stderr.md](../bash/stderr.md).

    $ python3 -m doctester
    doctester: Error: no test file informed
    $ python3 -m doctester; echo $status
    doctester: Error: no test file informed
    1
    $ echo this is stdout; echo this is stderr >&2
    this is stdout
    this is stderr
