#!/usr/bin/env fish
# doctest.fish - Test your documentation examples
# Made by Aurelio Jargas in September 2020

# Note that variables and functions are prefixed with double underscores
# to help mitigate name clash with user's own variables and functions
# that may be defined in their tests. This is necessary because we use
# `eval` to execute the user commands, bringing them into doctest.fish
# own execution environment.

set __my_url https://github.com/aureliojargas/doctest.fish
set __my_name doctest.fish
set __my_version dev

# Defaults
set __prefix '    '
set __prompt '> '
set __color_mode auto
set __use_color 0
set __verbose_level 0
set __quiet 0
set __yaml 0

# Global counters for aggregating results from all input files
set __total_tests 0
set __total_failed 0

function __printf_color # color template arguments
    test $__use_color -eq 1; and set_color $argv[1]
    printf $argv[2..-1]
    test $__use_color -eq 1; and set_color normal
end

function __error -a message
    set -l script_name (basename (status -f))
    __printf_color red '%s: Error: %s\n' $script_name $message >&2
    exit 1
end

function __starts_with -a pattern string
    test -z "$pattern"; and return 0 # empty pattern always matches
    test -z "$string"; and return 1 # empty string never matches
    set -l string_prefix (string sub -l (string length -- $pattern) -- $string)
    test "$string_prefix" = "$pattern"
end

function __show_version
    echo "$__my_name $__my_version"
end

function __show_help
    echo "usage: $__my_name [options] <file ...>"
    echo
    echo 'options:'
    echo '      --color WHEN      use colors or not? auto*, always, never'
    echo '      --prefix PREFIX   set the command line prefix (default: 4 spaces)'
    echo '      --prompt PROMPT   set the prompt string (default: "> ")'
    echo '  -q, --quiet           no output is shown (not even errors)'
    echo '  -v, --verbose         increase verbosity (cumulative)'
    echo '      --version         show the program version and exit'
    echo '      --yaml            show all test cases as YAML (no test is run)'
    echo '  -h, --help            show this help message and exit'
    echo
    echo "See also: $__my_url"
end

function __process_cmdline_arguments
    argparse --exclusive 'v,q' \
        'c-color=' \
        'x-prefix=' \
        'p-prompt=' \
        'q/quiet' \
        'v/verbose' \
        'V-version' \
        'y-yaml' \
        'h/help' \
        -- $argv
    or exit 1

    # Cumulative options
    set __verbose_level (count $_flag_verbose)

    # Options with arguments
    set -q _flag_color; and set __color_mode $_flag_color
    set -q _flag_prefix; and set __prefix $_flag_prefix
    set -q _flag_prompt; and set __prompt $_flag_prompt

    # On/off flags
    set -q _flag_quiet; and set __quiet 1
    set -q _flag_version; and __show_version; and exit 0
    set -q _flag_yaml; and set __yaml 1
    set -q _flag_help; and __show_help; and exit 0

    # Input files
    set --global __input_files $argv
end

function __setup_colors -a mode
    switch $mode
        case auto
            if isatty stdout
                set __use_color 1
            else
                set __use_color 0
            end
        case always yes
            set __use_color 1
        case never no
            set __use_color 0
        case '*'
            __error "Invalid --color mode '$mode'. Use: auto, always or never."
    end
end

function __validate_prompt -a string
    test -n "$string"
    or __error 'The prompt string cannot be empty, set it via --prompt'
end

function __validate_input_files -a paths
    test (count $paths) -eq 0
    and __error 'no test file informed'

    for path in $paths
        test -d "$path"; and __error "input file is a directory: $path"
        test -r "$path"; or __error "cannot read input file: $path"
    end
end

