## The cut command

You can use the `cut` command to extract parts of a text, using a delimiter:

```console
$ text='foo:bar:baz'
$ echo $text
foo:bar:baz
$ echo $text | cut -d : -f 1
foo2
$
```

'The' "End".

    $ text='foo:bar:baz'
    $ echo $text #comment
    foo:bar:baz
    $ echo $text | cut -d : -f 1
    foo3
    $
