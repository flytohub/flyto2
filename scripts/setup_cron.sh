#!/bin/bash
# Setup Cron Jobs for Flyto2 V4

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$(which python3)"

echo "========================================="
echo "Setup Flyto2 Cron Jobs"
echo "========================================="
echo ""
echo "Project: $PROJECT_DIR"
echo "Python: $PYTHON_BIN"
echo ""

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Backup existing crontab
crontab -l > /tmp/flyto2_crontab_backup.txt 2>/dev/null

# Generate new cron entries
CRON_FILE="/tmp/flyto2_cron.txt"

echo "# Flyto2 V4 Scheduled Tasks" > "$CRON_FILE"
echo "# Generated: $(date)" >> "$CRON_FILE"
echo "" >> "$CRON_FILE"

# Hourly debug analysis
echo "# Hourly: Debug Analysis" >> "$CRON_FILE"
echo "0 * * * * cd $PROJECT_DIR && $PYTHON_BIN scripts/run_scheduled_tasks.py --task debug >> logs/debug_cron.log 2>&1" >> "$CRON_FILE"
echo "" >> "$CRON_FILE"

# Daily catalog update (midnight)
echo "# Daily: Module Catalog Update" >> "$CRON_FILE"
echo "0 0 * * * cd $PROJECT_DIR && $PYTHON_BIN scripts/run_scheduled_tasks.py --task catalog >> logs/catalog_cron.log 2>&1" >> "$CRON_FILE"
echo "" >> "$CRON_FILE"

# Every 6 hours: Evolution tickets check
echo "# Every 6 hours: Evolution Tickets" >> "$CRON_FILE"
echo "0 */6 * * * cd $PROJECT_DIR && $PYTHON_BIN scripts/run_scheduled_tasks.py --task tickets >> logs/evolution_cron.log 2>&1" >> "$CRON_FILE"
echo "" >> "$CRON_FILE"

# Show what will be added
echo "Cron entries to be added:"
echo "========================================="
cat "$CRON_FILE"
echo "========================================="
echo ""

# Ask for confirmation
read -p "Add these cron jobs? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Append to existing crontab
    (crontab -l 2>/dev/null; cat "$CRON_FILE") | crontab -

    echo ""
    echo "[OK] Cron jobs added successfully"
    echo ""
    echo "View cron jobs: crontab -l"
    echo "Edit cron jobs: crontab -e"
    echo "Remove all: crontab -r"
else
    echo ""
    echo "Cancelled. No changes made."
fi

# Cleanup
rm -f "$CRON_FILE"
