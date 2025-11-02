# 🏥 Clinical AI Assistance System - Web Application

Flask-based web interface for the Clinical AI Medical Document Intelligence Pipeline.

https://uni-team-p5cfc6he.atlassian.net/jira/software/projects/SCRUM/boards/1


## 📋 Features

### ✅ Implemented (Phase 1)

- **User Authentication System**
  - Secure login with Flask-Login
  - Session management
  - Password hashing with Werkzeug
  
- **Role-Based Access Control (RBAC)**
  - **Doctor**: Access to AI processing tools, patient records
  - **Patient**: View personal medical records and AI analysis
  - **Admin**: System management, user administration
  
- **Role-Specific Dashboards**
  - Doctor Dashboard: Document upload, patient search, AI pipeline access
  - Patient Dashboard: Medical records view, health summary
  - Admin Dashboard: User management, system monitoring

- **Example Users** (In-Memory Storage)
  - Ready-to-use demo accounts for testing
  - All roles pre-configured

### 🚧 Coming Soon (Future Phases)

- Database integration (SQLite/PostgreSQL)
- Document upload and AI pipeline integration
- Real-time processing status
- Patient record management
- FHIR data visualization
- API endpoints for external systems

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# From the web_app directory
cd web_app
pip install -r requirements_flask.txt
```

### 2. Run the Application

```bash
python app.py
```

The server will start at: **http://127.0.0.1:5000**

---

## 👥 Demo Credentials

### Password for All Users
```
password123
```

### User Accounts

| Role | Username | Description |
|------|----------|-------------|
| **Doctor** | `dr.smith` | Cardiology specialist |
| **Doctor** | `dr.jones` | Neurology specialist |
| **Doctor** | `dr.chen` | General medicine |
| **Patient** | `patient1` | John Doe (MRN-001234) |
| **Patient** | `patient2` | Jane Wilson (MRN-005678) |
| **Patient** | `patient3` | Robert Taylor (MRN-009876) |
| **Admin** | `admin` | System administrator |
| **Admin** | `it.admin` | IT administrator |

---

## 📁 Project Structure

```
web_app/
│
├── app.py                  # Main Flask application
├── models.py               # User models (in-memory)
├── forms.py                # Flask-WTF forms
├── requirements_flask.txt  # Python dependencies
├── README.md              # This file
│
├── templates/             # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── login.html        # Login page
│   ├── dashboard_doctor.html
│   ├── dashboard_patient.html
│   ├── dashboard_admin.html
│   ├── users_list.html   # User management
│   ├── 404.html          # Error pages
│   ├── 403.html
│   └── 500.html
│
└── static/               # Static files
    └── css/
        └── style.css     # Custom styles
```

---

## 🔐 Security Features

- **Password Hashing**: Using Werkzeug's secure password hashing
- **Session Management**: Flask-Login for secure session handling
- **CSRF Protection**: Flask-WTF forms with CSRF tokens
- **Role-Based Access**: Decorators prevent unauthorized access
- **Secure Cookies**: Session cookies with HTTPOnly flag

---

## 🎨 User Interface

- **Bootstrap 5**: Modern, responsive design
- **Bootstrap Icons**: Comprehensive icon set
- **Custom Styling**: Professional medical interface
- **Mobile Responsive**: Works on all devices

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `web_app` directory:

```bash
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

### Security Note

⚠️ The current implementation uses in-memory storage with demo credentials. 
**DO NOT use in production without:**
- Implementing proper database storage
- Changing default passwords
- Adding rate limiting
- Implementing audit logging
- Enabling HTTPS
- Following HIPAA compliance guidelines

---

## 🔌 API Endpoints (Planned)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/process-document` | POST | Process medical document | Doctor, Admin |
| `/api/get-patient-records` | GET | Retrieve patient records | All authenticated |
| `/api/users` | GET | List all users | Admin only |

---

## 📊 Integration with AI Pipeline

The web application is designed to integrate with the AI medical pipeline:

1. **OCR Stage** → Document text extraction
2. **Sectionizer** → Document structure analysis
3. **NER** → Entity recognition
4. **Entity Linking** → Medical ontology mapping
5. **FHIR Mapper** → Standard format conversion
6. **Explanation Generator** → Human-readable summaries
7. **Safety Checker** → Risk analysis and alerts

---

## 🗄️ Future Database Schema (Planned)

```sql
-- Users table
CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Documents table
CREATE TABLE documents (
    id VARCHAR(50) PRIMARY KEY,
    patient_id VARCHAR(50),
    uploaded_by VARCHAR(50),
    document_type VARCHAR(50),
    file_path VARCHAR(255),
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id),
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

-- FHIR data table
CREATE TABLE fhir_bundles (
    id VARCHAR(50) PRIMARY KEY,
    document_id VARCHAR(50),
    bundle_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
```

---

## 🧪 Testing

### Manual Testing

1. Test login with different user roles
2. Verify role-based access restrictions
3. Check dashboard functionality for each role
4. Test logout and session management

### Automated Testing (Coming Soon)

```bash
pytest tests/
```

---

## 📝 Development Roadmap

### Phase 1: Authentication ✅ (Current)
- [x] User login system
- [x] Role-based access control
- [x] Example users
- [x] Dashboard templates

### Phase 2: Database Integration 🔄 (Next)
- [ ] SQLite/PostgreSQL setup
- [ ] User CRUD operations
- [ ] Data persistence
- [ ] Migration scripts

### Phase 3: AI Pipeline Integration
- [ ] Document upload interface
- [ ] AI processing status tracking
- [ ] Results visualization
- [ ] FHIR data display

### Phase 4: Advanced Features
- [ ] Real-time notifications
- [ ] Audit logging
- [ ] Report generation
- [ ] Export functionality

---

## 🤝 Contributing

This is part of the ELEC5620 Medical AI & ML Engineering Project.

**Team**: HACKERJEE - Group 7  
**University**: University of Sydney  
**Year**: 2025

---

## 📞 Support

For issues or questions:
- Check the main project README
- Review Flask documentation
- Contact system administrator

---

## ⚖️ License

Part of the Clinical AI Assistance System  
See main project LICENSE file

---

**Note**: This is a development version. Ensure proper security measures before deploying to production.

