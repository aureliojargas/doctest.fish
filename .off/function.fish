function foo -a one two rest
    echo $one
    echo $two
    echo $rest
    echo $argv
end

function foo2
    echo $argv[1]
    echo $argv[2]
    echo $argv[3..-1]
end

foo 1 2 3 4 5 6
# foo2 1 2 3 4 5 6


#--------------------------------------
# Make a function receive two lists as arguments
# And treat them as lists
set list1 1 2 3
set list2 4 5 6

function foo3 -a l1 l2
    echo "l1: $l1"
    echo "l2: $l2"
end
foo3 $list1 $list2
# Expected:
#   l1: 1 2 3
#   l2: 4 5 6
# Got:
#   l1: 1
#   l2: 2

function foo4 --no-scope-shadowing -a l1 l2
    echo "l1: $$l1"
    echo "l2: $$l2"
end
foo4 list1 list2 # works (hacky)
