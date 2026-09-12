#!/usr/bin/env bash
set -euo pipefail

# Build this script on Linux x86_64. PyInstaller does not cross-compile.
if [[ "$(uname -s)" != "Linux" ]]; then
  echo "Run packaging/build-linux.sh on Linux x86_64." >&2
  exit 1
fi
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build/linux-x86_64"
STAGE_DIR="$BUILD_DIR/stage"
VERSION="$(sed -n 's/^__version__ = "\(.*\)"/\1/p' "$PROJECT_ROOT/gitbloom/__init__.py")"
if [[ -z "$VERSION" ]]; then
  echo "Could not read the GitBloom version." >&2
  exit 1
fi
RELEASE_DIR="$PROJECT_ROOT/release/v$VERSION"

mkdir -p "$RELEASE_DIR" "$STAGE_DIR"
python3 -m pip install --upgrade pyinstaller
python3 -m PyInstaller \
  --noconfirm \
  --clean \
  --onefile \
  --windowed \
  --name "GitBloom" \
  --add-data "$PROJECT_ROOT/packaging/icons/GitBloom.png:packaging/icons" \
  --paths "$PROJECT_ROOT" \
  --distpath "$BUILD_DIR/dist" \
  --workpath "$BUILD_DIR/work" \
  --specpath "$BUILD_DIR" \
  "$PROJECT_ROOT/gitbloom/__main__.py"

rm -rf "$STAGE_DIR/AppDir"
mkdir -p "$STAGE_DIR/AppDir/usr/bin" "$STAGE_DIR/AppDir/usr/share/applications"
cp "$BUILD_DIR/dist/GitBloom" "$STAGE_DIR/AppDir/usr/bin/GitBloom"
cp "$PROJECT_ROOT/packaging/linux/AppRun" "$STAGE_DIR/AppDir/AppRun"
cp "$PROJECT_ROOT/packaging/linux/GitBloom.desktop" "$STAGE_DIR/AppDir/GitBloom.desktop"
cp "$PROJECT_ROOT/packaging/linux/GitBloom.desktop" "$STAGE_DIR/AppDir/usr/share/applications/GitBloom.desktop"
mkdir -p "$STAGE_DIR/AppDir/usr/share/icons/hicolor/scalable/apps"
cp "$PROJECT_ROOT/packaging/icons/GitBloom.svg" "$STAGE_DIR/AppDir/GitBloom.svg"
cp "$PROJECT_ROOT/packaging/icons/GitBloom.svg" "$STAGE_DIR/AppDir/usr/share/icons/hicolor/scalable/apps/GitBloom.svg"
chmod +x "$STAGE_DIR/AppDir/AppRun" "$STAGE_DIR/AppDir/usr/bin/GitBloom"

if command -v appimagetool >/dev/null 2>&1; then
  appimagetool "$STAGE_DIR/AppDir" "$RELEASE_DIR/GitBloom-Linux-x86_64.AppImage"
else
  echo "Skipping AppImage: install appimagetool to create GitBloom-Linux-x86_64.AppImage." >&2
  if [[ "${GITBLOOM_ONLY_APPIMAGE:-0}" == "1" ]]; then
    exit 1
  fi
fi

if [[ "${GITBLOOM_ONLY_APPIMAGE:-0}" == "1" ]]; then
  echo "Created Linux AppImage in $RELEASE_DIR (version $VERSION)"
  exit 0
fi

rm -rf "$STAGE_DIR/deb"
mkdir -p "$STAGE_DIR/deb/DEBIAN" "$STAGE_DIR/deb/usr/bin" "$STAGE_DIR/deb/usr/share/applications"
mkdir -p "$STAGE_DIR/deb/usr/share/icons/hicolor/scalable/apps"
cp "$BUILD_DIR/dist/GitBloom" "$STAGE_DIR/deb/usr/bin/GitBloom"
cp "$PROJECT_ROOT/packaging/linux/GitBloom.desktop" "$STAGE_DIR/deb/usr/share/applications/GitBloom.desktop"
cp "$PROJECT_ROOT/packaging/icons/GitBloom.svg" "$STAGE_DIR/deb/usr/share/icons/hicolor/scalable/apps/GitBloom.svg"
sed "s/@VERSION@/$VERSION/g" "$PROJECT_ROOT/packaging/linux/debian-control.in" > "$STAGE_DIR/deb/DEBIAN/control"
chmod 0755 "$STAGE_DIR/deb/usr/bin/GitBloom"
if command -v dpkg-deb >/dev/null 2>&1; then
  dpkg-deb --build "$STAGE_DIR/deb" "$RELEASE_DIR/gitbloom_amd64.deb" >/dev/null
else
  echo "Skipping Debian package: install dpkg-deb to create gitbloom_amd64.deb." >&2
fi

RPM_ROOT="$STAGE_DIR/rpm"
if command -v rpmbuild >/dev/null 2>&1; then
  rm -rf "$RPM_ROOT"
  mkdir -p "$RPM_ROOT/BUILD" "$RPM_ROOT/BUILDROOT" "$RPM_ROOT/RPMS" "$RPM_ROOT/SOURCES" "$RPM_ROOT/SPECS" "$RPM_ROOT/SRPMS"
  cp "$BUILD_DIR/dist/GitBloom" "$RPM_ROOT/SOURCES/GitBloom"
  cp "$PROJECT_ROOT/packaging/linux/GitBloom.desktop" "$RPM_ROOT/SOURCES/GitBloom.desktop"
  cp "$PROJECT_ROOT/packaging/icons/GitBloom.svg" "$RPM_ROOT/SOURCES/GitBloom.svg"
  sed "s/@VERSION@/$VERSION/g" "$PROJECT_ROOT/packaging/linux/gitbloom.spec.in" > "$RPM_ROOT/SPECS/gitbloom.spec"
  rpmbuild -bb \
    --define "_topdir $RPM_ROOT" \
    "$RPM_ROOT/SPECS/gitbloom.spec" >/dev/null
  RPM_FILE="$(find "$RPM_ROOT/RPMS" -type f -name 'gitbloom-*.rpm' | head -n 1)"
  cp "$RPM_FILE" "$RELEASE_DIR/gitbloom.x86_64.rpm"
else
  echo "Skipping RPM package: install rpmbuild to create gitbloom.x86_64.rpm." >&2
fi

echo "Created available Linux packages in $RELEASE_DIR (version $VERSION)"
