# doctester.py - Test your documentation examples

Make sure all your command line examples work as documented.

![](docs/include/all-passed.png)

## Testable documentation

You write something like the following in your documentation.

> To do X, please run the following command:
> ```console
> > some-command --option "foo"
> command output
> more command output
> >
> ```


> ## The cut command
> You can use the `cut` command to extract parts of a text, using a delimiter:
> ```console
> > set text 'foo:bar:baz'  
> > echo $text
> foo:bar:baz
> > echo $text | cut -d : -f 1
> foo
> >
> ```

Wouldn't it be nice if some tool could scan your documentation, detect the `some-command --option "foo"` command mentioned on it, run that command in the fish shell and check if the output is exactly as documented? That's what `doctester.py` does.

For example, this very repository have all its documentation automatically tested for correctness, using the following command:

    ./doctester.py --prompt '> ' docs/*.md

## Features

- Use any textual format (Markdown, reST, HTML, plain text) for the [input files](docs/input-file.md)
- You can test both stdout and [stderr output](docs/stderr.md)
- You can also check the [command's exit status](docs/status.md) (`$?`)
- All the commands inside an input file share the same execution environment (i.e., [defined variables are preserved](docs/variables-1.md))

## Usage

Click the option name to read its (testable) documentation.

<pre>
usage: doctester.py [options] &lt;<a href="docs/input-file.md">file</a> ...&gt;

options:
      <a href="docs/option-color.md">--color</a> WHEN      use colors or not? auto*, always, never
      <a href="docs/option-prefix.md">--prefix</a> PREFIX   set the command line prefix (default: 4 spaces)
      <a href="docs/option-prompt.md">--prompt</a> PROMPT   set the prompt string (default: "&gt; ")
  -q, <a href="docs/option-quiet.md">--quiet</a>           no output is shown (not even errors)
  -v, <a href="docs/option-verbose.md">--verbose</a>         increase verbosity (cumulative)
      <a href="docs/option-version.md">--version</a>         show the program version and exit
      <a href="docs/option-yaml.md">--yaml</a>            show all test cases as YAML (no test is run)
  -h, <a href="docs/option-help.md">--help</a>            show this help message and exit
</pre>
