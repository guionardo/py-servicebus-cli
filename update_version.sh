#!/bin/bash

CURRENT_VERSION=$(cat src/__init__.py | grep "version" | grep -Po '(\d{1,3}\.\d{1,3}\.\d{1,3})')
LAST_RELEASE=$([[ -e docs/last_release.txt ]] && cat docs/last_release.txt)
CURRENT_BRANCH=$(git symbolic-ref --short HEAD)

echo "Current version: $CURRENT_VERSION"
echo "Last release: $LAST_RELEASE"
echo "Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "develop" ]; then
    echo "You must change the branch to develop to create a new tag for release"
    exit 1
fi

semver=(${CURRENT_VERSION//./ })
MAJOR="${semver[0]}"
MINOR="${semver[1]}"
PATCH="${semver[2]}"

TYPE='patch'
for i in "$@"; do
    case $i in
    --major)
        TYPE='major'
        ;;
    --minor)
        TYPE='minor'
        ;;
    --patch)
        TYPE='patch'
        ;;
    esac
done

echo "Update version type: $TYPE"

case $TYPE in
major)
    ((MAJOR += 1))
    MINOR=0
    PATCH=0
    ;;
minor)
    ((MINOR += 1))
    PATCH=0
    ;;
patch)
    ((PATCH += 1))
    ;;

esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
echo "New version: $NEW_VERSION"

python -m unittest

if [ $? != 0 ]; then
    echo "Unit tests cannot fail to update version!"
    exit 1
fi

# Updating __version__
sed -i "s/${CURRENT_VERSION}/${NEW_VERSION}/" src/__init__.py
FILE_NEW_VERSION=$(cat src/__init__.py | grep "version" | grep -Po '(\d{1,3}\.\d{1,3}\.\d{1,3})')
if [ $FILE_NEW_VERSION == $CURRENT_VERSION ]; then
    echo "Failed to update __version__ of package"
    exit 1
else
    echo "src/__init__.py __version__='$NEW_VERSION'"
fi

# Update readme.md
bash build_readme.sh


# New Branch
RELEASE_BRANCH="release/v${NEW_VERSION}"
git checkout -b $RELEASE_BRANCH
git add README.md
git add src/__init__.py
git commit -m "New release v${NEW_VERSION}"
git tag v$NEW_VERSION
git push origin $RELEASE_BRANCH

echo $NEW_VERSION > docs/last_release.txt