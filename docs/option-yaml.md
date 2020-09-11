# Option --yaml

When using `--yaml`, instead of running the tests, all their data is printed to stdout in the YAML format. This information can then be used by other tools to act on the test data.

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
          - line: 3
            cmd: 'true; echo $status'
            out:
              - '0'
          - line: 5
            cmd: 'false; echo $status'
            out:
              - '1'
          - line: 7
            cmd: 'echo "command output and status"; echo $status'
            out:
              - 'command output and status'
              - '0'
          - line: 13
            cmd: 'false'
            out:
          - line: 14
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
