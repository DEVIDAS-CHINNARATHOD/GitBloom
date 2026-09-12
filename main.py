import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timedelta


APP_NAME = "GitBloom"
COMMIT_MESSAGE = "gitbloom commit"

MEMES = [
    "It's not a bug, it's an undocumented feature.",
    r"Works on my machine! ¯\_(ツ)_/¯",
    "There are 10 types of people: those who understand binary, and those who don't.",
    "Real programmers count from 0.",
    "There's no place like 127.0.0.1",
    "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
    "Programming is 10% writing code and 90% understanding why it's not working.",
    "To understand recursion, you must first understand recursion.",
    "My code doesn't work, I have no idea why. My code works, I have no idea why.",
    "Software and cathedrals are much the same – first we build them, then we pray.",
    "Deleting code is better than writing code.",
    "Why do Java developers wear glasses? Because they don't C#.",
    "A QA engineer walks into a bar. Orders a beer. Orders 0 beers. Orders 999999999 beers. Orders a lizard.",
    "Hide and seek champion since 1958: ';' in C/C++",
    "99 little bugs in the code. Take one down, patch it around. 127 little bugs in the code.",
    "git commit -m 'fixed stuff' (narrator: it was not fixed)",
    "In case of fire: git commit, git push, leave building."
]


def get_random_meme():
    try:
        req = urllib.request.Request(
            "https://official-joke-api.appspot.com/jokes/programming/random",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            if isinstance(data, list) and len(data) > 0:
                setup = data[0].get("setup", "")
                punchline = data[0].get("punchline", "")
                return f"{setup} -> {punchline}"
    except Exception:
        pass
    return random.choice(MEMES)


def banner():
    print(r"""
   ____ _  _     ____  _  ___   ___   _ __ ___  
  / ___(_)| |_  | __ )| |/ _ \ / _ \ | '_ ` _ \ 
 | |  _| || __| |  _ \| | (_) | (_) || | | | | |
 | |_| | || |_  | |_) | |\___/ \___/ |_| |_| |_|
  \____|_| \__| |____/|_|                       

                G I T B L O O M
""")


def run_command(command, cwd=None, env=None):
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )


def clean_repository_url(url):
    url = url.strip()

    if url.startswith("[") and "](" in url and url.endswith(")"):
        url = url.split("](", 1)[1][:-1]

    return url


def get_repository_url():
    while True:
        url = input("Git repository URL: ").strip()

        if not url:
            print("Please enter a repository URL.")
            continue

        url = clean_repository_url(url)

        if not url.startswith(("https://", "http://", "git@")):
            print("Please enter a valid Git repository URL.")
            continue

        return url


def get_filename():
    while True:
        filename = input("File name: ").strip()

        if not filename:
            print("Please enter a file name.")
            continue

        if os.path.basename(filename) != filename:
            print("Please enter only a file name.")
            continue

        return filename


def get_date_input(prompt_text):
    while True:
        value = input(prompt_text).strip()
        clean_val = value.replace("-", "").replace("/", "")

        if len(clean_val) == 8 and clean_val.isdigit():
            try:
                day = int(clean_val[:2])
                month = int(clean_val[2:4])
                year = int(clean_val[4:])
                return datetime(year, month, day)
            except ValueError:
                pass

        print("Please enter a valid date in DDMMYYYY format (e.g., 01012025 or 01-01-2026).")


def get_commit_count():
    while True:
        value = input("Number of commits: ").strip()

        try:
            count = int(value)

            if count > 0:
                return count

            print("Enter a number greater than zero.")

        except ValueError:
            print("Please enter a valid number.")


def random_date_between(start_date, end_date):
    start_dt = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
    end_dt = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)

    if end_dt < start_dt:
        start_dt, end_dt = end_dt, start_dt

    total_seconds = int((end_dt - start_dt).total_seconds())
    random_seconds = random.randint(0, total_seconds)

    return start_dt + timedelta(seconds=random_seconds)


def clone_repository(url):
    url = clean_repository_url(url)

    repository_name = url.rstrip("/").split("/")[-1]

    if repository_name.endswith(".git"):
        repository_name = repository_name[:-4]

    temp_root = tempfile.mkdtemp(
        prefix="gitbloom-"
    )

    clone_path = os.path.join(
        temp_root,
        repository_name
    )

    print("\nCloning repository")

    result = run_command(
        ["git", "clone", url, clone_path]
    )

    if result.returncode != 0:
        print("Unable to clone repository.")

        if result.stderr:
            print(result.stderr.strip())

        shutil.rmtree(
            temp_root,
            ignore_errors=True
        )

        return None

    print("Repository ready")

    return clone_path


