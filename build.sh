#!/bin/bash
serial_numbers = [0, 1, 2, 3, 4, 5, 6, 7,8,9]

current_serial = serial_numbers[-1]
new_serial = current_serial + 1

major, minor, patch = map(int, current_version.split('.'))

if new_serial == 0:
    minor += 1
elif new_serial % 10 == 0:
    major += 1

new_version = f"{major}.{minor}.{patch}"
print(f"New version: {new_version}")

setup_file = "setup.py"
with open(setup_file, "r") as f:
    lines = f.readlines()

with open(setup_file, "w") as f:
    for line in lines:
        if line.startswith("version="):
            line = f'version="{new_version}",\n'
        f.write(line)

print("setup.py file updated.")