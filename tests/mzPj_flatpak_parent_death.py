"""Verifica Linux della morte forzata del solo processo R di prova."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

root = Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory(prefix="mzPj-parent-death-", dir=root) as folder:
    folder = Path(folder)
    marker = folder / "host-pids.json"
    script = folder / "kill-this-R-only.R"
    code = "\n".join([
        "import subprocess,sys,os,json,time",
        "child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'],start_new_session=True)",
        "pids=[os.getpid(),child.pid]",
        "records={str(pid):open(f'/proc/{pid}/stat').read().rsplit(')',1)[1].split()[19] for pid in pids}",
        f"with open({str(marker)!r},'w') as f: json.dump(records,f)",
        "time.sleep(60)",
    ])
    script.write_text("\n".join([
        f"root <- {json.dumps(str(root))}",
        "libs <- list.dirs(file.path(root,'build'),recursive=FALSE,full.names=TRUE)",
        "libs <- libs[file.exists(file.path(libs,'Pj/DESCRIPTION'))]",
        ".libPaths(c(libs,'/app/lib/R/library',.libPaths()))",
        "library(Pj)",
        f"Pj::mzPjRunPython({json.dumps(code)},python='system',timeout=60L)",
    ]), encoding="utf-8")
    records = {}
    launch = subprocess.Popen(["flatpak", "run", "--command=Rscript",
                               "org.jamovi.jamovi", "--vanilla", str(script)],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        deadline = time.monotonic() + 15
        while not marker.exists():
            if time.monotonic() >= deadline or launch.poll() is not None:
                raise RuntimeError("Test host worker did not start")
            time.sleep(.02)
        records = json.loads(marker.read_text())
        matches = []
        for entry in Path("/proc").iterdir():
            if not entry.name.isdecimal():
                continue
            try:
                if entry.stat().st_uid != os.getuid():
                    continue
                args = (entry / "cmdline").read_bytes().split(b"\0")
                if any(arg == ("--file=" + str(script)).encode() for arg in args):
                    matches.append(int(entry.name))
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                pass
        assert len(matches) == 1, matches
        os.kill(matches[0], signal.SIGKILL)
        deadline = time.monotonic() + 5
        while True:
            live = []
            for pid, start in records.items():
                try:
                    fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
                    if fields[19] == start and fields[0] not in ("Z", "X"):
                        live.append(int(pid))
                except FileNotFoundError:
                    pass
            if not live or time.monotonic() >= deadline:
                break
            time.sleep(.02)
        assert not live, f"Host processes survived R death: {live}"
        print("Real R SIGKILL, Flatpak launcher death and host descendant cleanup PASSED")
    finally:
        # Ripulisce soltanto le identita' dei processi creati dalla prova.
        for pid, start in records.items():
            try:
                fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
                if fields[19] == start and fields[0] not in ("Z", "X"):
                    os.kill(int(pid), signal.SIGKILL)
            except (FileNotFoundError, ProcessLookupError):
                pass
        try:
            launch.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            launch.kill()
            launch.communicate(timeout=5)
