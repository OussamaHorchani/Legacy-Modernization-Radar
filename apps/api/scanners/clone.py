from contextlib import contextmanager
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

VALID_REPO_URL = re.compile(
    r"^https://(github\.com|gitlab\.com|bitbucket\.org)/"
    r"[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+(\.git)?/?$"
)
VALID_BRANCH = re.compile(r"^[A-Za-z0-9._\-/]+$")


class CloneError(RuntimeError):
    pass


def validate_clone_inputs(repo_url: str, branch: str) -> None:
    if VALID_REPO_URL.match(repo_url) is None:
        raise CloneError("Invalid repository URL")
    if VALID_BRANCH.match(branch) is None:
        raise CloneError("Invalid branch name")


def _safe_url(url: str) -> str:
    return re.sub(r"://[^@/]+@", "://", url)


@contextmanager
def shallow_clone(repo_url: str, branch: str):
    validate_clone_inputs(repo_url, branch)
    temp_dir = Path(tempfile.mkdtemp(prefix="radar-scan-"))
    safe_repo_url = _safe_url(repo_url)

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
            raise CloneError(f"Failed to clone {safe_repo_url}@{branch}: {detail}")

        yield temp_dir
    except subprocess.TimeoutExpired as exc:
        raise CloneError(
            f"Failed to clone {safe_repo_url}@{branch}: git clone timed out"
        ) from exc
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
