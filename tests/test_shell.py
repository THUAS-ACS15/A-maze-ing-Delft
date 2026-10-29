import pytest

from unittest.mock import Mock

import utilities.shell as shell_module
from utilities.shell import ShellResult, VirtualShell


@pytest.fixture
def shell():
    return VirtualShell(
        {
            "etc": {"hostname": "teacher-pc"},
            "home": {
                "teacher": {
                    "Documents": {
                        "grades.csv": "grades",
                        "notes.md": "notes",
                        ".hidden.txt": "hidden",
                    },
                    "Downloads": {"manual.txt": "manual"},
                    ".secret": {"super_secret_file.txt": "the key"},
                    ".bashrc": "export PS1='$ '",
                    "README.txt": "read me",
                    "my notes.txt": "spaced",
                }
            },
            "var": {"log": {"nixos.log": "log"}},
        }
    )


def test_prompt_at_home(shell):
    assert shell.prompt == "teacher@teacher-pc:~$"


def test_prompt_in_subdirectory(shell):
    shell.execute("cd Documents")
    assert shell.prompt == "teacher@teacher-pc:~/Documents$"


def test_help_lists_core_commands(shell):
    output = shell.execute("help").output
    for command in ("ls", "cd", "pwd", "cat", "find", "tree", "clear", "whoami", "exit"):
        assert command in output


def test_empty_command_does_nothing(shell):
    assert shell.execute("") == ShellResult()


def test_unknown_command(shell):
    assert (
        shell.execute("frobnicate").output
        == "bash: frobnicate: command not found"
    )


def test_unmatched_quote(shell):
    assert (
        shell.execute('cat "unterminated').output
        == "bash: syntax error: unmatched quote"
    )


def test_ls_lists_visible_entries(shell):
    assert shell.execute("ls").output.splitlines() == [
        "Documents",
        "Downloads",
        "README.txt",
        "my notes.txt",
    ]


def test_ls_all_includes_hidden_entries(shell):
    output = shell.execute("ls -a").output
    assert ".secret" in output
    assert ".bashrc" in output


def test_ls_path_and_long_format(shell):
    assert shell.execute("ls /etc").output == "hostname"
    long_output = shell.execute("ls -l /etc").output
    assert long_output.startswith("-rw-r--r--")
    assert long_output.endswith("hostname")


def test_ls_missing_path(shell):
    assert (
        shell.execute("ls /missing").output
        == "ls: cannot access '/missing': No such file or directory"
    )


def test_cd_pwd_and_parent(shell):
    shell.execute("cd Documents")
    assert shell.execute("pwd").output == "/home/teacher/Documents"
    shell.execute("cd ..")
    assert shell.execute("pwd").output == "/home/teacher"


def test_cd_home_and_tilde(shell):
    shell.execute("cd /etc")
    shell.execute("cd")
    assert shell.execute("pwd").output == "/home/teacher"
    shell.execute("cd /etc")
    shell.execute("cd ~")
    assert shell.execute("pwd").output == "/home/teacher"


def test_cd_missing_and_file_errors(shell):
    assert (
        shell.execute("cd /missing").output
        == "cd: no such file or directory: /missing"
    )
    assert (
        shell.execute("cd README.txt").output
        == "cd: not a directory: README.txt"
    )


def test_cat_file_and_read_paths(shell):
    result = shell.execute("cat README.txt")
    assert result.output == "read me"
    assert result.read_paths == ("/home/teacher/README.txt",)


def test_cat_quoted_path_with_spaces(shell):
    assert shell.execute('cat "my notes.txt"').output == "spaced"


def test_cat_missing_and_directory_errors(shell):
    assert (
        shell.execute("cat missing.txt").output
        == "cat: missing.txt: No such file or directory"
    )
    assert (
        shell.execute("cat Documents").output
        == "cat: Documents: Is a directory"
    )


def test_cat_multiple_files(shell):
    result = shell.execute("cat README.txt Documents/notes.md")
    assert result.output == "read me\nnotes"
    assert result.read_paths == (
        "/home/teacher/README.txt",
        "/home/teacher/Documents/notes.md",
    )


def test_find_all_and_name(shell):
    output = shell.execute("find .").output.splitlines()
    assert "./Documents" in output
    assert "./.secret" in output
    assert "./.secret/super_secret_file.txt" in output


def test_find_iname_and_type(shell):
    assert shell.execute('find . -iname "*secret*"').output.splitlines() == [
        "./.secret",
        "./.secret/super_secret_file.txt",
    ]
    assert shell.execute(
        'find . -type f -iname "*secret*"'
    ).output.splitlines() == ["./.secret/super_secret_file.txt"]


