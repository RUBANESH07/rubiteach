"""Child process that runs ONE student submission. Never imported by the API; launched by pyrunner.py.

Input (JSON on stdin): {code, stdin, expr, nonce, work, max_out}
Output (last line on the real stdout): <nonce>{json result}

Defence in depth, not a perfect jail: an audit hook blocks network, process creation, native code and any
file access outside a throw-away working directory; the parent enforces a time limit and kills the process.
For a public deployment run this on a separate, locked-down host (VM / low-privilege user), never next to the DB.
"""
import contextlib
import io
import json
import os
import sys
import traceback

STUDENT = "<student>"


class OutputLimit(Exception):
    pass


class Capped(io.StringIO):
    def __init__(self, limit):
        super().__init__()
        self.limit = limit

    def write(self, s):
        if self.tell() + len(s) > self.limit:
            super().write(s[: max(0, self.limit - self.tell())])
            raise OutputLimit("Output limit exceeded")
        return super().write(s)


def _real(p):
    try:
        return os.path.normcase(os.path.realpath(os.fsdecode(p)))
    except Exception:
        return None


def install_hook(work):
    work = _real(work)
    lib_dirs = {_real(p) for p in {sys.prefix, sys.base_prefix, sys.exec_prefix, sys.base_exec_prefix} if p}
    lib_dirs |= {_real(p) for p in sys.path if p}
    lib_dirs.discard(None)

    def inside(p, roots):
        return p is not None and any(p == r or p.startswith(r + os.sep) for r in roots)

    loopback = {"127.0.0.1", "::1", "localhost", "", "0.0.0.0"}
    bound = []  # sockets this run bound itself; asyncio's self-pipe needs a loopback listener + connect

    def host_of(addr):
        return addr[0] if isinstance(addr, tuple) and addr else None

    def socket_event(event, args):
        if event == "socket.__new__":
            return
        if event == "socket.bind" and host_of(args[1]) in loopback:
            bound.append(args[0])
            return
        if event == "socket.connect" and host_of(args[1]) in loopback:
            ports = set()
            for s in bound:
                try:
                    ports.add(s.getsockname()[1])
                except OSError:
                    pass
            if args[1][1] in ports:
                return
        raise PermissionError("Network access is not allowed in the exercise sandbox")

    blocked_prefixes = ("subprocess.", "ctypes.", "pty.", "os.exec", "os.spawn", "os.posix_spawn",
                        "os.fork", "os.system", "os.kill", "os.startfile", "_winapi.CreateProcess", "winreg.",
                        "webbrowser.", "shutil.", "tempfile.", "urllib.Request", "http.client.", "smtplib.", "ftplib.",
                        "os.putenv", "os.unsetenv", "signal.", "sys.settrace", "sys.setprofile")
    path_events = {"os.remove", "os.rename", "os.rmdir", "os.mkdir", "os.chmod", "os.chown", "os.symlink", "os.link",
                   "os.truncate", "os.utime", "os.chdir", "os.listdir", "os.scandir", "os.walk", "glob.glob"}

    def hook(event, args):
        if event == "open":
            path, mode, flags = args
            if isinstance(path, int):
                return
            p = _real(path)
            writing = bool(mode and any(c in str(mode) for c in "wax+")) or bool(
                isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if inside(p, [work]) or (not writing and inside(p, lib_dirs)):
                return
            raise PermissionError("File access outside the exercise folder is not allowed")
        if event.startswith("socket."):
            return socket_event(event, args)
        if event.startswith(blocked_prefixes):
            raise PermissionError(f"'{event}' is not allowed in the exercise sandbox")
        if event in path_events:
            p = _real(args[0]) if args and not isinstance(args[0], int) else work
            if inside(p, [work]) or (event in ("os.listdir", "os.scandir") and inside(p, lib_dirs)):
                return
            raise PermissionError("File access outside the exercise folder is not allowed")

    sys.addaudithook(hook)


def apply_limits():
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (768 * 2**20, 768 * 2**20))
        resource.setrlimit(resource.RLIMIT_FSIZE, (5 * 2**20, 5 * 2**20))
        resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
    except Exception:  # Windows has no `resource`; the parent time limit still applies
        pass


def main():
    payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    nonce, work = payload["nonce"], payload["work"]
    out_fd = os.dup(1)
    os.chdir(work)
    apply_limits()
    # Pre-import the modules lessons commonly need so lazy imports inside student code stay cheap.
    result = {"stdout": "", "error": None, "value": None, "has_value": False}
    stdout = Capped(payload["max_out"])
    sys.stdin = io.StringIO(payload["stdin"])
    code = payload["code"]
    expr = payload["expr"]
    try:
        compiled = compile(code, STUDENT, "exec")
    except SyntaxError as e:
        result["error"] = f"SyntaxError: {e.msg} (line {e.lineno})"
        compiled = None
    install_hook(work)
    if compiled is not None:
        ns = {"__name__": "__main__", "__builtins__": __builtins__}
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stdout):
                try:
                    exec(compiled, ns)
                    if expr:
                        value = eval(compile(expr, "<test>", "eval"), ns)
                        result["value"], result["has_value"] = repr(value)[:4000], True
                except SystemExit:
                    pass
        except OutputLimit:
            result["error"] = "Output limit exceeded (too much text printed)"
        except BaseException as e:  # noqa: BLE001 - report every student error
            tb = traceback.extract_tb(e.__traceback__)
            line = next((f.lineno for f in reversed(tb) if f.filename == STUDENT), None)
            where = f" (line {line})" if line else ""
            result["error"] = f"{type(e).__name__}: {e}{where}"[:500]
    result["stdout"] = stdout.getvalue()
    os.write(out_fd, (nonce + json.dumps(result) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
