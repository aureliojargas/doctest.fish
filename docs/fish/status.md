# Exit status

Please read the full documentation for exit status in 
[docs/bash/status.md](../bash/status.md).

    $ true; echo $status
    0
    $ false; echo $status
    1
    $ echo "command output and status"; echo $status
    command output and status
    0

It must be in the same line. This won't work:

    $ false
    $ echo $status
    0