def create_file_if_needed(repo_path, filename):
    filepath = os.path.join(
        repo_path,
        filename
    )

    if not os.path.exists(filepath):
        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:
            file.write("GitBloom\n")

    return filepath


def create_commit(repo_path, filename, number, test_date):
    filepath = create_file_if_needed(
        repo_path,
        filename
    )

    meme = get_random_meme()

    with open(
        filepath,
        "a",
        encoding="utf-8"
    ) as file:
        file.write(f"Commit #{number} | Meme: {meme}\n")

    result = run_command(
        ["git", "add", filename],
        cwd=repo_path
    )

    if result.returncode != 0:
        return False

    env = os.environ.copy()
    date_str = test_date.strftime('%Y-%m-%dT%H:%M:%S')
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str

    result = run_command(
        ["git", "commit", "-m", COMMIT_MESSAGE],
        cwd=repo_path,
        env=env
    )

    return result.returncode == 0


def show_loading(message, duration=0.8):
    frames = [
        "⠋",
        "⠙",
        "⠹",
        "⠸",
        "⠼",
        "⠴",
        "⠦",
        "⠧",
        "⠇",
        "⠏"
    ]

    end_time = time.time() + duration
    index = 0

    while time.time() < end_time:
        frame = frames[index % len(frames)]

        sys.stdout.write(
            f"\r  {frame} {message}"
        )

        sys.stdout.flush()

        time.sleep(0.08)
        index += 1

    sys.stdout.write(
        "\r  ✓ " + message + " " * 10 + "\n"
    )

    sys.stdout.flush()


def show_progress(current, total):
    width = 40

    percentage = int(
        current / total * 100
    )

    filled = int(
        width * current / total
    )

    bar = (
        "█" * filled +
        "░" * (width - filled)
    )

    sys.stdout.write(
        f"\r  [{bar}] "
        f"{percentage:3d}%  "
        f"{current}/{total} commits"
    )

    sys.stdout.flush()


def push_repository(repo_path):
    print("\nPushing repository")

    result = run_command(
        ["git", "push"],
        cwd=repo_path
    )

    if result.returncode == 0:
        print("  ✓ Push completed")
        return True

    print("  ✗ Push failed")

    if result.stderr:
        print(result.stderr.strip())

    return False


def cleanup(repo_path):
    if not repo_path:
        return

    temp_root = os.path.dirname(repo_path)

    if os.path.exists(temp_root):
        shutil.rmtree(
            temp_root,
            ignore_errors=True
        )


def main():
    banner()

    print("Git repository commit generator")
    print()

    repository_url = get_repository_url()
    filename = get_filename()

    print()
    start_date = get_date_input("From date (DDMMYYYY): ")
    end_date = get_date_input("Till date (DDMMYYYY): ")

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    commit_count = get_commit_count()

    print()
    print("Configuration")
    print("-" * 40)
    print(f"Repository : {repository_url}")
    print(f"File       : {filename}")
    print(f"From Date  : {start_date.strftime('%d-%m-%Y')}")
    print(f"Till Date  : {end_date.strftime('%d-%m-%Y')}")
    print(f"Commits    : {commit_count}")
    print()

    confirmation = input(
        "Start? [y/N]: "
    ).strip().lower()

    if confirmation != "y":
        print("\nCancelled.")
        return

    repository_path = clone_repository(
        repository_url
    )

    if repository_path is None:
        return

    try:
        show_loading("Preparing")

        print("\nCreating commits\n")

        successful = 0

        for number in range(
            1,
            commit_count + 1
        ):
            test_date = random_date_between(start_date, end_date)

            if create_commit(
                repository_path,
                filename,
                number,
                test_date
            ):
                successful += 1

            show_progress(
                number,
                commit_count
            )

            time.sleep(0.05)

        print("\n")
        print("  Completed")
        print(
            f"  {successful}/{commit_count} "
            "commits created"
        )

        if successful == 0:
            return

        print()

        push = input(
            "Push commits to remote? [y/N]: "
        ).strip().lower()

        if push == "y":
            push_repository(
                repository_path
            )
        else:
            print("  Commits remain local")

    finally:
        cleanup(repository_path)

    print("\nGitBloom finished.")


if __name__ == "__main__":
    main()