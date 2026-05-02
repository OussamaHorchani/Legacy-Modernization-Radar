from contextlib import contextmanager
from pathlib import Path
import shutil
import subprocess
import tempfile


class CloneError(RuntimeError):
    pass


@contextmanager
def shallow_clone(repo_url: str, branch: str):
    temp_dir = Path(tempfile.mkdtemp(prefix="radar-scan-"))

    try:
        result = subprocess.run(
            [
                "git",
                "clone",
                "--depth=1",
                f"--branch={branch}",
                "--single-branch",
                repo_url,
                str(temp_dir),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=25,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip() or "unknown git clone error"
            raise CloneError(f"Failed to clone {repo_url}@{branch}: {detail}")

        yield temp_dir
    except subprocess.TimeoutExpired as exc:
        raise CloneError(f"Failed to clone {repo_url}@{branch}: git clone timed out") from exc
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
