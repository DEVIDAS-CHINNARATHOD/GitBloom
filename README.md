# GitBloom V2

GitBloom is a cross-platform desktop application for creating an organized Git commit timeline from a project folder or selected files.

## Features

- Select a complete folder and scan files recursively.
- Select multiple individual files.
- Automatically set the number of commits to the number of selected files.
- Edit the automatically suggested commit count.
- Enter a start date.
- Adjust the end date with the slider without changing the commit count; the maximum range is the number of commits.
- Preview the complete commit plan before changing the repository.
- Generate commit messages from the planned files.
- Show progress while processing.
- Ask for confirmation before pushing.
- Use a remote repository URL only.

## Requirements

- Python 3.10 or newer
- Git installed and available on PATH
- Tkinter
- PyInstaller for building releases

## Run from source

```bash
python -m gitbloom
```

On Linux, install your distribution's Tkinter package if it is not already installed.

## Build releases

Build each desktop package on its native operating system. PyInstaller does not cross-compile between Windows, macOS, and Linux.

All final artifacts are written to one versioned folder such as `release/v2.1.0/`. The version is read from `gitbloom/__init__.py`, so every package uses the same version. Build output, temporary files, Python caches, and local editor files are excluded by `.gitignore`.

### Windows x64

Run in PowerShell from the project root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\packaging\build-windows.ps1
```

Output:

```text
release/v2.1.0/GitBloom-Windows-x64.exe
```

### macOS

Run in Terminal on macOS:

```bash
chmod +x packaging/build-macos.sh
./packaging/build-macos.sh
```

Output:

```text
release/v2.1.0/GitBloom-macOS.dmg
```

### Linux x86_64

For the AppImage-only release used by the cross-platform workflow, install `appimagetool`. Debian and RPM packages are optional local outputs and require `dpkg-deb` and `rpmbuild`.

```bash
chmod +x packaging/build-linux.sh
./packaging/build-linux.sh
```

Outputs:

```text
release/v2.1.0/GitBloom-Linux-x86_64.AppImage
release/v2.1.0/gitbloom_amd64.deb
release/v2.1.0/gitbloom.x86_64.rpm
```

The script always creates the AppImage and Debian package when their tools are installed. If `rpmbuild` is unavailable, it creates the first two packages and reports that the RPM could not be created.

### Build all three apps with one command

Windows, macOS, and Linux packages must be built on their native operating systems. The included GitHub Actions workflow builds all three automatically and produces exactly these files in one versioned release folder:

```text
GitBloom-Windows-x64.exe
GitBloom-macOS.dmg
GitBloom-Linux-x86_64.AppImage
```

Push this project to GitHub, authenticate with GitHub CLI, then run from the project root:

```bash
gh workflow run build-release.yml --ref main
```

Open the completed `GitBloom-release` workflow artifact and download the three files together. The workflow is also started automatically when a `v*` tag is pushed.

## GitHub release upload

Upload all files from the versioned `release/v2.1.0/` folder as GitHub Release assets using these names:

- Windows x64: `GitBloom-Windows-x64.exe`
- macOS: `GitBloom-macOS.dmg`
- Linux x64: `GitBloom-Linux-x86_64.AppImage`
- Debian/Ubuntu: `gitbloom_amd64.deb`
- Fedora/RHEL: `gitbloom.x86_64.rpm`

Do not upload `build/`, `dist/`, `__pycache__/`, or other temporary files.

## Project layout

```text
gitbloom/                 Application source
packaging/                Platform build scripts and Linux package metadata
packaging/icons/          GitBloom application icon assets
release/v<version>/       Final release artifacts (generated, ignored by Git)
```