function __parse_input_file -a path
    set --local line_number 0
    set --local pending_output 0

    # The results will be saved in the $__parsed_data list. The format
    # `line_number:type:contents` is used because fish does not
    # support multidimensional lists. Example:
    #    3:cmd:true; echo $status
    #    4:out:0
    #    5:cmd:false; echo $status
    #    6:out:1
    #    7:cmd:echo "command output and status"; echo $status
    #    8:out:command output and status
    #    9:out:0
    set --global __parsed_data

    test $__verbose_level -ge 2
    and printf 'Parsing file %s\n' $path

    function __show_parsed_line -a line label message
        test $__verbose_level -lt 3; and return 0

        switch $label
            case command
                set message (__printf_color cyan '%s' $message)
            case output
                set message (__printf_color magenta '%s' $message)
        end
        printf '%4d %-7s [%s]\n' $line $label $message
    end

    # Adding extra empty "line" to the end of the input to make the
    # algorithm simpler. Then we always have a last-line trigger for the
    # last pending command. Otherwise we would have to handle the last
    # command after the loop.
    for line in (cat $path) ''
        set line_number (math $line_number + 1)

        if __starts_with $__command_id $line
            # Found a command line
            set --local cmd (string sub -s (math $__command_id_length + 1) -- $line)
            set --append __parsed_data "$line_number:cmd:$cmd"
            __show_parsed_line $line_number command $cmd
            set pending_output 1

        else if test "$line" = "$__command_id"; or test "$line" = "$__command_id_trimmed"
            # Line has prompt, but it is an empty command
            __show_parsed_line $line_number prompt $line
            set pending_output 0

        else if test "$pending_output" -eq 1; and __starts_with $__prefix $line
            # Line has the prefix and is not a command, so this is the
            # command output
            set --local out (string sub -s (math $__prefix_length + 1) -- $line)
            set --append __parsed_data "$line_number:out:$out"
            __show_parsed_line $line_number output $out

        else
            # Line is not a command neither command output
            __show_parsed_line $line_number other $line
            set pending_output 0
        end
    end

    test $__verbose_level -ge 2
    and printf 'Parsing finished, %d command/output lines found\n' \
        (count $__parsed_data)
end

function __test_input_file -a __input_file
    set --local __test_number 0
    set --local __failed_tests 0

    test $__verbose_level -ge 2
    and printf 'Testing commands from file %s\n' $__input_file

    # Adding extra empty "command" after $__parsed_data to make the
    # algorithm simpler. Then we always have a last-command trigger for
    # the last pending command. Otherwise we would have to handle the
    # last command after the loop.
    for __data in $__parsed_data '0:cmd:'
        test $__verbose_level -ge 3
        and printf '  [%s]\n' $__data

        string split --max 2 : $__data |
        read --line __line __type __text

        if test "$__type" = cmd

            # There's a pending previous command, test it now
            if test -n "$__command"
                set __test_number (math $__test_number + 1) # this file
                set __total_tests (math $__total_tests + 1) # global

                test $__verbose_level -ge 2
                and printf 'Running [%s], expecting [%s]\n' \
                    "$__command" \
                    (string join '\\n' $__expected)

                # Important: eval must be in the same execution scope
                # for all the tests in a single file. A var $foo defined
                # in a command should be visible to the next commands
                # from the same file, and it should not be visible for
                # the commands on the next file.
                true # reset $status to zero
                set __output (eval $__command 2>&1)

                if test "$__output" = "$__expected" # OK
                    test $__verbose_level -ge 1
                    and __printf_color green '%s:%d: [ ok ] %s\n' \
                        $__input_file $__line_number $__command

                else # FAIL
                    set __failed_tests (math $__failed_tests + 1) # this file
                    set __total_failed (math $__total_failed + 1) # global

                    if test $__quiet -eq 0
                        echo
                        __printf_color red '%s:%d: [fail] %s\n' \
                            $__input_file $__line_number $__command

                        # Show a nice diff
                        diff -u \
                            (printf '%s\n' $__expected | psub) \
                            (printf '%s\n' $__output | psub) |
                        sed '1,2 d' # delete ---/+++ headers
                        echo
                    end
                end
            end

            # Setup new command data
            set __line_number $__line
            set __command $__text
            set __expected

        else if test "$__type" = out
            set --append __expected $__text

        else
            __error "Unknown data type: $__type"
        end
    end
    __show_file_summary $__input_file $__test_number $__failed_tests

    test $__verbose_level -ge 2
    and printf 'Testing finished for file %s\n' $__input_file
