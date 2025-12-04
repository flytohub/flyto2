#!/usr/bin/env python3
"""Debug f-string issues"""

# Test if we can construct the prompt
module_name = "test.module"
problem = "Test problem"

try:
    with open("src/core/meta/enhanced_module_generator.py", "r") as f:
        content = f.read()

    # Find the prompt f-string start
    start_marker = 'prompt = f"""You are a SENIOR Python developer'
    start_idx = content.find(start_marker)

    if start_idx == -1:
        print("❌ Could not find prompt start")
        exit(1)

    print(f"Found prompt at index {start_idx}")

    # Try to extract just the problematic section
    # Let's search for lines with {{ and : together
    lines = content[start_idx:start_idx+10000].split('\n')

    print("\nSearching for problematic patterns...")
    for i, line in enumerate(lines[:100], start=1):
        # Look for {{something:something}}
        if '{{' in line and ':' in line:
            # Check if there's a colon that might be interpreted as format spec
            import re
            # Pattern: {{ followed by text with : but not inside quotes
            if re.search(r'\{\{[^}]*:[^}]*\}\}', line):
                print(f"Line {i}: {line.strip()}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
