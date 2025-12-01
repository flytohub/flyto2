#!/bin/bash

# Run quality tests for modules and record results
# Usage: ./scripts/run_quality_tests.sh

echo "Module Quality Test Runner"
echo "=========================="
echo ""

# Test configurations
TESTS=(
    "data.json.parse:workflows/_test/test_json_parse.yaml"
    "data.json.stringify:workflows/_test/test_data_json_stringify.yaml"
    "string.split:workflows/_test/test_string_split.yaml"
    "string.replace:workflows/_test/test_string_replace.yaml"
    "string.trim:workflows/_test/test_string_trim.yaml"
    "string.lowercase:workflows/_test/test_string_lowercase.yaml"
    "string.uppercase:workflows/_test/test_string_uppercase.yaml"
    "array.map:workflows/_test/test_array_map.yaml"
    "array.filter:workflows/_test/test_array_filter.yaml"
    "array.sort:workflows/_test/test_array_sort.yaml"
    "array.join:workflows/_test/test_array_join.yaml"
    "array.unique:workflows/_test/test_array_unique.yaml"
    "math.round:workflows/_test/test_math_round.yaml"
    "math.abs:workflows/_test/test_math_abs.yaml"
    "object.keys:workflows/_test/test_object_keys.yaml"
    "object.merge:workflows/_test/test_object_merge.yaml"
)

RUNS=10
RESULTS_FILE="metrics/test_results_$(date +%Y%m%d_%H%M%S).txt"

# Create metrics directory if needed
mkdir -p metrics

echo "Running $RUNS tests for each module..."
echo "" > "$RESULTS_FILE"

for test_config in "${TESTS[@]}"; do
    IFS=':' read -r module_id test_file <<< "$test_config"

    echo ""
    echo "Testing: $module_id"
    echo "File: $test_file"
    echo "----------------------------------------"

    success=0
    fail=0

    for i in $(seq 1 $RUNS); do
        if python -m src.cli.main "$test_file" > /dev/null 2>&1; then
            success=$((success + 1))
            echo -n "."
        else
            fail=$((fail + 1))
            echo -n "x"
        fi
    done

    pass_rate=$(echo "scale=3; $success / $RUNS" | bc)

    echo ""
    echo "Results: $success/$RUNS passed (${pass_rate})"

    # Write to results file
    echo "$module_id,$success,$fail,$pass_rate" >> "$RESULTS_FILE"
done

echo ""
echo "========================================"
echo "Results saved to: $RESULTS_FILE"
echo ""
echo "Summary:"
cat "$RESULTS_FILE"
