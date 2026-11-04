"""Runner host Linux invocato da Pj tramite flatpak-spawn, non API utente."""
import os
import re
import signal
import sys
import time


def _tagged_processes(token):
    # Come processx/ps, riconosce soltanto processi con il marcatore di questa chiamata.
    marker = b"MZPJ_HOST_CALL=" + token.encode("ascii")
    found = []
    for name in os.listdir("/proc"):
        if not name.isdecimal() or int(name) == os.getpid():
            continue
        base = "/proc/" + name
        try:
            if os.stat(base).st_uid != os.getuid():
                continue
            with open(base + "/environ", "rb") as handle:
                if marker not in handle.read().split(b"\0"):
                    continue
            with open(base + "/stat", encoding="utf-8") as handle:
                state = handle.read().rsplit(")", 1)[1].split()[0]
            if state not in ("Z", "X"):
                found.append(int(name))
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
    return found


def _cleanup(token):
    # Ripete la scansione per includere i discendenti in fase di creazione.
    deadline = time.monotonic() + 2.0
    while True:
        live = _tagged_processes(token)
        if not live:
            return True
        for pid in live:
            try:
                # Ricontrolla il marcatore prima del segnale, evitando PID estranei.
                with open(f"/proc/{pid}/environ", "rb") as handle:
                    owned = (b"MZPJ_HOST_CALL=" + token.encode("ascii")) in handle.read().split(b"\0")
                if owned:
                    os.kill(pid, signal.SIGKILL)
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                pass
        if time.monotonic() >= deadline:
            return not _tagged_processes(token)
        time.sleep(0.02)


def _watch(parent, token):
    # Una sessione distinta sopravvive alla terminazione del gruppo del launcher.
    os.setsid()
    try:
        # Evita che il watchdog trattenga stdin (il file dello script).
        os.close(0)
        while os.getppid() == parent:
            time.sleep(0.02)
        clean = _cleanup(token)
        message = f"\n__MZPJ_HOST_CLEAN__ {token} {'OK' if clean else 'FAILED'}\n"
        os.write(1, message.encode("ascii"))
    except BrokenPipeError:
        # Se R e' morto il cleanup deve comunque essere gia' stato effettuato.
        pass
    finally:
        os._exit(0)


def main():
    if not sys.platform.startswith("linux") or len(sys.argv) != 2:
        raise RuntimeError("The Pj Flatpak host runner requires Linux and a call token.")
    token = sys.argv[1]
    if re.fullmatch(r"[A-Za-z0-9_-]{8,128}", token) is None:
        raise ValueError("Invalid Pj host call token.")
    parent = os.getpid()
    watcher = os.fork()
    if watcher == 0:
        _watch(parent, token)
    # I subprocessi Python ereditano il token anche se creano una nuova sessione.
    os.environ["MZPJ_HOST_CALL"] = token
    os.write(1, f"__MZPJ_HOST_READY__ {token}\n".encode("ascii"))
    source = sys.stdin.read()
    # Conserva la convenzione python '-' del percorso System Python precedente.
    sys.argv = ["-"]
    namespace = {"__name__": "__main__", "__file__": "<stdin>",
                 "__package__": None, "__spec__": None}
    exec(compile(source, "<stdin>", "exec"), namespace)


if __name__ == "__main__":
    main()
