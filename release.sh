#!/usr/bin/env bash
# release.sh - bump version, build, and upload to PyPI
# Usage: ./release.sh [new_version]

set -euo pipefail

# Check dependencies
command -v git >/dev/null 2>&1 || { echo "git is required"; exit 1; }
command -v sed >/dev/null 2>&1 || { echo "sed is required"; exit 1; }
command -v rm >/dev/null 2>&1 || { echo "rm is required"; exit 1; }
command -v python >/dev/null 2>&1 || { echo "python is required"; exit 1; }
command -v twine >/dev/null 2>&1 || { echo "twine is required"; exit 1; }

# Determine new version
if [ $# -eq 1 ]; then
  NEW_VERSION=$1
else
  # Auto-increment patch version in pyproject.toml
  CURRENT_VERSION=$(grep -E '^version\s*=\s*"' pyproject.toml | sed -E 's/version\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"/\1/')
  IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"
  PATCH=$((PATCH + 1))
  NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
fi

echo "Releasing version $NEW_VERSION"

# Update pyproject.toml
sed -i.bak -E "s/^version = \"[0-9]+\.[0-9]+\.[0-9]+\"/version = \"${NEW_VERSION}\"/" pyproject.toml
rm pyproject.toml.bak

# Commit version bump
git add pyproject.toml
git commit -m "Bump version to $NEW_VERSION"

echo "Building distributions..."
# Clean previous builds
rm -rf build dist *.egg-info

# Build
env python -m build

echo "Uploading to PyPI..."
twine upload dist/*

echo "Tagging Git..."
git tag v$NEW_VERSION
git push origin --tags

echo "Release $NEW_VERSION complete!"