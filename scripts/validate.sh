#!/bin/bash
# Workflow Validation Helper Script
# Simple wrapper around validate_workflow.yaml meta-workflow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Help message
show_help() {
    cat << EOF
Flyto2 Workflow Validation Tool

Usage:
  ./scripts/validate.sh <workflow_path> [options]

Options:
  --strict          Enable strict validation mode
  --help           Show this help message

Examples:
  # Validate a workflow
  ./scripts/validate.sh workflows/google_search.yaml

  # Strict validation
  ./scripts/validate.sh workflows/_generated/new_workflow.yaml --strict

  # Validate all generated workflows
  ./scripts/validate.sh workflows/_generated/*.yaml

Description:
  This script validates Flyto2 workflow YAML files by running the
  validate_workflow.yaml meta-workflow. It checks:

  - YAML syntax
  - Required fields
  - Module existence
  - Parameter schemas
  - Variable references
  - Security issues

Exit Codes:
  0 - Validation passed
  1 - Validation failed
  2 - Invalid usage
EOF
}

# Check if no arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No workflow path provided${NC}"
    echo ""
    show_help
    exit 2
fi

# Check for help flag
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

# Get workflow path
WORKFLOW_PATH="$1"
shift

# Check if file exists
if [ ! -f "$WORKFLOW_PATH" ]; then
    echo -e "${RED}Error: Workflow file not found: $WORKFLOW_PATH${NC}"
    exit 2
fi

# Parse options
STRICT="false"
while [ $# -gt 0 ]; do
    case "$1" in
        --strict)
            STRICT="true"
            shift
            ;;
        *)
            echo -e "${YELLOW}Warning: Unknown option: $1${NC}"
            shift
            ;;
    esac
done

# Print header
echo -e "${GREEN}Validating workflow: $WORKFLOW_PATH${NC}"
echo ""

# Run validation
python -m src.cli.main workflows/meta/validate_workflow.yaml \
    --param target="$WORKFLOW_PATH" \
    --param strict="$STRICT"

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Validation passed${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Validation failed${NC}"
    exit 1
fi
