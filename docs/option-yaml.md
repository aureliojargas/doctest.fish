# Option --yaml

No tests are run when the `--yaml` option is used. Instead, all the parsed data for the test cases is printed to stdout in the YAML format. This information can then be consumed by other tools.

## Single input file

    > ./doctest.fish --yaml docs/include/one-ok.md
    prefix: '    '
    prompt: '> '
    version: 'doctest.fish dev'
    files:
      - path: 'docs/include/one-ok.md'
        tests:
          - line: 1
            cmd: 'echo foo'
            out:
              - 'foo'

## Multiple input files

    > ./doctest.fish --yaml docs/status.md docs/include/one-{ok,fail}.md
    prefix: '    '
    prompt: '> '
    version: 'doctest.fish dev'
    files:
      - path: 'docs/status.md'
        tests:
          - line: 5
            cmd: 'true; echo $status'
            out:
              - '0'
          - line: 7
            cmd: 'false; echo $status'
            out:
              - '1'
          - line: 9
            cmd: 'echo "command output and status"; echo $status'
            out:
              - 'command output and status'
              - '0'
          - line: 15
            cmd: 'false'
            out:
          - line: 16
            cmd: 'echo $status'
            out:
              - '0'
      - path: 'docs/include/one-ok.md'
        tests:
          - line: 1
            cmd: 'echo foo'
            out:
              - 'foo'
      - path: 'docs/include/one-fail.md'
        tests:
          - line: 1
            cmd: 'echo foo'
            out:
              - 'bar'
