#!/usr/bin/env bash
set -euo pipefail

# Build this script on macOS. PyInstaller builds for the OS it runs on.
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Run packaging/build-macos.sh on macOS. PyInstaller does not cross-compile." >&2
  exit 1
fi
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(sed -n 's/^__version__ = "\(.*\)"/\1/p' "$PROJECT_ROOT/gitbloom/__init__.py")"
if [[ -z "$VERSION" ]]; then
  echo "Could not read the GitBloom version." >&2
  exit 1
fi
RELEASE_DIR="$PROJECT_ROOT/release/v$VERSION"
BUILD_DIR="$PROJECT_ROOT/build/macos"
ICON_PNG="$PROJECT_ROOT/packaging/icons/GitBloom.png"
ICONSET_DIR="$BUILD_DIR/GitBloom.iconset"
ICON_ICNS="$BUILD_DIR/GitBloom.icns"

mkdir -p "$RELEASE_DIR"
rm -rf "$ICONSET_DIR"
mkdir -p "$ICONSET_DIR"
if ! command -v sips >/dev/null 2>&1 || ! command -v iconutil >/dev/null 2>&1; then
  echo "macOS sips and iconutil are required to create the application icon." >&2
  exit 1
fi
for size in 16 32 128 256 512; do
  sips -z "$size" "$size" "$ICON_PNG" --out "$ICONSET_DIR/icon_${size}x${size}.png" >/dev/null
  double_size=$((size * 2))
  sips -z "$double_size" "$double_size" "$ICON_PNG" --out "$ICONSET_DIR/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET_DIR" -o "$ICON_ICNS"

python3 -m pip install --upgrade pyinstaller
python3 -m PyInstaller \
  --noconfirm \
  --clean \
  --onedir \
  --windowed \
  --name "GitBloom-macOS" \
  --icon "$ICON_ICNS" \
  --add-data "$PROJECT_ROOT/packaging/icons/GitBloom.png:packaging/icons" \
  --paths "$PROJECT_ROOT" \
  --distpath "$BUILD_DIR/dist" \
  --workpath "$BUILD_DIR" \
  --specpath "$BUILD_DIR" \
  "$PROJECT_ROOT/gitbloom/__main__.py"

if ! command -v hdiutil >/dev/null 2>&1; then
  echo "hdiutil is required to create the macOS DMG." >&2
  exit 1
fi
if [[ ! -d "$BUILD_DIR/dist/GitBloom-macOS.app" ]]; then
  echo "PyInstaller did not create GitBloom-macOS.app." >&2
  find "$BUILD_DIR/dist" -maxdepth 2 -print >&2 || true
  exit 1
fi

rm -f "$RELEASE_DIR/GitBloom-macOS.dmg"
hdiutil create \
  -volname "GitBloom" \
  -srcfolder "$BUILD_DIR/dist/GitBloom-macOS.app" \
  -ov \
  -format UDZO \
  "$RELEASE_DIR/GitBloom-macOS.dmg" >/dev/null

echo "Created $RELEASE_DIR/GitBloom-macOS.dmg (version $VERSION)"