def test_find_absolute_path(shell):
    assert (
        shell.execute('find /home/teacher/.secret -name "*.txt"').output
        == "/home/teacher/.secret/super_secret_file.txt"
    )


def test_find_missing_path(shell):
    assert (
        shell.execute("find /missing").output
        == "find: '/missing': No such file or directory"
    )


def test_tree_hides_and_shows_hidden(shell):
    visible = shell.execute("tree").output
    assert ".secret" not in visible
    assert "Documents" in visible
    hidden = shell.execute("tree -a").output
    assert ".secret" in hidden


def test_clear_whoami_and_exit(shell):
    assert shell.execute("whoami").output == "teacher"
    assert shell.execute("clear").clear_requested is True
    for command in ("exit", "logout", "shutdown"):
        assert shell.execute(command).exit_requested is True


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("ls --bogus", "ls: unrecognized option '--bogus'"),
        ("ls -z", "ls: invalid option -- 'z'"),
        ("cd a b", "cd: too many arguments"),
        ("cat", "cat: missing operand"),
        ("find . -name", "find: missing argument to '-name'"),
        ("find . -type x", "find: unknown argument to -type: x"),
        ("find . -bogus", "find: unknown predicate '-bogus'"),
        ("tree a b", "tree: too many arguments"),
        ("tree --bogus", "tree: unrecognized option '--bogus'"),
        ("tree /missing", "tree: /missing: No such file or directory"),
        ("frobnicate --verbose", "bash: frobnicate: command not found"),
    ],
)
def test_command_error_messages(shell, command, expected):
    assert shell.execute(command).output == expected


@pytest.mark.parametrize(
    ("start", "command", "expected"),
    [
        ("/home/teacher", "cd Documents", "/home/teacher/Documents"),
        ("/home/teacher/Documents", "cd ..", "/home/teacher"),
        ("/home/teacher", "cd /etc", "/etc"),
        ("/etc", "cd", "/home/teacher"),
        ("/etc", "cd ~", "/home/teacher"),
        ("/home/teacher", "cd ~/Downloads", "/home/teacher/Downloads"),
        ("/home/teacher", "cd .", "/home/teacher"),
    ],
)
def test_cd_navigation(shell, start, command, expected):
    shell.cwd = start
    shell.execute(command)
    assert shell.execute("pwd").output == expected


@pytest.mark.parametrize(
    ("filesystem", "command", "expected_lines"),
    [
        ({"a": "1", "b": "2"}, "ls", ["a", "b"]),
        ({"dir": {"f.txt": "x"}}, "ls dir", ["f.txt"]),
        ({"dir": {"f.txt": "x"}}, "ls -a dir", [".", "..", "f.txt"]),
        ({}, "ls", []),
    ],
)
def test_ls_over_filesystems(filesystem, command, expected_lines):
    custom = VirtualShell(filesystem, cwd="/", home="/")
    assert custom.execute(command).output.splitlines() == expected_lines


@pytest.mark.parametrize(
    "command",
    [
        "",
        "   ",
        "cd",
        "cd a b c",
        "cd -",
        "ls -z",
        "ls --bogus",
        "ls > out.txt",
        "cat",
        "cat /",
        "find",
        "find . -name",
        "find . -type z",
        "find . --bogus",
        "tree a b",
        "tree --bogus",
        "HELP",
        "Exit",
        "sudo ls",
        "echo hello | cat",
        "cat 'unclosed",
        'cat "unclosed',
        "~root",
        "$HOME",
    ],
)
def test_execute_never_raises(shell, command):
    assert isinstance(shell.execute(command), ShellResult)


@pytest.mark.parametrize("command", ["exit", "logout", "shutdown"])
def test_exit_aliases_request_exit(shell, command):
    result = shell.execute(command)
    assert result.exit_requested is True
    assert result.output == ""


def test_prompt_reflects_patched_identity(monkeypatch, shell):
    monkeypatch.setattr(shell, "user", "root")
    monkeypatch.setattr(shell, "hostname", "nixos")
    assert shell.prompt == "root@nixos:~$"


def test_display_cwd_outside_home(monkeypatch, shell):
    monkeypatch.setattr(shell, "cwd", "/etc")
    assert shell.display_cwd == "/etc"


def test_execute_reports_syntax_error_when_split_fails(monkeypatch, shell):
    monkeypatch.setattr(
        shell_module.shlex, "split", Mock(side_effect=ValueError("no closing quotation"))
    )
    assert (
        shell.execute("cat 'oops").output == "bash: syntax error: unmatched quote"
    )
