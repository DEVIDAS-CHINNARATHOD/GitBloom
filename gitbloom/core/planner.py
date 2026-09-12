import os
from datetime import timedelta


def collect_files(folder):
    files = []
    for root, dirs, names in os.walk(folder):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in names:
            files.append(os.path.relpath(os.path.join(root, name), folder))
    return sorted(files)


def distribute_files(files, count):
    count = min(max(1, count), len(files))
    groups = [[] for _ in range(count)]
    for index, filename in enumerate(files):
        groups[index % count].append(filename)
    return [group for group in groups if group]


def distribute_dates(start, days, count):
    if count == 1:
        return [start]
    return [start + timedelta(days=round(days * i / (count - 1))) for i in range(count)]


def message_for(files):
    if not files:
        return "Update project"
    if len(files) == 1:
        return f"Update {os.path.basename(files[0])}"
    return f"Update {len(files)} project files"


def build_plan(files, start, days, commit_count):
    groups = distribute_files(files, commit_count)
    dates = distribute_dates(start, days, len(groups))
    return [
        {
            "number": index + 1,
            "date": dates[index],
            "files": group,
            "message": message_for(group),
        }
        for index, group in enumerate(groups)
    ]
