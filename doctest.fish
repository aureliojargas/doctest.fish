#!/usr/bin/env fish
# doctest.fish, by Aurelio Jargas

set ___my_name doctest.fish
set ___my_version dev
set ___my_url https://github.com/aureliojargas/doctest.fish

# Defaults
set ___prefix '    '
set ___prompt '> '
set ___color_mode auto
set ___use_color 0
set ___verbose_level 0
set ___quiet 0
set ___yaml 0

# Global counters for aggregating results from all input files
set ___total_tests 0
set ___total_failed 0

function ___printf_color # color template arguments
    test $___use_color -eq 1; and set_color $argv[1]
    printf $argv[2..-1]
    test $___use_color -eq 1; and set_color normal
end

function ___error -a message
    set -l script_name (basename (status -f))
    ___printf_color red '%s: Error: %s\n' $script_name $message >&2
    exit 1
end

function ___starts_with -a pattern string
    test -z "$pattern"; and return 0 # empty pattern always matches
    test -z "$string"; and return 1 # empty string never matches
    set -l string_prefix (string sub -l (string length -- $pattern) -- $string)
    test "$string_prefix" = "$pattern"
end

function ___show_version
    echo "$___my_name $___my_version"
end

function ___show_help
    echo "usage: $___my_name [options] <file ...>"
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
    echo "See also: $___my_url"
end

function ___process_cmdline_arguments
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
    set ___verbose_level (count $_flag_verbose)

    # Options with arguments
    set -q _flag_color; and set ___color_mode $_flag_color
    set -q _flag_prefix; and set ___prefix $_flag_prefix
    set -q _flag_prompt; and set ___prompt $_flag_prompt

    # On/off flags
    set -q _flag_quiet; and set ___quiet 1
    set -q _flag_version; and ___show_version; and exit 0
    set -q _flag_yaml; and set ___yaml 1
    set -q _flag_help; and ___show_help; and exit 0

    # Input files
    set --global ___input_files $argv
end

function ___setup_colors -a mode
    switch $mode
        case auto
            if isatty stdout
                set ___use_color 1
            else
                set ___use_color 0
            end
        case always yes
            set ___use_color 1
        case never no
            set ___use_color 0
        case '*'
            ___error "Invalid --color mode '$mode'. Use: auto, always or never."
    end
end

function ___validate_prompt -a string
    test -n "$string"
    or ___error 'The prompt string cannot be empty, set it via --prompt'
end

function ___validate_input_files -a paths
    test (count $paths) -eq 0
    and ___error 'no test file informed'

    for path in $paths
        test -d "$path"; and ___error "input file is a directory: $path"
        test -r "$path"; or ___error "cannot read input file: $path"
    end
end

function ___parse_input_file -a path
    set --local line_number 0
    set --local pending_output 0

    # The results will be saved in the $___parsed_data list. The format
    # `line_number:type:contents` is used because fish does not
    # support multidimensional lists. Example:
    #    3:cmd:true; echo $status
    #    4:out:0
    #    5:cmd:false; echo $status
    #    6:out:1
    #    7:cmd:echo "command output and status"; echo $status
    #    8:out:command output and status
    #    9:out:0
    set --global ___parsed_data

    test $___verbose_level -ge 2
    and printf 'Parsing file %s\n' $path

    function ___show_parsed_line -a line label message
        test $___verbose_level -lt 3; and return 0

        switch $label
            case command
                set message (___printf_color cyan '%s' $message)
            case output
                set message (___printf_color magenta '%s' $message)
        end
        printf '%4d %-7s [%s]\n' $line $label $message
    end

    # Adding extra empty "line" to the end of the input to make the
    # algorithm simpler. Then we always have a last-line trigger for the
    # last pending command. Otherwise we would have to handle the last
    # command after the loop.
    for line in (cat $path) ''
        set line_number (math $line_number + 1)

        if ___starts_with $___command_id $line
            # Found a command line
            set --local cmd (string sub -s (math $___command_id_length + 1) -- $line)
            set --append ___parsed_data "$line_number:cmd:$cmd"
            ___show_parsed_line $line_number command $cmd
            set pending_output 1

        else if test "$line" = "$___command_id"; or test "$line" = "$___command_id_trimmed"
            # Line has prompt, but it is an empty command
            ___show_parsed_line $line_number prompt $line
            set pending_output 0

        else if test "$pending_output" -eq 1; and ___starts_with $___prefix $line
            # Line has the prefix and is not a command, so this is the
            # command output
            set --local out (string sub -s (math $___prefix_length + 1) -- $line)
            set --append ___parsed_data "$line_number:out:$out"
            ___show_parsed_line $line_number output $out

        else
            # Line is not a command neither command output
            ___show_parsed_line $line_number other $line
            set pending_output 0
        end
    end

    test $___verbose_level -ge 2
    and printf 'Parsing finished, %d command/output lines found\n' \
        (count $___parsed_data)
end

