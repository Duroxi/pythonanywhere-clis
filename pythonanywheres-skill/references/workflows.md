# Workflow Examples

Step-by-step examples for common tasks.

## Table of Contents

- [Deploy a Website](#deploy-a-website)
- [Manage Files](#manage-files)
- [Manage Console](#manage-console)
- [Manage Web App](#manage-web-app)
- [Manage Tasks](#manage-tasks)
- [Multi-Account Management](#multi-account-management)
- [Extend Account Expiry](#extend-account-expiry)

---

## Deploy a Website

### Basic Deployment

```bash
# 1. Configure account (first time only)
pa init

# 2. Deploy project
pa deploy ./my-site

# 3. Visit your site
# https://yourusername.pythonanywhere.com
```

### Deploy with Custom Domain

```bash
pa deploy ./my-site --domain mysite.pythonanywhere.com
```

### Deploy with Specific Python Version

```bash
pa deploy ./my-site --python python311
```

### Preview Deployment

```bash
pa deploy ./my-site --dry-run
```

### Manual Deployment (Step by Step)

```bash
# 1. Upload files
pa files upload ./myproject /home/myuser/myproject -r

# 2. Create console
pa console create

# 3. Activate console
pa console activate 12345

# 4. Setup virtual environment
pa console send 12345 "cd /home/myuser/myproject"
pa console send 12345 "mkvirtualenv myproject --python=/usr/bin/python310"
pa console send 12345 "workon myproject && pip install -r requirements.txt"

# 5. Create web app
pa webapp create myuser.pythonanywhere.com

# 6. Configure source directory
pa webapp config myuser.pythonanywhere.com -s /home/myuser/myproject

# 7. Add static files
pa webapp static myuser.pythonanywhere.com --url /static/ --path /home/myuser/myproject/static

# 8. Reload web app
pa webapp reload myuser.pythonanywhere.com
```

---

## Manage Files

### Upload Files

```bash
# Upload single file
pa files upload ./app.py /home/myuser/app.py

# Upload directory
pa files upload ./myproject /home/myuser/myproject -r

# Upload to root
pa files upload ./config.json /home/myuser/config.json
```

### Download Files

```bash
# Download single file
pa files download /home/myuser/app.py ./app.py

# Download directory
pa files download /home/myuser/myproject ./myproject -r
```

### List Files

```bash
# List root directory
pa files ls

# List subdirectory
pa files ls myproject
```

### Delete Files

```bash
# Delete file
pa files rm /home/myuser/old.txt

# Delete directory
pa files rm /home/myuser/old_project -r -f
```

### Share Files

```bash
# Share file
pa files share /home/myuser/data.csv
# Output: Share link: https://www.pythonanywhere.com/user/myuser/shares/abc123/

# Check share status
pa files share-status /home/myuser/data.csv

# Stop sharing
pa files unshare /home/myuser/data.csv
```

---

## Manage Console

### Create and Use Console

```bash
# 1. Create console
pa console create
# Output: Console created: id=12345, executable=bash

# 2. Activate console
pa console activate 12345

# 3. Send commands
pa console send 12345 "ls -la"
pa console send 12345 "python --version"

# 4. Clean up
pa console kill 12345
```

### Smart Console Management

```bash
# Get existing or create new
pa console get-or-create

# With custom executable
pa console get-or-create -e python3.10
```

### Long-Running Commands

```bash
# With custom timeout
pa console send 12345 "pip install flask" --timeout 120

# Without waiting
pa console send 12345 "long-running-command" --no-wait
```

---

## Manage Web App

### Create and Configure Web App

```bash
# 1. Create web app
pa webapp create mysite.pythonanywhere.com

# 2. Configure source directory
pa webapp config mysite -s /home/user/mysite

# 3. Configure virtualenv
pa webapp config mysite -v /home/user/.virtualenvs/mysite

# 4. Add static files
pa webapp static mysite --url /static/ --path /home/user/mysite/static

# 5. Reload app
pa webapp reload mysite.pythonanywhere.com
```

### View Logs

```bash
# View error logs
pa webapp logs --type error --lines 20

# View access logs
pa webapp logs --type access --lines 50

# View server logs
pa webapp logs --type server
```

### Check Traffic

```bash
pa webapp hits mysite.pythonanywhere.com
```

### Enable/Disable App

```bash
# Disable app
pa webapp disable mysite.pythonanywhere.com

# Enable app
pa webapp enable mysite.pythonanywhere.com
```

### Delete App

```bash
pa webapp delete mysite.pythonanywhere.com
```

### Check SSL

```bash
pa webapp ssl mysite.pythonanywhere.com
```

---

## Manage Tasks

### Create Scheduled Tasks

```bash
# Daily backup at 2 AM
pa tasks create "python /home/user/backup.py" --interval daily --hour 2 --minute 0

# Hourly health check
pa tasks create "curl https://api.example.com/health" --interval hourly

# Weekly report
pa tasks create "python /home/user/report.py" --interval weekly --hour 9 --minute 0

# With description
pa tasks create "python /home/user/cleanup.py" --interval daily --hour 3 --description "Daily cleanup"
```

### Manage Tasks

```bash
# List all tasks
pa tasks list

# Disable task
pa tasks disable 12345

# Enable task
pa tasks enable 12345

# Delete task
pa tasks delete 12345 -f
```

### Create Always-on Tasks (Paid)

```bash
# Create webhook server
pa always-on create "python /home/user/webhook_server.py"

# List tasks
pa always-on list

# Delete task
pa always-on delete 789 -f
```

---

## Multi-Account Management

### Add Multiple Accounts

```bash
# Add first account
pa init

# Add second account
pa init
```

### Switch Accounts

```bash
# List accounts
pa account list
# Output:
# * user1    www.pythonanywhere.com    token: abc12345...
#   user2    www.pythonanywhere.com    token: def67890...

# Switch to user2
pa account switch user2

# Deploy under user2
pa deploy ./my-site
```

### Remove Account

```bash
pa account remove user1
```

---

## Extend Account Expiry

Free accounts expire after a period. Extend to keep active.

```bash
# 1. Store password (first time only)
pa account login

# 2. Extend expiry
pa account extend
```

---

## Common Command Sequences

### Fresh Project Setup

```bash
pa init
pa deploy ./my-project
```

### Update Existing Project

```bash
pa files upload ./app.py /home/myuser/myproject/app.py
pa webapp reload myuser.pythonanywhere.com
```

### Debug Web App

```bash
pa webapp logs --type error --lines 50
pa console get-or-create
pa console send 12345 "cd /home/myuser/myproject && python app.py"
```

### Backup Project

```bash
pa files download /home/myuser/myproject ./backup/myproject -r
```

### Monitor Resources

```bash
pa status cpu
pa status disk
pa webapp hits myuser.pythonanywhere.com
```
