# 🔧 Upload Feature Troubleshooting Guide

## Issue: "No data left in file" Error

### ✅ Verified Working
The sample PDF (`samples/sample_medical_report_1.pdf`) works correctly when accessed directly.

### 🔍 Common Causes

1. **File Upload from Desktop Issues**
   - File might be getting corrupted during upload
   - File might not be fully written before processing
   - Browser security restrictions

2. **File Path Issues**
   - Incorrect upload folder permissions
   - File being deleted too early

3. **PDF Library Issues**
   - Missing dependencies
   - Incompatible PDF format

---

## 🧪 Test 1: Verify Upload Folder

```bash
cd /path/to/5620medai/web_app
ls -la uploads/
# Should show directory with write permissions
```

If folder doesn't exist:
```bash
mkdir -p uploads
chmod 755 uploads
```

---

## 🧪 Test 2: Test with Sample PDF (Copy Method)

Instead of uploading from desktop:

1. **Copy sample PDF to desktop**:
   ```bash
   cp samples/sample_medical_report_1.pdf ~/Desktop/test_medical.pdf
   ```

2. **Upload from desktop** in the web app

3. **Check server logs** for exact error message

---

## 🧪 Test 3: Direct File Test

Run this test script:

```bash
cd web_app
source ../venv_ai/bin/activate
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

from medical_document_processor import process_uploaded_document

# Test with sample file
result = process_uploaded_document('../samples/sample_medical_report_1.pdf')

print("\n=== TEST RESULT ===")
print(f"Success: {result['success']}")
if result['success']:
    print(f"Conditions: {result['conditions']}")
    print(f"Medications: {result['medications']}")
    print(f"Text length: {len(result['raw_text'])} chars")
else:
    print(f"Error: {result.get('error', 'Unknown error')}")
EOF
```

---

## 🧪 Test 4: Check Browser Upload

### In Browser DevTools (F12 → Network tab):

1. Upload a file
2. Check the POST request to `/insurance/request-quote`
3. Look at "Form Data" - verify file is included
4. Check response for error details

### In Server Terminal:

Watch for these debug messages:
```
✓ Processing uploaded document: [filename]
  → File: [filename] ([size] bytes)
  → Extracted [chars] characters from PDF
```

---

## 🔧 Quick Fixes

### Fix 1: Increase Upload Size Limit

In `app.py`, check this line (should be present):
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

### Fix 2: Ensure File Persists

The issue might be that `uploaded_file.save()` needs to flush:

In `app.py` around line 251, after `uploaded_file.save(file_path)`, add:
```python
uploaded_file.save(file_path)
# Ensure file is written before processing
import time
time.sleep(0.1)  # Small delay to ensure file is fully written
```

### Fix 3: Add Debugging

Add this right after file save in `app.py`:
```python
uploaded_file.save(file_path)

# Debug
import os
print(f"✓ File saved: {file_path}")
print(f"  Exists: {os.path.exists(file_path)}")
print(f"  Size: {os.path.getsize(file_path)} bytes")
```

---

## 📝 Updated Error Messages

The code has been updated with better error messages. You should now see one of:

- ✅ "Uploaded file is empty (0 bytes)" - File uploaded but empty
- ✅ "File not found: [path]" - File wasn't saved correctly  
- ✅ "PDF extraction failed: [error]" - PDF library error (detailed)
- ✅ "Error reading text file: [error]" - Text file read error
- ✅ "No text extracted from document" - PDF processed but empty

---

## 🎯 Recommended Testing Flow

1. **Test with provided sample PDF first**:
   - Use `samples/sample_medical_report_1.pdf` directly from the samples folder
   - Upload via the web interface
   - Check if it works

2. **If sample works but desktop upload fails**:
   - Copy the sample PDF to desktop
   - Try uploading the copied version
   - Compare behavior

3. **Check server logs carefully**:
   - Look for the exact error message
   - Note the file size reported
   - Check if file exists message

4. **Try text file instead**:
   - Use `samples/sample_medical_report_1.txt`
   - This bypasses PDF parsing
   - Helps isolate the issue

---

## 🚨 If Still Failing

Try this workaround in `app.py`:

```python
# Around line 251, replace:
uploaded_file.save(file_path)

# With:
try:
    uploaded_file.save(file_path)
    
    # Verify file was saved
    if not os.path.exists(file_path):
        flash('File upload failed: File not saved', 'danger')
        return render_template('insurance_quote_form.html', form=form, ai_medical_available=AI_MEDICAL_AVAILABLE)
    
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        flash('File upload failed: Empty file (0 bytes)', 'danger')
        return render_template('insurance_quote_form.html', form=form, ai_medical_available=AI_MEDICAL_AVAILABLE)
    
    print(f"✓ File uploaded successfully: {filename} ({file_size} bytes)")
    
except Exception as save_err:
    print(f"✗ File save error: {save_err}")
    flash(f'File upload failed: {str(save_err)}', 'danger')
    return render_template('insurance_quote_form.html', form=form, ai_medical_available=AI_MEDICAL_AVAILABLE)
```

---

## ✅ Expected Behavior (Working State)

When upload works correctly, you should see in terminal:

```
✓ Processing uploaded document: sample_medical_report_1.pdf
  → File: sample_medical_report_1.pdf (3757 bytes)
Step 1: Extracting text from document...
  → Extracted 1046 characters from PDF
Step 2: Sectionizing document...
  → Found 5 sections
Step 3: Extracting medical entities...
  → Extracted 8 entities
✓ Extracted: ['Type 2 Diabetes Mellitus', 'Essential Hypertension', ...], ['Metformin', 'Lisinopril', ...]
```

And in browser:
```
✓ Document processed! Extracted 3 conditions and 2 medications.
```

---

## 📞 Still Need Help?

1. Copy the **exact error message** from the browser
2. Copy the **terminal output** from the server
3. Run **Test 3** above and share results
4. Check if `uploads/` folder exists and has permissions

Good luck! 🍀

