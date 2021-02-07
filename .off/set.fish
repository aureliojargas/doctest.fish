function foo
    set -g inside_foo 1
    echo "outside_foo is valid inside foo: $outside_foo"
end

set outside_foo 1
foo
echo "inside_foo: $inside_foo"
