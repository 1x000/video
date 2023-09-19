#!/bin/sh

# Checkout to a temporary branch
git checkout --orphan temp_branch

# Add all the files
git add -A

# Commit the changes
git commit -am "The latest commit"

# Delete the old branch
git branch -D main

# Rename the temporary branch to main
git branch -m main

# Finally, force update your repository
git push -f origin main
