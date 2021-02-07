function foo
    echo foo called
end

# foo
echo $argv
status current-filename
status current-command

# Detect if this script is being sourced
# Only call `foo` when not being sourced
test (status current-command) != "source"; and foo
