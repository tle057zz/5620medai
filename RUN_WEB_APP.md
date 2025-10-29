# 🚀 How to Run Web App - Quick Reference

## 🎯 **FASTEST METHOD** - Use Local Venv (Recommended)

### First Time Setup (3 minutes):

```bash
# Run the automated setup script
cd /Users/thanhle/Library/CloudStorage/GoogleDrive-lenhothanh.nsl@gmail.com/.shortcut-targets-by-id/1Je2GU6cAmriwQ_9lhORCt8JeHBjH-2Yq/ELEC5620/Code/5620medai

./setup_local_venv.sh
```

This creates a virtual environment at `/Users/thanhle/venv_web_local` (on your local drive, not Google Drive).

---

### Every Time You Want to Run (30 seconds):

```bash
# 1. Activate local venv
source /Users/thanhle/venv_web_local/bin/activate

# 2. Navigate to web app
cd /Users/thanhle/Library/CloudStorage/GoogleDrive-lenhothanh.nsl@gmail.com/.shortcut-targets-by-id/1Je2GU6cAmriwQ_9lhORCt8JeHBjH-2Yq/ELEC5620/Code/5620medai/web_app

# 3. Run
python app.py
```

**Access at**: http://127.0.0.1:5000

---

## 🔑 Login Credentials

```
Patient:
- patient1 / password123
- patient2 / password123
- patient3 / password123

Doctor:
- dr.smith / password123
- dr.jones / password123
- dr.chen / password123

Admin:
- admin / password123
- it.admin / password123
```

---

## ⚡ Even Shorter Commands

Save this as an alias in your `~/.zshrc`:

```bash
# Add to ~/.zshrc
alias webapp='source /Users/thanhle/venv_web_local/bin/activate && cd /Users/thanhle/Library/CloudStorage/GoogleDrive-lenhothanh.nsl@gmail.com/.shortcut-targets-by-id/1Je2GU6cAmriwQ_9lhORCt8JeHBjH-2Yq/ELEC5620/Code/5620medai/web_app && python app.py'
```

Then just run:
```bash
webapp
```

---

## 🐛 Troubleshooting

### If setup_local_venv.sh fails:

**Manual setup:**
```bash
# Create venv
python3.11 -m venv /Users/thanhle/venv_web_local

# Activate
source /Users/thanhle/venv_web_local/bin/activate

# Install packages
cd /Users/thanhle/Library/CloudStorage/GoogleDrive-lenhothanh.nsl@gmail.com/.shortcut-targets-by-id/1Je2GU6cAmriwQ_9lhORCt8JeHBjH-2Yq/ELEC5620/Code/5620medai/web_app

pip install -r requirements_minimal.txt
```

### If port 5000 is busy:

```bash
# Kill existing process
lsof -ti:5000 | xargs kill -9

# Or use a different port
python app.py
# Then edit app.py line 1344: app.run(debug=True, host='0.0.0.0', port=5050)
```

### If AI features are disabled:

This is NORMAL with minimal install! You'll see:
```
⚠ AI Medical Pipeline unavailable
```

All web features still work:
- ✅ Login/authentication
- ✅ Insurance quotes (simulated)
- ✅ Financial assistance calculator
- ✅ All dashboards
- ✅ Database features
- ❌ Document upload/AI processing (disabled)

---

## 📊 What's Different in Local Venv?

| Feature | Google Drive venv_ai | Local venv_web_local |
|---------|---------------------|----------------------|
| **Startup time** | 60-120 seconds | 5-10 seconds |
| **Crashes** | Segmentation faults | No crashes |
| **Web features** | ✅ All work | ✅ All work |
| **AI document processing** | ✅ Works | ❌ Disabled |
| **Insurance quotes** | ✅ Works | ✅ Works |
| **Financial assistance** | ✅ Works | ✅ Works |
| **All dashboards** | ✅ Works | ✅ Works |

**Recommendation**: Use local venv for development/testing, Google Drive venv only if you need full AI pipeline.

---

## 🎯 Quick Start Commands

```bash
# First time
./setup_local_venv.sh

# Every time after
source /Users/thanhle/venv_web_local/bin/activate
cd web_app
python app.py

# Access: http://127.0.0.1:5000
```

**That's it!** 🚀


