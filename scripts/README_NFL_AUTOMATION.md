# NFL Automated Data Gathering System

## Overview

This system automatically gathers NFL data without user interaction, running via cron jobs on your local machine. It tracks:

- Player/coach movements (insider connections)
- Betting line intelligence
- Injury reports
- Practice squad changes
- Social media mentions

## Quick Setup

```bash
# 1. Run setup script
./scripts/setup_nfl_automation.sh

# 2. Review the generated cron file
cat scripts/nfl_data_gathering.cron

# 3. Install cron jobs
crontab scripts/nfl_data_gathering.cron

# 4. Seed initial database
python scripts/seed_initial_data.py

# 5. Test the system
python Three_PointO_ArchE/nfl_automated_data_gatherer.py
```

## Automation Schedule

**Daily Tasks (4x per day):**
- **6 AM EST**: Transaction gathering (NFL.com)
- **8 AM EST**: Betting line updates
- **2 PM EST**: Practice report gathering
- **5 PM EST**: Final betting line update

**Weekly Tasks (Monday 6 AM EST):**
- Practice squad roster updates
- Coaching staff changes
- Advanced metrics updates

## Database Location

- **Path**: `data/nfl_insider_intelligence.db`
- **Type**: SQLite (self-contained, no server needed)

## Alerts System

The system creates alerts for:
- **High Priority**: Critical insider connections
- **Medium Priority**: Significant movements
- **Low Priority**: Routine updates

View alerts:
```python
from Three_PointO_ArchE.nfl_insider_database import NFLInsiderDatabase

db = NFLInsiderDatabase()
alerts = db.get_pending_alerts(priority='high')
for alert in alerts:
    print(f"[{alert['priority']}] {alert['message']}")
```

## Logs

- **Main log**: `logs/nfl_data_gatherer.log`
- **Cron log**: `logs/cron.log`

Monitor logs:
```bash
tail -f logs/nfl_data_gatherer.log
```

## Manual Testing

Test individual components:
```bash
# Test transaction scraper
python Three_PointO_ArchE/nfl_transaction_scraper.py

# Test database
python -c "from Three_PointO_ArchE.nfl_insider_database import NFLInsiderDatabase; db = NFLInsiderDatabase(); print('✅ Database OK')"

# Test full gathering
python Three_PointO_ArchE/nfl_automated_data_gatherer.py
```

## Customization

### Change Schedule

Edit `scripts/nfl_data_gathering.cron` and reinstall:
```bash
crontab scripts/nfl_data_gathering.cron
```

### Add Notification

Edit `nfl_automated_data_gatherer.py` `_send_notification()` method to add:
- Email notifications
- Slack webhooks
- SMS alerts
- Desktop notifications

### Add Data Sources

1. Create scraper in `Three_PointO_ArchE/nfl_*_scraper.py`
2. Add to `nfl_automated_data_gatherer.py`
3. Update cron schedule if needed

## Troubleshooting

**Cron jobs not running:**
```bash
# Check if cron is running
systemctl status cron  # Linux
# or
service cron status

# Check cron logs
grep CRON /var/log/syslog  # Linux
```

**Database errors:**
```bash
# Check database file
ls -lh data/nfl_insider_intelligence.db

# Test database connection
python -c "from Three_PointO_ArchE.nfl_insider_database import NFLInsiderDatabase; db = NFLInsiderDatabase(); print('OK')"
```

**Scraping failures:**
- Check internet connection
- Verify NFL.com is accessible
- Check for HTML structure changes (may need to update selectors)

## Maintenance

**Weekly:**
- Review alerts: `python -c "from Three_PointO_ArchE.nfl_insider_database import NFLInsiderDatabase; db = NFLInsiderDatabase(); print(len(db.get_pending_alerts()))"`
- Check logs for errors
- Verify data is being collected

**Monthly:**
- Review database size: `du -h data/nfl_insider_intelligence.db`
- Archive old data if needed
- Update scrapers if NFL.com structure changes

## Next Steps

1. **Phase 1**: Free sources (NFL.com scraping) - ✅ Implemented
2. **Phase 2**: Add API integrations (The Odds API, Twitter API)
3. **Phase 3**: Add notification system (email/Slack)
4. **Phase 4**: Add GitHub Actions for cloud-based automation

## Notes

- System runs completely autonomously
- No user interaction required
- Alerts notify you of important findings
- Database grows automatically
- All data is stored locally (privacy)
