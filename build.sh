#!/bin/bash

serial_numbers=(0 1 2 3 4 5 6 7 8 9)

current_serial=${serial_numbers[-1]}
new_serial=$((current_serial + 1))

IFS='.' read -ra version_parts <<< "$current_version"
major=${version_parts[0]}
minor=${version_parts[1]}
patch=${version_parts[2]}

if ((new_serial == 0)); then
    ((minor += 1))
elif ((new_serial % 10 == 0)); then
    ((major += 1))
fi

new_version="$major.$minor.$patch"
echo "New version: $new_version"

setup_file="setup.py"
while IFS= read -r line; do
    if [[ $line == version=* ]]; then
        line="version='$new_version',"
    fi
    echo "$line"
done < "$setup_file" > temp_setup.py

mv temp_setup.py "$setup_file"

echo "setup.py file updated."
