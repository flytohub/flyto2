#!/usr/bin/env python3
"""Re-double the braces for .format()"""

with open("src/core/meta/enhanced_module_generator.py", "r") as f:
    lines = f.readlines()

# Re-double braces in lines 181-411 (0-indexed: 180-410)
for i in range(180, min(411, len(lines))):
    # Replace { with {{ and } with }} (but not if already doubled)
    lines[i] = lines[i].replace("{", "{{").replace("}", "}}")
    # Fix the .format() line which shouldn't have doubled braces
    if ".format(" in lines[i]:
        # Undo the doubling for the .format call itself
        lines[i] = lines[i].replace("{{module_name}}", "{module_name}").replace("{{problem}}", "{problem}")

with open("src/core/meta/enhanced_module_generator.py", "w") as f:
    f.writelines(lines)

print("✅ Re-doubled braces for .format()")
