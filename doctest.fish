#!/usr/bin/env fish
# doctest.fish, by Aurelio Jargas

set my_name doctest.fish
set my_version dev
set my_url https://github.com/aureliojargas/doctest.fish

# Defaults
set prefix '    '
set prompt '> '
set color_mode auto
set use_color 0
set debug_level 0
set verbose 0
set quiet 0
set yaml 0

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

function show_version
    echo "$my_name $my_version"
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
    echo '  -V, --version         show the program version and exit'
    echo '      --yaml            show all test cases as YAML (no test is run)'
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
        'V/version' \
        'y-yaml' \
        'h/help' \
        -- $argv
    or exit 1
    set debug_level (count $_flag_debug) # undocumented dev option
    set -q _flag_color; and set color_mode $_flag_color
    set -q _flag_prefix; and set prefix $_flag_prefix
    set -q _flag_prompt; and set prompt $_flag_prompt
    set -q _flag_quiet; and set quiet 1
    set -q _flag_verbose; and set verbose 1
    set -q _flag_version; and show_version; and exit 0
    set -q _flag_yaml; and set yaml 1
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

function parse_input_file -a input_file
    set --local line_number 0
    set --local pending_output 0

    # The results will be saved in the $parsed_data list. The format
    # `line_number:type:contents` is used because fish does not
    # support multidimensional lists. Example:
    #    3:cmd:true; echo $status
    #    4:out:0
    #    5:cmd:false; echo $status
    #    6:out:1
    #    7:cmd:echo "command output and status"; echo $status
    #    8:out:command output and status
    #    9:out:0
    set --global parsed_data

    # Adding extra empty "line" to the end of the input to make the
    # algorithm simpler. Then we always have a last-line trigger for the
    # last pending command. Otherwise we would have to handle the last
    # command after the loop.
    for line in (cat $input_file) ''

        set line_number (math $line_number + 1)
        debug yellow '?' $line_number $line

        if starts_with $command_id $line
            # Found a command line
            set --local cmd (string sub -s (math $command_id_length + 1) -- $line)
            set --append parsed_data "$line_number:cmd:$cmd"
            debug blue COMMAND $line_number $cmd
            set pending_output 1

        else if test "$line" = "$command_id"; or test "$line" = "$command_id_trimmed"
            # Line has prompt, but it is an empty command
            debug blue EMPTY $line_number ''
            set pending_output 0

        else if test "$pending_output" -eq 1; and starts_with $prefix $line
            # Line has the prefix and is not a command, so this is the
            # command output
            set --local out (string sub -s (math $prefix_length + 1) -- $line)
            set --append parsed_data "$line_number:out:$out"
            debug cyan OUTPUT $line_number $out

        else
            # Line is not a command neither command output
            debug magenta OTHER $line_number $line
            set pending_output 0
        end
    end
end

function test_input_file -a input_file
    set --local test_number 0
    set --local failed_tests 0

    # Adding extra empty "command" after $parsed_data to make the
    # algorithm simpler. Then we always have a last-command trigger for
    # the last pending command. Otherwise we would have to handle the
    # last command after the loop.
    for data in $parsed_data '0:cmd:'
        test $debug_level -gt 0; and printf_color magenta '[%s]\n' $data

        string split --max 2 : $data | read --line line type text

        if test "$type" = cmd

            # There's a pending previous command, test it now
            if test -n "$command"
                set test_number (math $test_number + 1) # this file
                set total_tests (math $total_tests + 1) # global

                # Important: eval must be in the same execution scope
                # for all the tests in a single file. A var $foo defined
                # in a command should be visible to the next commands
                # from the same file, and it should not be visible for
                # the commands on the next file.
                set output (eval $command 2>&1)

                if test "$output" = "$expected" # OK
                    test $verbose -eq 1
                    and printf_color green '%s:%d: [ ok ] %s\n' \
                        $input_file $line_number $command

                else # FAIL
                    set failed_tests (math $failed_tests + 1) # this file
                    set total_failed (math $total_failed + 1) # global

                    if test $quiet -eq 0
                        echo
                        printf_color red '%s:%d: [fail] %s\n' \
                            $input_file $line_number $command

                        # Show a nice diff
                        diff -u \
                            (printf '%s\n' $expected | psub) \
                            (printf '%s\n' $output | psub) |
                        sed '1,2 d' # delete ---/+++ headers
                        echo
                    end
                end
            end

            # Setup new command data
            set line_number $line
            set command $text
            set expected

        else if test "$type" = out
            set --append expected $text

        else
            error "Unknown data type: $type"
        end
    end
    show_file_summary $input_file $test_number $failed_tests
end

function show_file_summary -a file tested failed
    test $quiet -eq 1; and return 0

    # Examples of output:
    #   tests/foo.md: No tests found
    #   tests/foo.md: 7 tests PASSED
    #   tests/foo.md: 3 of 7 tests FAILED
    printf '%s: ' $file

    if test $tested -eq 0
        echo 'No tests found'
    else
        if test $failed -eq 0
            printf '%d tests %s\n' \
                $tested \
                (printf_color green PASSED)
        else
            printf '%d of %d tests %s\n' \
                $failed \
                $tested \
                (printf_color red FAILED)
        end
    end
end

#-----------------------------------------------------------------------
# YAML

function yaml_string -a text
    # https://www.yaml.info/learn/quote.html#single
    # foo'bar => 'foo''bar'
    printf "'%s'" (string replace --all "'" "''" $text)
end

function yaml_root
    printf '%s: %s\n' prefix (yaml_string $prefix)
    printf '%s: %s\n' prompt (yaml_string $prompt)
    printf '%s: %s\n' version (yaml_string (show_version))
    printf '%s:\n' files
end

function yaml_file_data # file data_list
    printf '  - path: %s\n' (yaml_string $argv[1])
    printf '    tests:\n'

    for data in $argv[2..-1]
        string split --max 2 : $data | read --line line type text

        if test "$type" = cmd
            printf '      - line: %d\n' $line
            printf '        cmd: %s\n' (yaml_string $text)
            printf '        out:\n'
        else
            printf '          - %s\n' (yaml_string $text)
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

# Maybe we only need to print the YAML?
if test "$yaml" -eq 1
    yaml_root
    for input_file in $input_files
        parse_input_file $input_file # set $parsed_data
        yaml_file_data $input_file $parsed_data
    end
    exit 0 # we're done
end

# Run all the tests from all the input files
for input_file in $input_files
    parse_input_file $input_file # set $parsed_data
    test_input_file $input_file # use $parsed_data
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
