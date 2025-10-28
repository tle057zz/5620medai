# 🚨 URGENT: Remove Database Folder from GitHub (AWS Password Leaked)

**Date**: October 28, 2025  
**Issue**: Database folder with AWS credentials pushed to GitHub  
**Priority**: 🔴 **CRITICAL - Security Issue**

---

## ⚠️ IMPORTANT SECURITY STEPS

### Step 1: Change AWS Password IMMEDIATELY ⚡

**Before removing from GitHub, secure your AWS account:**

1. **Login to AWS Console**: https://aws.amazon.com/console/
2. **Change RDS Database Password**:
   - Go to RDS → Databases
   - Select your database
   - Click "Modify"
   - Change master password
   - Apply immediately

3. **Rotate Any Other Leaked Credentials**
   - API keys
   - Access tokens
   - Any other secrets in the database folder

**⚠️ WARNING**: Even after removing from GitHub, the old password is in the git history and may have been accessed by others!

---

## ✅ Step 2: Update `.gitignore` (DONE)

The `.gitignore` file has been updated to exclude:
```
# Database folder with sensitive credentials
database/
**/database/
*.sql
# Web app uploads
web_app/uploads/
**/uploads/
```

---

## 🔥 Step 3: Remove Database Folder from Git History

### Option A: Using git filter-branch (Recommended)

```bash
cd /Users/thanhle/Library/CloudStorage/GoogleDrive-lenhothanh.nsl@gmail.com/.shortcut-targets-by-id/1Je2GU6cAmriwQ_9lhORCt8JeHBjH-2Yq/ELEC5620/Code/5620medai

# 1. Remove database folder from all commits in history
git filter-branch --force --index-filter \
  'git rm -r --cached --ignore-unmatch database/' \
  --prune-empty --tag-name-filter cat -- --all

# 2. Remove from current working directory (but keep locally)
git rm -r --cached database/

# 3. Clean up
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. Verify database is not tracked
git status
# Should show: database/ as untracked (red)

# 5. Add to .gitignore (already done)
git add .gitignore
git commit -m "chore: Add database folder to .gitignore (remove sensitive data)"
```

### Option B: Using BFG Repo-Cleaner (Faster, Easier)

```bash
# 1. Install BFG (if not installed)
brew install bfg

# 2. Create a fresh clone
cd ~/Desktop
git clone --mirror https://github.com/YOUR_USERNAME/5620medai.git

# 3. Remove database folder from history
cd 5620medai.git
bfg --delete-folders database

# 4. Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Push the cleaned history
git push --force

# 6. Go back to your working directory
cd /path/to/5620medai
git pull --force
```

---

## 🚀 Step 4: Force Push to GitHub

**⚠️ WARNING**: Force push will rewrite history. Notify collaborators!

```bash
# Push to GitHub (force push to overwrite history)
git push origin main --force

# Or if on a different branch:
git push origin YOUR_BRANCH --force

# Push to all branches
git push origin --force --all
git push origin --force --tags
```

---

## ✅ Step 5: Verify Removal from GitHub

1. **Go to GitHub repository**
2. **Check that `database/` folder is gone**
3. **Try searching for the password**:
   - Go to your repo on GitHub
   - Press `t` (search files)
   - Search for part of the password
   - Should find nothing

4. **Check git history**:
   ```bash
   git log --all --full-history --source --pretty=format:'%h %s' -- database/
   # Should be empty or show only the removal commit
   ```

---

## 📝 Step 6: Safe Commit (After Removal)

Now you can safely commit your other changes:

```bash
# Stage your changes (database is now ignored)
git add .

# Commit
git commit -m "feat: Complete UC-05 Financial Assistance + fix upload error handling"

# Push normally
git push origin main
```

---

## 🔒 Step 7: Prevent Future Leaks

### Create `.env` file for secrets

Create `web_app/.env` (this will be in `.gitignore`):
```env
# Database credentials
DB_HOST=your-rds-endpoint.amazonaws.com
DB_NAME=elec5620_db
DB_USER=admin
DB_PASSWORD=your-new-secure-password
DB_PORT=5432

# Flask secret
SECRET_KEY=your-flask-secret-key

# AWS credentials (if needed)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

### Update code to use environment variables

In `database/aws_database.py`, replace hardcoded values with:
```python
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', 5432))
}
```

### Add `.env` to `.gitignore`

Already added:
```gitignore
# Environment variables
.env
.env.local
.env.*.local
**/.env
```

---

## ⚡ Quick Reference Commands

### Remove database from git (all-in-one script)

```bash
#!/bin/bash
# Run from project root

echo "🔥 Removing database folder from git history..."

# Remove from history
git filter-branch --force --index-filter \
  'git rm -r --cached --ignore-unmatch database/' \
  --prune-empty --tag-name-filter cat -- --all

# Remove from staging
git rm -r --cached database/

# Clean up
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "✓ Database removed from git history"
echo "⚠️ Now run: git push origin main --force"
```

---

## 📋 Checklist

Security Actions:
- [ ] Change AWS RDS password immediately
- [ ] Rotate any other exposed credentials
- [ ] Review AWS CloudTrail logs for unauthorized access
- [ ] Consider enabling AWS GuardDuty

Git Actions:
- [x] Update `.gitignore` to exclude `database/`
- [ ] Remove `database/` from git history
- [ ] Force push to GitHub
- [ ] Verify removal on GitHub
- [ ] Search GitHub for leaked password (should find nothing)
- [ ] Create `.env` file for future credentials
- [ ] Install `python-dotenv`: `pip install python-dotenv`

Team Actions:
- [ ] Notify team about force push (if applicable)
- [ ] Team members need to re-clone or reset their repos
- [ ] Document the incident for future reference

---

## 🆘 If Team Members Have Old History

After force push, team members need to update:

```bash
# Option 1: Reset to match remote (loses local changes)
git fetch origin
git reset --hard origin/main

# Option 2: Re-clone (safest)
cd ..
mv 5620medai 5620medai_backup
git clone https://github.com/YOUR_USERNAME/5620medai.git
```

---

## ⚠️ Additional Security Recommendations

1. **Enable GitHub Secret Scanning**
   - Go to repo Settings → Security → Secret scanning
   - Enable alerts

2. **Add pre-commit hook** to prevent future leaks:
   ```bash
   # .git/hooks/pre-commit
   #!/bin/bash
   if git diff --cached --name-only | grep -q "database/"; then
       echo "ERROR: Attempting to commit database folder!"
       exit 1
   fi
   ```

3. **Use GitHub Secrets** for CI/CD
   - Never hardcode credentials
   - Use repository secrets

4. **Regular Security Audits**
   - Use tools like `gitleaks` or `truffleHog`
   - Run: `pip install gitleaks && gitleaks detect`

---

## 📞 Need Help?

If you encounter issues:

1. **Git filter-branch fails**:
   - Try BFG Repo-Cleaner (Option B)
   - Or create a new repo and copy clean files

2. **Force push rejected**:
   - Check branch protection rules on GitHub
   - Temporarily disable protection, push, re-enable

3. **Still see password on GitHub**:
   - Clear browser cache
   - Wait 5-10 minutes for GitHub to update
   - Contact GitHub support to request cache purge

---

## ✅ After Completion

Once done:
1. ✅ AWS password changed
2. ✅ Database folder removed from GitHub
3. ✅ `.gitignore` updated
4. ✅ Using `.env` for secrets
5. ✅ Can commit safely

**You're secure!** 🔒

---

**Last Updated**: October 28, 2025  
**Status**: Instructions ready - ACTION REQUIRED

