#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

VERSION="v$(date +%Y.%-m.%-d)"

echo "Releasing version: $VERSION"

if git tag | grep -q "^${VERSION}$"; then
    echo "Error: Tag $VERSION already exists"
    exit 1
fi

sed -i "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml

git add pyproject.toml
git commit -m "Release $VERSION"

git tag -a "$VERSION" -m "Release $VERSION"

echo "Done! Created release $VERSION"
echo "Run 'git push' to push the commit and tags to remote"
