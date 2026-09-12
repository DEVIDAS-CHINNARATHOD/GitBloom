import os
import shutil
import subprocess
import tempfile


def run(command, cwd=None, env=None):
    return subprocess.run(command, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def clone_repository(url):
    workspace = tempfile.mkdtemp(prefix="gitbloom-")
    name = url.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    repository = os.path.join(workspace, name)
    result = run(["git", "clone", url, repository])
    if result.returncode:
        shutil.rmtree(workspace, ignore_errors=True)
        raise RuntimeError(result.stderr.strip() or "Unable to clone repository.")
    return workspace, repository


def commit(repository, files, date, message):
    for filename in files:
        result = run(["git", "add", "--", filename], cwd=repository)
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or f"Unable to stage {filename}.")

    timestamp = date.strftime("%Y-%m-%dT%H:%M:%S")
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = timestamp
    env["GIT_COMMITTER_DATE"] = timestamp
    result = run(["git", "commit", "-m", message], cwd=repository, env=env)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Unable to create commit.")


def push(repository):
    result = run(["git", "push"], cwd=repository)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Push failed.")
