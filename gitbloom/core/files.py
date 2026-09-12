import os
import shutil


def copy_folder(source, destination):
    for root, dirs, names in os.walk(source):
        dirs[:] = [d for d in dirs if d != ".git"]
        relative = os.path.relpath(root, source)
        target_root = destination if relative == "." else os.path.join(destination, relative)
        os.makedirs(target_root, exist_ok=True)
        for name in names:
            shutil.copy2(os.path.join(root, name), os.path.join(target_root, name))


def copy_files(files, source_root, destination):
    for source_file in files:
        relative = os.path.relpath(source_file, source_root) if source_root else os.path.basename(source_file)
        target = os.path.join(destination, relative)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(source_file, target)


def cleanup(path):
    if path:
        shutil.rmtree(path, ignore_errors=True)
