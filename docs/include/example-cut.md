## The cut command

You can use the `cut` command to extract parts of a text,
using a delimiter:

    > set my_text 'foo:bar:baz'
    > echo $my_text
    foo:bar:baz
    > echo $my_text | cut -d : -f 1
    foo
    >
