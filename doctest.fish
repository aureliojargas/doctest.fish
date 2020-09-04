#!/usr/bin/env fish

# Defaults
set prefix '    '
set prompt '> '
set color_mode auto
set use_color 0
set debug_level 0
set verbose 0
set quiet 0

function printf_color # color template arguments
    test $use_color -eq 1; and set_color $argv[1]
    printf $argv[2..-1]
    test $use_color -eq 1; and set_color normal
end

function error -a message
    set -l script_name (basename (status -f))
    printf_color red '%s: Error: %s\n' $script_name $message >&2
    exit 1
end

function debug -a color id line message
    test $debug_level -gt 0
    and printf_color $color 'Line %d: %s [%s]\n' $line $id $message
end

function starts_with -a pattern string
    test -z "$pattern"; and return 0 # empty pattern always matches
    test -z "$string"; and return 1 # empty string never matches
    set -l string_prefix (string sub -l (string length -- $pattern) -- $string)
    test "$string_prefix" = "$pattern"
end

function show_diff
    # Getting $expected and $output from the outer scope because I
    # cannot pass two lists to a function (there's the automatic list
    # conversion for multiline strings)
    diff -u (printf '%s\n' $expected | psub) (printf '%s\n' $output | psub) |
    sed '1 { /^--- / { N; /\n+++ /d; }; }' # no ---/+++ headers
end

function process_cmdline_arguments
    argparse --exclusive 'v,q' \
        'v/verbose' \
        'q/quiet' \
        'd-debug' \
        'x-prefix=' \
        'p-prompt=' \
        'c-color=' \
        -- $argv
    or exit 1
    set debug_level (count $_flag_debug)
    set -q _flag_prefix; and set prefix $_flag_prefix
    set -q _flag_prompt; and set prompt $_flag_prompt
    set -q _flag_color; and set color_mode $_flag_color
    set -q _flag_verbose; and set verbose 1
    set -q _flag_quiet; and set quiet 1
    set --global input_file $argv[1]
end

function setup_colors -a mode
    switch $mode
        case auto
            not test -t 1 # status=0 when stdout is not a terminal
            set use_color $status
        case never no
            set use_color 0
        case always yes
            set use_color 1
        case '*'
            error "Invalid --color mode '$mode'. Use: auto, always or never."
    end
end

function validate_prompt -a prompt
    test -n "$prompt"
    or error 'The prompt string cannot be empty, set it via --prompt'
end

function validate_input_file -a path
    test -n "$path"; or error 'no test file informed'
    test -d "$path"; and error "input file is a directory: $path"
    test -r "$path"; or error "cannot read input file: $path"
end

#-----------------------------------------------------------------------

process_cmdline_arguments $argv
setup_colors $color_mode
validate_prompt $prompt
validate_input_file $input_file

# This will be the main identifier for commands
set command_id $prefix$prompt
set command_id_trimmed (string replace --regex ' +$' '' -- $command_id)

# Pre-compute lengths to be used inside the main loop
set prefix_length (string length -- $prefix)
set command_id_length (string length -- $command_id)

set line_number 0
set test_number 0
set total_failed 0

# Adding extra empty "line" to the end of the input to make the
# algorithm simpler. Then we always have a last-line trigger for the
# last pending command. Otherwise we would have to handle the last
# command after the loop.
for line in (cat $input_file) ''

    set line_number (math $line_number + 1)
    set run_test 0

    debug yellow '?' $line_number $line

    if starts_with $command_id $line
        # Found a command line

        set next_command (string sub -s (math $command_id_length + 1) -- $line)
        set next_command_line_number $line_number

        debug blue COMMAND $line_number $next_command

        if set -q current_command
            set run_test 1
        else
            set current_command $next_command
            set current_command_line_number $line_number
            set --erase next_command
            set --erase next_command_line_number
        end

    else if test "$line" = "$command_id" || test "$line" = "$command_id_trimmed"
        # Line has prompt, but it is an empty command

        set -q current_command && set run_test 1

    else if test -n "$current_command$next_command" && starts_with $prefix $line
        # Line has the prefix and is not a command, so this is the
        # command output

        set output_line (string sub -s (math $prefix_length + 1) -- $line)
        set --append current_output $output_line

        debug cyan OUTPUT $line_number $output_line

    else
        # Line is not a command neither command output

        set -q current_command && set run_test 1

        debug magenta OTHER $line_number $line
    end


    # Run the current test
    if test $run_test -eq 1
        set test_number (math $test_number + 1)
        set expected $current_output
        set output (eval $current_command 2>&1)

        # ^ Here (eval) is where the command is really executed.
        # Note: eval cannot be inside a function due to scope rules. A
        #       defined foo var should be accessible by the next tests.

        if test "$output" = "$expected"
            # OK
            test $verbose -eq 1
            and printf_color green '%s:%d: [ ok ] %s\n' \
                $input_file $current_command_line_number $current_command

        else
            # FAIL
            set total_failed (math $total_failed + 1)
            if test $quiet -eq 0
                echo
                printf_color red '%s:%d: [fail] %s\n' \
                    $input_file $current_command_line_number $current_command
                show_diff (string collect -- $expected) (string collect -- $output)
                echo
            end
        end

        # Clear data from the already executed test
        set --erase current_command
        set --erase current_command_line_number
        set --erase current_output

        # If there's a pending command, make it the current one
        # (it will be tested only when the next trigger appears)
        if set -q next_command
            set current_command $next_command
            set current_command_line_number $next_command_line_number
            set --erase next_command
            set --erase next_command_line_number
        end
    end
end

if test $quiet -eq 0
    # Examples of output:
    # tests/foo.md: No tests found
    # tests/foo.md: OK (7 tests passed)
    # tests/foo.md: FAIL (4 tests passed, 3 failed)

    # The filename is always shown in the line beginning, regardless of
    # the final test results
    printf '%s: ' $input_file

    if test $test_number -eq 0
        echo 'No tests found'
    else
        if test $total_failed -eq 0
            printf_color green 'OK (%d tests passed%s)\n' \
                $test_number
        else
            printf_color red 'FAILED (%d tests passed, %d failed%s)\n' \
                (math $test_number - $total_failed) \
                $total_failed
        end
    end
end

# Script exit code will be zero only when there are no failed tests
test $total_failed -eq 0
