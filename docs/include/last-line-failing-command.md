Test to avoid raising `RuntimeError` if the user enters a failing command in the very last line of the input file.

Related code:
- `ShellBase.get_script()`
- `ShellBase.execute()`

$ false