end

function __show_file_summary -a path tested failed
    test $__quiet -eq 1; and return 0

    # Examples of output:
    #   docs/foo.md: No tests found
    #   docs/foo.md: 7 tests PASSED
    #   docs/foo.md: 3 of 7 tests FAILED
    printf '%s: ' $path

    if test $tested -eq 0
        echo 'No tests found'
    else
        if test $failed -eq 0
            printf '%d tests %s\n' \
                $tested \
                (__printf_color green PASSED)
        else
            printf '%d of %d tests %s\n' \
                $failed \
                $tested \
                (__printf_color red FAILED)
        end
    end
end

#-----------------------------------------------------------------------
# YAML

function __yaml_string -a text
    # https://www.yaml.info/learn/quote.html#single
    # foo'bar => 'foo''bar'
    printf "'%s'" (string replace --all "'" "''" $text)
end

function __yaml_root
    printf '%s: %s\n' prefix (__yaml_string $__prefix)
    printf '%s: %s\n' prompt (__yaml_string $__prompt)
    printf '%s: %s\n' version (__yaml_string (__show_version))
    printf '%s:\n' files
end

function __yaml_file_data # file data_list
    printf '  - path: %s\n' (__yaml_string $argv[1])
    printf '    tests:\n'

    for data in $argv[2..-1]
        string split --max 2 : $data | read --line line type text

        if test "$type" = cmd
            printf '      - line: %d\n' $line
            printf '        cmd: %s\n' (__yaml_string $text)
            printf '        out:\n'
        else
            printf '          - %s\n' (__yaml_string $text)
        end
    end
end

#-----------------------------------------------------------------------

__process_cmdline_arguments $argv
__setup_colors $__color_mode
__validate_prompt $__prompt
__validate_input_files $__input_files

# This will be the main identifier for commands
set __command_id $__prefix$__prompt
set __command_id_trimmed (string replace --regex ' +$' '' -- $__command_id)

# Pre-compute lengths and counts
set __prefix_length (string length -- $__prefix)
set __command_id_length (string length -- $__command_id)
set __input_files_count (count $__input_files)

# Maybe we only need to print the YAML?
if test "$__yaml" -eq 1
    __yaml_root
    for __input_file in $__input_files
        __parse_input_file $__input_file # set $__parsed_data
        __yaml_file_data $__input_file $__parsed_data
    end
    exit 0 # we're done
end

# Run all the tests from all the input files
for __input_file in $__input_files
    __parse_input_file $__input_file # set $__parsed_data
    __test_input_file $__input_file # use $__parsed_data
end

# Show final total status when there are at least 2 input files
# Examples of output:
#   Summary: 14 input files, no tests were found (check --prefix and --prompt)
#   Summary: 14 input files, 56 tests passed
#   Summary: 14 input files, 3 of 53 tests failed
if test $__quiet -eq 0; and test $__input_files_count -gt 1

    echo # visually separate from previous block

    echo -n "Summary: $__input_files_count input files, "

    if test $__total_tests -eq 0
        echo 'no tests were found (check --prefix and --prompt)'
    else if test $__total_failed -eq 0
        printf "%d tests %s\n" \
            $__total_tests \
            (__printf_color green passed)
    else
        printf "%d of %d tests %s\n" \
            $__total_failed \
            $__total_tests \
            (__printf_color red failed)
    end
end

# Script exit code will be zero only when there are no failed tests
test $__total_failed -eq 0
