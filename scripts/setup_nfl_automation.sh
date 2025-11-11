#!/bin/bash
# Setup script for NFL automated data gathering
# Creates cron jobs and initializes database

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_PATH="$PROJECT_ROOT/arche_env/bin/python"
GATHERER_SCRIPT="$PROJECT_ROOT/Three_PointO_ArchE/nfl_automated_data_gatherer.py"
LOG_DIR="$PROJECT_ROOT/logs"

# Create logs directory
mkdir -p "$LOG_DIR"

# Create cron job file
CRON_FILE="$PROJECT_ROOT/scripts/nfl_data_gathering.cron"

cat > "$CRON_FILE" << EOF
# NFL Automated Data Gathering
# Runs daily at 6 AM, 8 AM, 2 PM, and 5 PM EST

# Daily transaction gathering (6 AM EST = 11 AM UTC in winter, 10 AM UTC in summer)
0 11 * * * cd $PROJECT_ROOT && $PYTHON_PATH $GATHERER_SCRIPT >> $LOG_DIR/cron.log 2>&1

# Betting line updates (8 AM EST = 1 PM UTC)
0 13 * * * cd $PROJECT_ROOT && $PYTHON_PATH $GATHERER_SCRIPT >> $LOG_DIR/cron.log 2>&1

# Practice report gathering (2 PM EST = 7 PM UTC)
0 19 * * * cd $PROJECT_ROOT && $PYTHON_PATH $GATHERER_SCRIPT >> $LOG_DIR/cron.log 2>&1

# Final betting line update (5 PM EST = 10 PM UTC)
0 22 * * * cd $PROJECT_ROOT && $PYTHON_PATH $GATHERER_SCRIPT >> $LOG_DIR/cron.log 2>&1

# Weekly tasks (Monday 6 AM EST = 11 AM UTC)
0 11 * * 1 cd $PROJECT_ROOT && $PYTHON_PATH $GATHERER_SCRIPT >> $LOG_DIR/cron.log 2>&1
EOF

echo "✅ Cron job file created: $CRON_FILE"
echo ""
echo "To install cron jobs, run:"
echo "  crontab $CRON_FILE"
echo ""
echo "To view current cron jobs:"
echo "  crontab -l"
echo ""
echo "To remove cron jobs:"
echo "  crontab -r"
echo ""

# Initialize database
echo "Initializing database..."
cd "$PROJECT_ROOT"
$PYTHON_PATH -c "
from Three_PointO_ArchE.nfl_insider_database import NFLInsiderDatabase
db = NFLInsiderDatabase()
print('✅ Database initialized')
db.close()
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Review cron job file: $CRON_FILE"
echo "2. Install cron jobs: crontab $CRON_FILE"
echo "3. Check logs: tail -f $LOG_DIR/nfl_data_gatherer.log"

