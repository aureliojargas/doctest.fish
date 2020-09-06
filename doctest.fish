#!/usr/bin/env fish
# doctest.fish, by Aurelio Jargas

set my_name doctest.fish
set my_url https://github.com/aureliojargas/doctest.fish

# Defaults
set prefix '    '
set prompt '> '
set color_mode auto
set use_color 0
set debug_level 0
set verbose 0
set quiet 0

# Global counters for aggregating results from all input files
set total_tests 0
set total_failed 0

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

function show_help
    echo "usage: $my_name [options] <file ...>"
    echo
    echo 'options:'
    echo '      --color WHEN      use colors or not? auto*, always, never'
    echo '      --prefix PREFIX   set the command line prefix (default: 4 spaces)'
    echo '      --prompt PROMPT   set the prompt string (default: "> ")'
    echo '  -q, --quiet           no output is shown (not even errors)'
    echo '  -v, --verbose         show information about every executed test'
    echo '  -h, --help            show this help message and exit'
    echo
    echo "See also: $my_url"
end

function process_cmdline_arguments
    argparse --exclusive 'v,q' \
        'c-color=' \
        'd-debug' \
        'x-prefix=' \
        'p-prompt=' \
        'q/quiet' \
        'v/verbose' \
        'h/help' \
        -- $argv
    or exit 1
    set debug_level (count $_flag_debug) # undocumented dev option
    set -q _flag_color; and set color_mode $_flag_color
    set -q _flag_prefix; and set prefix $_flag_prefix
    set -q _flag_prompt; and set prompt $_flag_prompt
    set -q _flag_quiet; and set quiet 1
    set -q _flag_verbose; and set verbose 1
    set -q _flag_help; and show_help; and exit 0
    set --global input_files $argv
end

function setup_colors -a mode
    switch $mode
        case auto
            if isatty stdout
                set use_color 1
            else
                set use_color 0
            end
        case always yes
            set use_color 1
        case never no
            set use_color 0
        case '*'
            error "Invalid --color mode '$mode'. Use: auto, always or never."
    end
end

function validate_prompt -a prompt
    test -n "$prompt"
    or error 'The prompt string cannot be empty, set it via --prompt'
end

function validate_input_files -a paths
    test (count $paths) -eq 0
    and error 'no test file informed'

    for path in $paths
        test -d "$path"; and error "input file is a directory: $path"
        test -r "$path"; or error "cannot read input file: $path"
    end
end

function test_input_file -a input_file
    set line_number 0
    set test_number 0
    set failed_tests 0

    # Adding extra empty "line" to the end of the input to make the
    # algorithm simpler. Then we always have a last-line trigger for the
    # last pending command. Otherwise we would have to handle the last
    # command after the loop.
    for line in (cat $input_file) ''

        set line_number (math $line_number + 1)
        set run_test 0

        debug yellow '?' $line_number $line

        # Parse the current input line
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
            set test_number (math $test_number + 1) # this file
            set total_tests (math $total_tests + 1) # global

            # These must be global, see comments in show_diff
            set --global expected $current_output
            set --global output (eval $current_command 2>&1)

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
                set failed_tests (math $failed_tests + 1) # this file
                set total_failed (math $total_failed + 1) # global
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

    # Show results (when not quiet)
    # Examples of output:
    #   tests/foo.md: No tests found
    #   tests/foo.md: 7 tests PASSED
    #   tests/foo.md: 3 of 7 tests FAILED
    if test $quiet -eq 0
        printf '%s: ' $input_file

        if test $test_number -eq 0
            echo 'No tests found'
        else
            if test $failed_tests -eq 0
                printf '%d tests %s\n' \
                    $test_number \
                    (printf_color green PASSED)
            else
                printf '%d of %d tests %s\n' \
                    $failed_tests \
                    $test_number \
                    (printf_color red FAILED)
            end
        end
    end
end

#-----------------------------------------------------------------------

process_cmdline_arguments $argv
setup_colors $color_mode
validate_prompt $prompt
validate_input_files $input_files

# This will be the main identifier for commands
set command_id $prefix$prompt
set command_id_trimmed (string replace --regex ' +$' '' -- $command_id)

# Pre-compute lengths and counts
set prefix_length (string length -- $prefix)
set command_id_length (string length -- $command_id)
set input_files_count (count $input_files)

# Run all the tests from all the input files
for input_file in $input_files
    test_input_file $input_file
end

# Show final total status when there are at least 2 input files
# Examples of output:
#   Summary: 14 input files, no tests were found (check --prefix and --prompt)
#   Summary: 14 input files, 56 tests passed
#   Summary: 14 input files, 3 of 53 tests failed
if test $quiet -eq 0; and test $input_files_count -gt 1

    echo # visually separate from previous block

    echo -n "Summary: $input_files_count input files, "

    if test $total_tests -eq 0
        echo 'no tests were found (check --prefix and --prompt)'
    else if test $total_failed -eq 0
        printf "%d tests %s\n" \
            $total_tests \
            (printf_color green passed)
    else
        printf "%d of %d tests %s\n" \
            $total_failed \
            $total_tests \
            (printf_color red failed)
    end
end

# Script exit code will be zero only when there are no failed tests
test $total_failed -eq 0
