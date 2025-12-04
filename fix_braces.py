#!/usr/bin/env python3
"""Fix doubled braces in the prompt"""

with open("src/core/meta/enhanced_module_generator.py", "r") as f:
    lines = f.readlines()

# Replace doubled braces in lines 181-411 (0-indexed: 180-410)
for i in range(180, min(411, len(lines))):
    # Replace {{ with { and }} with }
    lines[i] = lines[i].replace("{{", "{").replace("}}", "}")

with open("src/core/meta/enhanced_module_generator.py", "w") as f:
    f.writelines(lines)

print("✅ Fixed doubled braces in prompt")
