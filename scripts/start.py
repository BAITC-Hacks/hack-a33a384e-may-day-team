"""Start the local Career Quest backend and frontend dev server."""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"
STOP_REQUESTED = False


def main() -> int:
    _install_stop_signals()
    npm = shutil.which("npm")
    vite = FRONTEND / "node_modules" / "vite" / "package.json"
    if npm is None or not vite.is_file():
        print(
            "Frontend dependencies are not available. "
            "Install them with npm ci in frontend/ before starting.",
            file=sys.stderr,
        )
        return 1

    backend = _spawn(
        [sys.executable, "-m", "backend.career_quest.serve"],
        ROOT,
    )
    frontend = _spawn(
        [npm, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
        FRONTEND,
    )
    print(f"Backend: {BACKEND_URL}", flush=True)
    print(f"Frontend: {FRONTEND_URL}", flush=True)
    exit_code = 0
    try:
        while not STOP_REQUESTED:
            backend_code = backend.poll()
            frontend_code = frontend.poll()
            if backend_code is not None or frontend_code is not None:
                exit_code = 1
                break
            time.sleep(0.4)
    finally:
        _stop(frontend)
        _stop(backend)
    return exit_code


def _request_stop(signum: int, frame: object) -> None:
    global STOP_REQUESTED
    STOP_REQUESTED = True


def _install_stop_signals() -> None:
    signal.signal(signal.SIGINT, _request_stop)
    if os.name == "nt":
        signal.signal(signal.SIGBREAK, _request_stop)
    else:
        signal.signal(signal.SIGTERM, _request_stop)


def _spawn(args: list[str], cwd: Path) -> subprocess.Popen[bytes]:
    kwargs: dict[str, object] = {"cwd": cwd}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(args, **kwargs)


def _stop(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        process.terminate()
    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
