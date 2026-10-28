"""Virtual shell engine. Pure: no game state, no display code, no real filesystem access."""

import fnmatch
import posixpath
import shlex
from dataclasses import dataclass

HELP_TEXT = """Available commands:
  ls [-a] [-l] [path...]   list directory contents
  cd [path]                change directory
  pwd                      print the working directory
  cat <file...>            print file contents
  find [path]              search for files
  tree [path]              show a directory tree
  exit                     leave the terminal
  help                     show this help"""


@dataclass(frozen=True)
class ShellResult:
    output: str = ""
    exit_requested: bool = False
    clear_requested: bool = False
    read_paths: tuple[str, ...] = ()


class VirtualShell:
    def __init__(
        self,
        filesystem: dict,
        cwd: str = "/home/teacher",
        home: str = "/home/teacher",
        user: str = "teacher",
        hostname: str = "teacher-pc",
    ):
        self.filesystem = filesystem
        self.cwd = cwd
        self.home = home
        self.user = user
        self.hostname = hostname

    @property
    def display_cwd(self) -> str:
        if self.cwd == self.home:
            return "~"
        if self.cwd.startswith(self.home + "/"):
            return "~" + self.cwd[len(self.home) :]
        return self.cwd

    @property
    def prompt(self) -> str:
        return f"{self.user}@{self.hostname}:{self.display_cwd}$"

    def execute(self, command: str) -> ShellResult:
        try:
            tokens = shlex.split(command, posix=True)
        except ValueError:
            return ShellResult(output="bash: syntax error: unmatched quote")
        if not tokens:
            return ShellResult()
        name, args = tokens[0], tokens[1:]
        handler = getattr(self, f"_cmd_{name}", None)
        if handler is None:
            return ShellResult(output=f"bash: {name}: command not found")
        return handler(args)

    def _cmd_help(self, args: list[str]) -> ShellResult:
        return ShellResult(output=HELP_TEXT)

    def _cmd_ls(self, args: list[str]) -> ShellResult:
        show_all = False
        long_format = False
        targets: list[str] = []
        for arg in args:
            if arg == "--all":
                show_all = True
            elif arg.startswith("--"):
                return ShellResult(output=f"ls: unrecognized option '{arg}'")
            elif arg.startswith("-") and arg != "-":
                for flag in arg[1:]:
                    if flag == "a":
                        show_all = True
                    elif flag == "l":
                        long_format = True
                    else:
                        return ShellResult(output=f"ls: invalid option -- '{flag}'")
            else:
                targets.append(arg)
        if not targets:
            targets = ["."]

        errors: list[str] = []
        file_entries: list[tuple[str, dict | str]] = []
        dir_entries: list[tuple[str, dict]] = []
        for target in targets:
            node = self._node(self._resolve(target))
            if node is None:
                errors.append(f"ls: cannot access '{target}': No such file or directory")
            elif isinstance(node, dict):
                dir_entries.append((target, node))
            else:
                file_entries.append((target, node))

        blocks = ["\n".join(errors)] if errors else []
        if file_entries:
            blocks.append("\n".join(self._render(file_entries, long_format)))
        for target, node in dir_entries:
            body = "\n".join(self._render(self._listing(node, show_all), long_format))
            blocks.append(f"{target}:\n{body}" if len(targets) > 1 else body)
        return ShellResult(output="\n\n".join(blocks))

    def _cmd_cd(self, args: list[str]) -> ShellResult:
        if len(args) > 1:
            return ShellResult(output="cd: too many arguments")
        raw = args[0] if args else "~"
        path = self._resolve(raw)
        node = self._node(path)
        if node is None:
            return ShellResult(output=f"cd: no such file or directory: {raw}")
        if not isinstance(node, dict):
            return ShellResult(output=f"cd: not a directory: {raw}")
        self.cwd = path
        return ShellResult()

    def _cmd_pwd(self, args: list[str]) -> ShellResult:
        return ShellResult(output=self.cwd)

    def _cmd_cat(self, args: list[str]) -> ShellResult:
        if not args:
            return ShellResult(output="cat: missing operand")
        lines: list[str] = []
        read_paths: list[str] = []
        for raw in args:
            path = self._resolve(raw)
            node = self._node(path)
            if node is None:
                lines.append(f"cat: {raw}: No such file or directory")
            elif isinstance(node, dict):
                lines.append(f"cat: {raw}: Is a directory")
            else:
                lines.append(node)
                read_paths.append(path)
        return ShellResult(output="\n".join(lines), read_paths=tuple(read_paths))

    def _cmd_find(self, args: list[str]) -> ShellResult:
        root: str | None = None
        name_pattern: str | None = None
        ignore_case = False
        kind: str | None = None
        index = 0
        while index < len(args):
            arg = args[index]
            if arg in ("-name", "-iname", "-type"):
                if index + 1 >= len(args):
                    return ShellResult(output=f"find: missing argument to '{arg}'")
                value = args[index + 1]
                index += 2
                if arg == "-type":
                    if value not in ("f", "d"):
                        return ShellResult(output=f"find: unknown argument to -type: {value}")
                    kind = value
                else:
                    name_pattern = value
                    ignore_case = arg == "-iname"
            elif not arg.startswith("-") and root is None:
                root = arg
                index += 1
            else:
                return ShellResult(output=f"find: unknown predicate '{arg}'")

        raw = root if root is not None else "."
        node = self._node(self._resolve(raw))
        if node is None:
            return ShellResult(output=f"find: '{raw}': No such file or directory")

        matches: list[str] = []
        root_name = posixpath.basename(raw.rstrip("/")) or raw
        for display, name, entry in self._walk(raw, root_name, node):
            if kind == "f" and isinstance(entry, dict):
                continue
            if kind == "d" and not isinstance(entry, dict):
                continue
            if name_pattern is not None:
                subject, pattern = (name.lower(), name_pattern.lower()) if ignore_case else (name, name_pattern)
                if not fnmatch.fnmatchcase(subject, pattern):
                    continue
            matches.append(display)
        return ShellResult(output="\n".join(sorted(matches)))

    def _walk(self, display: str, name: str, node: dict | str) -> list[tuple[str, str, dict | str]]:
        found = [(display, name, node)]
        if isinstance(node, dict):
            for child_name, child in node.items():
                found.extend(self._walk(posixpath.join(display, child_name), child_name, child))
        return found

    def _cmd_tree(self, args: list[str]) -> ShellResult:
        show_all = False
        targets: list[str] = []
        for arg in args:
            if arg == "-a":
                show_all = True
            elif arg.startswith("-"):
                return ShellResult(output=f"tree: unrecognized option '{arg}'")
            else:
                targets.append(arg)
        if len(targets) > 1:
            return ShellResult(output="tree: too many arguments")
        raw = targets[0] if targets else "."
        node = self._node(self._resolve(raw))
        if node is None:
            return ShellResult(output=f"tree: {raw}: No such file or directory")
        lines = [raw]
        if isinstance(node, dict):
            lines.extend(self._tree_lines(node, "", show_all))
        return ShellResult(output="\n".join(lines))

    def _tree_lines(self, node: dict, prefix: str, show_all: bool) -> list[str]:
        names = sorted(name for name in node if show_all or not name.startswith("."))
        lines: list[str] = []
        for index, name in enumerate(names):
            last = index == len(names) - 1
            lines.append(f"{prefix}{'└── ' if last else '├── '}{name}")
            child = node[name]
            if isinstance(child, dict):
                lines.extend(self._tree_lines(child, prefix + ("    " if last else "│   "), show_all))
        return lines

    def _cmd_whoami(self, args: list[str]) -> ShellResult:
        return ShellResult(output=self.user)

    def _cmd_clear(self, args: list[str]) -> ShellResult:
        return ShellResult(clear_requested=True)

    def _cmd_exit(self, args: list[str]) -> ShellResult:
        return ShellResult(exit_requested=True)

    _cmd_logout = _cmd_exit
    _cmd_shutdown = _cmd_exit

    def _listing(self, node: dict, show_all: bool) -> list[tuple[str, dict | str]]:
        names = sorted(name for name in node if show_all or not name.startswith("."))
        entries = [(name, node[name]) for name in names]
        if show_all:
            entries = [(".", {}), ("..", {})] + entries
        return entries

    def _render(self, entries: list[tuple[str, dict | str]], long_format: bool) -> list[str]:
        if not long_format:
            return [name for name, _ in entries]
        lines = []
        for name, node in entries:
            if isinstance(node, dict):
                lines.append(f"drwxr-xr-x 1 teacher users {4096:>5} Jan 01 00:00 {name}")
            else:
                lines.append(f"-rw-r--r-- 1 teacher users {len(node):>5} Jan 01 00:00 {name}")
        return lines

    def _resolve(self, path: str) -> str:
        if path == "~" or path.startswith("~/"):
            path = self.home + path[1:]
        elif not path.startswith("/"):
            path = posixpath.join(self.cwd, path)
        return "/" + posixpath.normpath(path).lstrip("/")

    def _node(self, path: str) -> dict | str | None:
        node: dict | str = self.filesystem
        for part in path.split("/"):
            if part == "":
                continue
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
        return node