function ___test_input_file -a ___input_file
    set --local ___test_number 0
    set --local ___failed_tests 0

    test $___verbose_level -ge 2
    and printf 'Testing commands from file %s\n' $___input_file

    # Adding extra empty "command" after $___parsed_data to make the
    # algorithm simpler. Then we always have a last-command trigger for
    # the last pending command. Otherwise we would have to handle the
    # last command after the loop.
    for ___data in $___parsed_data '0:cmd:'
        test $___verbose_level -ge 3
        and printf '  [%s]\n' $___data

        string split --max 2 : $___data |
        read --line ___line ___type ___text

        if test "$___type" = cmd

            # There's a pending previous command, test it now
            if test -n "$___command"
                set ___test_number (math $___test_number + 1) # this file
                set ___total_tests (math $___total_tests + 1) # global

                test $___verbose_level -ge 2
                and printf 'Running [%s], expecting [%s]\n' \
                    "$___command" \
                    (string join '\\n' $___expected)

                # Important: eval must be in the same execution scope
                # for all the tests in a single file. A var $foo defined
                # in a command should be visible to the next commands
                # from the same file, and it should not be visible for
                # the commands on the next file.
                true # reset $status to zero
                set ___output (eval $___command 2>&1)

                if test "$___output" = "$___expected" # OK
                    test $___verbose_level -ge 1
                    and ___printf_color green '%s:%d: [ ok ] %s\n' \
                        $___input_file $___line_number $___command

                else # FAIL
                    set ___failed_tests (math $___failed_tests + 1) # this file
                    set ___total_failed (math $___total_failed + 1) # global

                    if test $___quiet -eq 0
                        echo
                        ___printf_color red '%s:%d: [fail] %s\n' \
                            $___input_file $___line_number $___command

                        # Show a nice diff
                        diff -u \
                            (printf '%s\n' $___expected | psub) \
                            (printf '%s\n' $___output | psub) |
                        sed '1,2 d' # delete ---/+++ headers
                        echo
                    end
                end
            end

            # Setup new command data
            set ___line_number $___line
            set ___command $___text
            set ___expected

        else if test "$___type" = out
            set --append ___expected $___text

        else
            ___error "Unknown data type: $___type"
        end
    end
    ___show_file_summary $___input_file $___test_number $___failed_tests

    test $___verbose_level -ge 2
    and printf 'Testing finished for file %s\n' $___input_file
end

function ___show_file_summary -a path tested failed
    test $___quiet -eq 1; and return 0

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
                (___printf_color green PASSED)
        else
            printf '%d of %d tests %s\n' \
                $failed \
                $tested \
                (___printf_color red FAILED)
        end
    end
end

#-----------------------------------------------------------------------
# YAML

function ___yaml_string -a text
    # https://www.yaml.info/learn/quote.html#single
    # foo'bar => 'foo''bar'
    printf "'%s'" (string replace --all "'" "''" $text)
end

function ___yaml_root
    printf '%s: %s\n' prefix (___yaml_string $___prefix)
    printf '%s: %s\n' prompt (___yaml_string $___prompt)
    printf '%s: %s\n' version (___yaml_string (___show_version))
    printf '%s:\n' files
end

function ___yaml_file_data # file data_list
    printf '  - path: %s\n' (___yaml_string $argv[1])
    printf '    tests:\n'

    for data in $argv[2..-1]
        string split --max 2 : $data | read --line line type text

        if test "$type" = cmd
            printf '      - line: %d\n' $line
            printf '        cmd: %s\n' (___yaml_string $text)
            printf '        out:\n'
        else
            printf '          - %s\n' (___yaml_string $text)
        end
    end
end

#-----------------------------------------------------------------------

___process_cmdline_arguments $argv
___setup_colors $___color_mode
___validate_prompt $___prompt
___validate_input_files $___input_files

# This will be the main identifier for commands
set ___command_id $___prefix$___prompt
set ___command_id_trimmed (string replace --regex ' +$' '' -- $___command_id)

# Pre-compute lengths and counts
set ___prefix_length (string length -- $___prefix)
set ___command_id_length (string length -- $___command_id)
set ___input_files_count (count $___input_files)

# Maybe we only need to print the YAML?
if test "$___yaml" -eq 1
    ___yaml_root
    for ___input_file in $___input_files
        ___parse_input_file $___input_file # set $___parsed_data
        ___yaml_file_data $___input_file $___parsed_data
    end
    exit 0 # we're done
end

# Run all the tests from all the input files
for ___input_file in $___input_files
    ___parse_input_file $___input_file # set $___parsed_data
    ___test_input_file $___input_file # use $___parsed_data
end

# Show final total status when there are at least 2 input files
# Examples of output:
#   Summary: 14 input files, no tests were found (check --prefix and --prompt)
#   Summary: 14 input files, 56 tests passed
#   Summary: 14 input files, 3 of 53 tests failed
if test $___quiet -eq 0; and test $___input_files_count -gt 1

    echo # visually separate from previous block

    echo -n "Summary: $___input_files_count input files, "

    if test $___total_tests -eq 0
        echo 'no tests were found (check --prefix and --prompt)'
    else if test $___total_failed -eq 0
        printf "%d tests %s\n" \
            $___total_tests \
            (___printf_color green passed)
    else
        printf "%d of %d tests %s\n" \
            $___total_failed \
            $___total_tests \
            (___printf_color red failed)
    end
end

# Script exit code will be zero only when there are no failed tests
test $___total_failed -eq 0
