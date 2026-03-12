#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

VERSION="v$(date +%Y.%-m.%-d)"

echo "Releasing version: $VERSION"

if git tag | grep -q "^${VERSION}$"; then
    echo "Error: Tag $VERSION already exists"
    exit 1
fi

git tag -a "$VERSION" -m "Release $VERSION"

echo "Done! Created tag $VERSION"
echo "VERSION=$VERSION" > .release_version
