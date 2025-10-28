# 🏃‍♂️ Agile Project Management Guide
## Clinical AI Medical System - ELEC5620 Group 7 (HACKERJEE)

**Date**: October 28, 2025  
**Project Status**: 90% Complete  
**Team**: HACKERJEE - University of Sydney

---

## 📋 Table of Contents

1. [Introduction to Agile](#introduction-to-agile)
2. [Your Project in Agile Terms](#your-project-in-agile-terms)
3. [Sprint Planning](#sprint-planning)
4. [User Stories](#user-stories)
5. [Task Breakdown](#task-breakdown)
6. [Progress Tracking](#progress-tracking)
7. [Jira Preparation](#jira-preparation)
8. [Agile Ceremonies](#agile-ceremonies)
9. [Best Practices](#best-practices)

---

## 1️⃣ Introduction to Agile

### What is Agile?

Agile is an **iterative approach** to software development that emphasizes:
- **Iterative Development**: Build software in small, manageable increments
- **Collaboration**: Close teamwork between developers, users, and stakeholders
- **Responding to Change**: Flexibility to adapt requirements as you learn
- **Working Software**: Focus on delivering functional software over documentation
- **Continuous Improvement**: Regular reflection and adjustment

### Key Agile Principles (Applied to Your Project)

1. **Deliver working software frequently** 
   - ✅ You've already done this! UC-01 → UC-02 → UC-03 → UC-04
   
2. **Welcome changing requirements**
   - Your system supports multiple use cases that evolved over time
   
3. **Working software is the primary measure of progress**
   - 90% completion = 4 working features + backend logic
   
4. **Build projects around motivated individuals**
   - Each team member owns a use case (Chadwick, Saahir, Sarvadnya, Venkatesh, Thanh)

5. **Face-to-face conversation** 
   - Daily standups, pair programming sessions

6. **Simplicity—the art of maximizing work not done**
   - Modular AI pipeline allows independent development

---

## 2️⃣ Your Project in Agile Terms

### Product Vision

**"An AI-powered clinical assistance system that transforms unstructured medical documents into actionable, FHIR-compliant insights while providing insurance matching and financial assistance."**

### Product Backlog (Current State)

Your project has been organized into **5 Epic Use Cases**:

| Epic ID | Epic Name | Owner | Status | Story Points |
|---------|-----------|-------|--------|--------------|
| **UC-01** | Insurance Quote Generation | Chadwick Ng | ✅ DONE | 21 |
| **UC-02** | Clinical Record Analysis | Saahir Khan | ✅ DONE | 34 |
| **UC-03** | Patient History & Trends | Sarvadnya Kamble | ✅ DONE | 21 |
| **UC-04** | Review AI Output & Approve | Thanh Le | 🔶 IN PROGRESS | 13 (8 done) |
| **UC-05** | Financial Assistance Matching | Venkatesh Badri | 🔜 TO DO | 21 |

**Total Story Points**: 110  
**Completed**: 84 (76%)  
**Remaining**: 26 (24%)

---

## 3️⃣ Sprint Planning

### Sprint Structure

For Jira preparation, organize your work into **2-week sprints**:

---

### **SPRINT 0: Foundation** (COMPLETED ✅)
**Duration**: Week 1-2  
**Goal**: Set up infrastructure and authentication

#### Completed User Stories:
- ✅ User authentication system (login/logout)
- ✅ Role-based access control (Patient, Doctor, Admin)
- ✅ Flask web application setup
- ✅ Bootstrap UI templates
- ✅ Database schema design

**Retrospective Learnings**:
- Flask-Login integration was smoother than expected
- Bootstrap 5 provided good responsive design out of the box
- In-memory storage good for prototyping, but database needed soon

---

### **SPRINT 1: Insurance Quote Feature** (COMPLETED ✅)
**Duration**: Week 3-4  
**Goal**: Implement UC-01 - Insurance Quote Generation

#### Completed User Stories:
- ✅ As a **patient**, I want to enter my health data so that I can get insurance quotes
- ✅ As a **patient**, I want to upload medical documents to automatically populate health data
- ✅ As a **patient**, I want to see ranked insurance quotes based on my health and income
- ✅ As a **patient**, I want to compare insurance plans side-by-side
- ✅ As a **patient**, I want to simulate costs for different scenarios
- ✅ As a **patient**, I want to share quotes with my doctor for review
- ✅ As a **doctor**, I want to review patient insurance quotes and provide recommendations

**Demo Deliverables**:
- Working insurance quote form
- AI risk assessment engine
- Quote comparison page
- Cost breakdown with simulations
- Doctor review workflow

**Retrospective Learnings**:
- AI risk assessment needs clear business rules
- Cost simulation feature very popular with test users
- Doctor review adds credibility to AI recommendations

---

### **SPRINT 2: Clinical Analysis Pipeline** (COMPLETED ✅)
**Duration**: Week 5-6  
**Goal**: Implement UC-02 - AI Medical Document Analysis

#### Completed User Stories:
- ✅ As a **doctor**, I want to upload medical documents for AI processing
- ✅ As a **patient**, I want to upload my medical records for analysis
- ✅ As a **user**, I want OCR text extraction from PDFs and images
- ✅ As a **user**, I want medical entities extracted (conditions, medications, observations)
- ✅ As a **user**, I want entities mapped to standard codes (SNOMED, RxNorm, LOINC)
- ✅ As a **user**, I want FHIR R4 bundles generated for interoperability
- ✅ As a **patient**, I want plain-language explanations of my medical data
- ✅ As a **doctor**, I want safety flags and red alerts for patient risks

**Demo Deliverables**:
- 7-stage AI pipeline (OCR → Sectionizer → NER → Linker → FHIR → Explain → Safety)
- FHIR R4 bundle generation
- Patient-friendly explanations
- Safety checker with risk levels
- Analysis history tracking

**Retrospective Learnings**:
- SpaCy models work well but have macOS ARM64 compatibility issues
- FHIR mapping more complex than anticipated—need good test data
- Safety checker requires domain knowledge—consulted medical references
- Processing time acceptable for small documents, optimization needed for large files

---

### **SPRINT 3: Patient History & Timeline** (COMPLETED ✅)
**Duration**: Week 7-8  
**Goal**: Implement UC-03 - Patient History Documentation

#### Completed User Stories:
- ✅ As a **doctor**, I want to view a patient's complete medical history
- ✅ As a **doctor**, I want to see trends in patient conditions over time
- ✅ As a **doctor**, I want an interactive timeline of medical events
- ✅ As a **doctor**, I want data quality alerts for incomplete records
- ✅ As a **doctor**, I want to identify gaps in patient data
- ✅ As a **doctor**, I want to export patient history reports
- ✅ As a **patient**, I want to see my own medical history timeline

**Demo Deliverables**:
- Patient history dashboard with stats
- Interactive timeline with filters
- Data quality assessment
- Gap detection and recommendations
- Trend analysis for vitals and conditions
- JSON export functionality

**Retrospective Learnings**:
- Database integration critical for this feature—moved from in-memory to SQLite
- Timeline visualization needs client-side filtering for performance
- Empty state UX important when patient has no data
- Export feature useful for sharing with specialists

---

### **SPRINT 4: Doctor Review System (CURRENT)** 🔶
**Duration**: Week 9-10  
**Goal**: Implement UC-04 - Review AI Output & Approve

#### User Stories IN PROGRESS:

**Backend (COMPLETED ✅)**:
- ✅ As a **doctor**, I want to see pending AI outputs that need review
- ✅ As a **doctor**, I want to view AI-generated summaries and FHIR data
- ✅ As a **doctor**, I want to evaluate safety flags with severity levels
- ✅ As a **doctor**, I want to approve or reject AI outputs
- ✅ As a **doctor**, I want to add notes and modifications before approval
- ✅ As a **doctor**, I want the system to block unsafe approvals
- ✅ As a **doctor**, I want to digitally sign my approval decisions
- ✅ As an **admin**, I want an immutable audit trail of all approvals

**Frontend (TO DO 🔜)**:
- 🔜 As a **doctor**, I want a clean UI to view pending reviews
- 🔜 As a **doctor**, I want an intuitive review form with checklists
- 🔜 As a **doctor**, I want to see approval history with filters
- 🔜 As a **doctor**, I want to view decision details and audit trails

**Current Tasks**:
1. ✅ Backend models (`approval_models.py`) - DONE
2. ✅ Flask routes (5 routes) - DONE
3. ✅ Safety validation logic - DONE
4. 🔜 Template: `pending_ai_reviews.html` - TO DO
5. 🔜 Template: `review_ai_output.html` - TO DO
6. 🔜 Template: `review_history.html` - TO DO
7. 🔜 Template: `approval_decision_detail.html` - TO DO

**Remaining Work**: 4 templates (~3-4 hours)

**Blockers**: None  
**Risks**: None

---

### **SPRINT 5: Financial Assistance (PLANNED)** 🔜
**Duration**: Week 11-12  
**Goal**: Implement UC-05 - Financial Assistance & Loan Matching

#### Planned User Stories:

- 🔜 As a **patient**, I want to check eligibility for government subsidies
- 🔜 As a **patient**, I want to see my out-of-pocket costs after subsidies
- 🔜 As a **patient**, I want personalized insurance recommendations based on affordability
- 🔜 As a **patient**, I want cost breakdowns comparing subsidized vs. full-cost plans
- 🔜 As a **patient**, I want loan options if I can't afford premiums
- 🔜 As a **patient**, I want to request human advisor consultation
- 🔜 As a **doctor**, I want to review plan selections for medical appropriateness

**Estimated Story Points**: 21

**Dependencies**:
- UC-01 (Insurance Quote) must be complete ✅
- UC-02 (Clinical Analysis) for health data ✅
- External APIs for subsidy calculation (if available)

---

### **SPRINT 6: Polish & Testing** 🔜
**Duration**: Week 13-14  
**Goal**: Final testing, documentation, and deployment preparation

#### Planned User Stories:

- 🔜 As a **developer**, I want comprehensive test coverage (pytest)
- 🔜 As an **admin**, I want deployment documentation for production
- 🔜 As a **user**, I want a user guide and tutorials
- 🔜 As a **developer**, I want CI/CD pipeline setup
- 🔜 As a **developer**, I want performance optimization for large documents
- 🔜 As a **team**, I want final code review and refactoring

---

## 4️⃣ User Stories

### What is a User Story?

**Format**: As a `[role]`, I want `[feature]` so that `[benefit]`

### Example: UC-04 Review AI Output

#### Epic: Review AI Output & Approve
**Epic Description**: Doctors must review and validate AI-generated medical summaries before releasing them to patients, ensuring safety and accuracy.

---

#### Story 1: View Pending Reviews
**As a** doctor  
**I want to** see a queue of AI outputs awaiting my review  
**So that** I can prioritize which patients need attention first

**Acceptance Criteria**:
- [ ] Pending reviews displayed in a sortable table
- [ ] Each review shows patient name, document type, and processing date
- [ ] High-risk cases (critical safety flags) highlighted in red
- [ ] Click on review opens detailed review page
- [ ] Empty state message when no reviews pending

**Story Points**: 3  
**Priority**: High  
**Status**: Backend ✅ | Frontend 🔜

---

#### Story 2: Review AI Summary
**As a** doctor  
**I want to** view AI-generated medical summaries, FHIR data, and safety flags  
**So that** I can validate the accuracy before approving

**Acceptance Criteria**:
- [ ] Display patient summary in readable markdown
- [ ] Show extracted conditions, medications, observations
- [ ] Display FHIR bundle in expandable JSON viewer
- [ ] List safety flags with severity badges
- [ ] Show AI confidence scores for key extractions
- [ ] Provide checklist for systematic review

**Story Points**: 5  
**Priority**: High  
**Status**: Backend ✅ | Frontend 🔜

---

#### Story 3: Approve or Reject with Notes
**As a** doctor  
**I want to** approve or reject AI outputs with my clinical notes  
**So that** patients receive validated information

**Acceptance Criteria**:
- [ ] Approve button (green) with confirmation modal
- [ ] Reject button (red) with required reason field
- [ ] Optional modification textarea for corrections
- [ ] Digital signature confirmation
- [ ] System logs approval in audit trail
- [ ] Success message with next actions

**Story Points**: 5  
**Priority**: High  
**Status**: Backend ✅ | Frontend 🔜

---

#### Story 4: Override Safety Flags
**As a** doctor  
**I want to** override safety flags with clinical justification  
**So that** I can approve cases where AI is overly cautious

**Acceptance Criteria**:
- [ ] Critical flags require override before approval
- [ ] Override form requires justification text (min 20 chars)
- [ ] System validates that all critical flags are addressed
- [ ] Overrides logged separately in audit trail
- [ ] Warning message confirms override action

**Story Points**: 3  
**Priority**: Medium  
**Status**: Backend ✅ | Frontend 🔜

---

#### Story 5: View Approval History
**As a** doctor  
**I want to** see my past approval decisions  
**So that** I can track my workload and review past cases

**Acceptance Criteria**:
- [ ] Table of past approvals/rejections
- [ ] Filter by status (approved/rejected/escalated)
- [ ] Filter by date range
- [ ] Search by patient name or ID
- [ ] Click to view decision details
- [ ] Export to CSV for reporting

**Story Points**: 3  
**Priority**: Low  
**Status**: Backend ✅ | Frontend 🔜

---

### Complete User Story Mapping

```
EPIC: Clinical AI System
│
├── UC-01: Insurance Quote
│   ├── Enter health data
│   ├── Upload documents
│   ├── View ranked quotes
│   ├── Compare plans
│   ├── Simulate costs
│   └── Share with doctor
│
├── UC-02: Clinical Analysis
│   ├── Upload medical document
│   ├── Extract text (OCR)
│   ├── Extract entities (NER)
│   ├── Map to codes (SNOMED/RxNorm)
│   ├── Generate FHIR bundle
│   ├── Create explanations
│   └── Check safety flags
│
├── UC-03: Patient History
│   ├── View patient dashboard
│   ├── See medical timeline
│   ├── Detect data gaps
│   ├── Analyze trends
│   └── Export history report
│
├── UC-04: Review & Approve
│   ├── View pending reviews
│   ├── Review AI summaries
│   ├── Evaluate safety flags
│   ├── Approve/reject/escalate
│   └── View approval history
│
└── UC-05: Financial Assistance
    ├── Check subsidy eligibility
    ├── Calculate out-of-pocket costs
    ├── Compare subsidized plans
    ├── Find loan options
    └── Request advisor help
```

---

## 5️⃣ Task Breakdown

### How to Break Down Stories into Tasks

Each user story should be broken down into **technical tasks**:

#### Example: Story "View Pending Reviews"

**Frontend Tasks**:
1. Create `pending_ai_reviews.html` template (2 hrs)
   - Design table layout
   - Add sorting functionality
   - Implement status badges
   - Add "No reviews" empty state

2. Add CSS styling (0.5 hrs)
   - Card layout
   - Table responsive design
   - Badge colors

3. Add JavaScript interactivity (1 hr)
   - Sort table by column
   - Filter by status
   - Search functionality

**Backend Tasks**:
1. ✅ Create route `/review/pending` (DONE)
2. ✅ Query database for pending analyses (DONE)
3. ✅ Sort by priority (critical flags first) (DONE)
4. ✅ Pass data to template (DONE)

**Testing Tasks**:
1. Manual test with mock data (0.5 hrs)
2. Test with 0, 1, and 10+ pending reviews
3. Test sorting and filtering
4. Test on mobile devices

**Total Estimated Time**: 4 hours  
**Story Points**: 3

---

### Task Board (Kanban Style)

```
┌─────────────┬─────────────┬──────────────┬──────────┐
│   TO DO     │ IN PROGRESS │  IN REVIEW   │   DONE   │
├─────────────┼─────────────┼──────────────┼──────────┤
│ UC-05 All   │ UC-04       │              │ UC-01    │
│ Stories     │ Templates   │              │ Complete │
│             │             │              │          │
│             │ - pending_  │              │ UC-02    │
│             │   reviews   │              │ Complete │
│             │   .html     │              │          │
│             │             │              │ UC-03    │
│             │ - review_   │              │ Complete │
│             │   ai_output │              │          │
│             │   .html     │              │ UC-04    │
│             │             │              │ Backend  │
│             │ - review_   │              │          │
│             │   history   │              │          │
│             │   .html     │              │          │
│             │             │              │          │
│             │ - approval_ │              │          │
│             │   detail    │              │          │
│             │   .html     │              │          │
└─────────────┴─────────────┴──────────────┴──────────┘
```

---

## 6️⃣ Progress Tracking

### Velocity Tracking

**Velocity** = Story points completed per sprint

| Sprint | Planned | Completed | Velocity | Notes |
|--------|---------|-----------|----------|-------|
| Sprint 0 | 8 | 8 | 8 | Foundation setup |
| Sprint 1 | 21 | 21 | 21 | Insurance feature complete |
| Sprint 2 | 34 | 34 | 34 | AI pipeline complete |
| Sprint 3 | 21 | 21 | 21 | Patient history done |
| Sprint 4 | 13 | 8 | — | In progress (61% done) |
| **Average** | **19.4** | **18.4** | **21** | High velocity team! |

**Insight**: Your team has consistently high velocity. For Sprint 5, you can confidently plan for 21 story points.

---

### Burndown Chart (Sprint 4)

```
Story Points Remaining
13 │ ●
12 │ │
11 │ │
10 │ │
 9 │ │
 8 │ │  ●
 7 │ │  │
 6 │ │  │
 5 │ │  │  ○ ← Projected (5 remaining)
 4 │ │  │  │
 3 │ │  │  │
 2 │ │  │  │
 1 │ │  │  │
 0 │ └──┴──┴────────────►
   Day 1  5  10        14

● = Actual progress
○ = Projected finish
```

**Status**: On track to finish Sprint 4 on time with 4 template tasks remaining.

---

### Definition of Done (DoD)

Before marking a story as "DONE", ensure:

- [ ] **Code Complete**: All tasks implemented
- [ ] **UI Rendered**: Template displays correctly
- [ ] **Functionality Works**: Tested manually with real data
- [ ] **No Console Errors**: Browser and server logs clean
- [ ] **Responsive Design**: Works on mobile and desktop
- [ ] **Security Checked**: No SQL injection, XSS vulnerabilities
- [ ] **Documentation Updated**: Comments and README updated
- [ ] **Peer Reviewed**: Another team member reviewed the code
- [ ] **Integrated**: Merged into main branch without conflicts
- [ ] **Demo Ready**: Can be shown to stakeholders

---

## 7️⃣ Jira Preparation

### How to Set Up Your Project in Jira

When you move to Jira in Stage 2, here's how to structure it:

---

### **1. Create Project**

- **Project Name**: Clinical AI Medical System
- **Project Key**: CAMS
- **Project Type**: Scrum (or Kanban)
- **Project Lead**: Assign a team lead

---

### **2. Create Epics**

| Epic Key | Epic Name | Status | Story Points |
|----------|-----------|--------|--------------|
| CAMS-1 | Insurance Quote Generation | DONE | 21 |
| CAMS-2 | Clinical Record Analysis | DONE | 34 |
| CAMS-3 | Patient History & Trends | DONE | 21 |
| CAMS-4 | Review AI Output & Approve | IN PROGRESS | 13 |
| CAMS-5 | Financial Assistance Matching | TO DO | 21 |

---

### **3. Create User Stories**

Example for UC-04:

| Story Key | Story Title | Epic | Story Points | Status |
|-----------|-------------|------|--------------|--------|
| CAMS-41 | View Pending Reviews | CAMS-4 | 3 | IN PROGRESS |
| CAMS-42 | Review AI Summary | CAMS-4 | 5 | TO DO |
| CAMS-43 | Approve or Reject | CAMS-4 | 5 | TO DO |
| CAMS-44 | Override Safety Flags | CAMS-4 | 3 | TO DO |
| CAMS-45 | View Approval History | CAMS-4 | 3 | TO DO |

---

### **4. Create Tasks (Sub-tasks)**

Example for CAMS-41 (View Pending Reviews):

| Task Key | Task Title | Estimate | Status |
|----------|------------|----------|--------|
| CAMS-41-1 | Create Flask route | 1h | DONE |
| CAMS-41-2 | Create HTML template | 2h | TO DO |
| CAMS-41-3 | Add CSS styling | 0.5h | TO DO |
| CAMS-41-4 | Add JavaScript sorting | 1h | TO DO |
| CAMS-41-5 | Manual testing | 0.5h | TO DO |

---

### **5. Set Up Sprints**

- **Sprint Name**: Sprint 4 - Review System
- **Duration**: 2 weeks
- **Start Date**: Week 9, Day 1
- **End Date**: Week 10, Day 14
- **Sprint Goal**: Complete UC-04 Review & Approve frontend

**Stories in Sprint**:
- CAMS-41 (3 points)
- CAMS-42 (5 points)
- CAMS-43 (5 points)

**Total**: 13 points

---

### **6. Create Board**

**Kanban Board Columns**:
1. **Backlog** (not started)
2. **To Do** (in current sprint)
3. **In Progress** (actively working)
4. **In Review** (code review/testing)
5. **Done** (meets DoD)

**Scrum Board** (alternative):
- Same columns, but tied to specific sprints

---

### **7. Custom Fields**

Add these custom fields for medical AI tracking:

- **Use Case ID** (UC-01, UC-02, etc.)
- **Owner** (Chadwick, Saahir, Sarvadnya, Venkatesh, Thanh)
- **Component** (Frontend, Backend, AI Pipeline, Database)
- **Risk Level** (Low, Medium, High)
- **Has Dependencies** (Yes/No)
- **Demo Ready** (Yes/No)

---

### **8. Workflow**

```
TO DO → IN PROGRESS → CODE REVIEW → TESTING → DONE
         ↓             ↓              ↓
      BLOCKED ← ─ ─ ─ ─ ┘            CLOSED
```

**Transitions**:
- **Start Progress**: Move from TO DO → IN PROGRESS
- **Submit for Review**: Move to CODE REVIEW
- **Approve**: Move to TESTING
- **Complete**: Move to DONE
- **Block**: Move to BLOCKED (with blocker reason)
- **Reopen**: Move from DONE back to IN PROGRESS

---

## 8️⃣ Agile Ceremonies

### Daily Standup (15 minutes)

**Format**:
Each team member answers 3 questions:

1. **What did I complete yesterday?**
   - Example: "Finished the backend route for pending reviews"

2. **What will I work on today?**
   - Example: "Create the HTML template for pending reviews page"

3. **What blockers do I have?**
   - Example: "Need design mockup for approval form layout"

**Tips**:
- Keep it short (15 min max)
- Focus on progress, not details
- Raise blockers, don't solve them in standup
- Use a timer

---

### Sprint Planning (2-4 hours)

**Agenda**:

1. **Review Sprint Goal** (15 min)
   - What do we want to achieve this sprint?
   - Example: "Complete UC-04 frontend"

2. **Review Backlog** (30 min)
   - Product owner presents prioritized stories
   - Team asks clarifying questions

3. **Estimate Stories** (1 hour)
   - Use **Planning Poker** for story points
   - Discuss differences in estimates
   - Reach consensus

4. **Commit to Sprint** (30 min)
   - Based on velocity, select stories
   - Break down into tasks
   - Assign owners

5. **Define Success** (15 min)
   - What does "done" look like?
   - What will we demo?

---

### Sprint Review / Demo (1-2 hours)

**Agenda**:

1. **Demo Working Software** (45 min)
   - Show each completed story
   - Use real data, not mocks
   - Let stakeholders try it

2. **Gather Feedback** (30 min)
   - What worked well?
   - What needs improvement?
   - Any new requirements?

3. **Update Backlog** (15 min)
   - Add new stories from feedback
   - Re-prioritize if needed

**Example Demo Script for UC-04**:

> "Today I'll demo the AI Review & Approve system. As Dr. Smith, I log in and see 3 pending reviews. I click on patient John Doe's analysis. The system shows his FHIR data, AI summary, and 2 safety flags. I review the checklist, add a note, and approve. The system logs my decision and releases the data to the patient. Let me show you..."

---

### Sprint Retrospective (1-2 hours)

**Format**: Start, Stop, Continue

**Start** (What should we start doing?):
- Example: "Start doing code reviews before merging"
- Example: "Start writing tests alongside features"

**Stop** (What should we stop doing?):
- Example: "Stop working late nights—causes burnout"
- Example: "Stop skipping documentation"

**Continue** (What's working well?):
- Example: "Continue pair programming for complex features"
- Example: "Continue using modular architecture"

**Action Items**:
- Assign owner to each action
- Track in next sprint
- Review progress in next retrospective

---

### Example Retrospective for Your Team

**Sprint 3 Retrospective** (Patient History):

**What Went Well** 🎉:
- Database integration smoother than expected
- Timeline visualization looks great
- Empty state UX very user-friendly

**What Could Improve** 🔧:
- Large queries slow down dashboard—need caching
- Some CSS conflicts between Bootstrap and custom styles
- Didn't write any automated tests

**Action Items**:
1. **Thanh**: Research Flask-Caching for patient history (1 day)
2. **Sarvadnya**: Refactor CSS to use more utility classes (2 hours)
3. **Team**: Set up pytest and write first test suite (next sprint)

---

## 9️⃣ Best Practices

### 1. Keep Sprints Short (2 weeks)

**Why?**
- Faster feedback loops
- Easier to adjust priorities
- Reduces risk of building wrong features

**Your Context**:
- 2-week sprints align with university schedule
- Allows demo every 2 weeks to professor/TA
- Matches assignment milestones

---

### 2. Write Good User Stories

**Bad User Story** ❌:
> "Build review page"

**Good User Story** ✅:
> "As a doctor, I want to view pending AI outputs in a sortable table so that I can prioritize high-risk cases first."

**Tips**:
- Always include role, feature, benefit
- Make acceptance criteria specific and testable
- Keep stories small (3-8 story points)
- Avoid technical jargon in story title

---

### 3. Estimate with Story Points, Not Hours

**Why?**
- Accounts for complexity, not just time
- Team-relative (what's hard for one person may be easy for another)
- Reduces pressure to finish by exact time

**Fibonacci Scale**:
- **1 point**: Trivial (add a button, fix typo)
- **2 points**: Simple (small template, basic route)
- **3 points**: Moderate (template with logic)
- **5 points**: Complex (multi-step workflow)
- **8 points**: Very complex (full feature)
- **13 points**: Epic-level (too big, break down)

**Your Project Examples**:
- Create login form: 2 points ✅
- Build FHIR mapper: 13 points ✅
- Add safety checker: 8 points ✅
- Create review template: 3 points 🔜

---

### 4. Maintain a Healthy Backlog

**Backlog Grooming** (30-60 min weekly):
- Review new stories
- Update priorities
- Break down large stories
- Remove obsolete stories
- Estimate upcoming stories

**Backlog Health**:
- **Top 20%**: Ready for next sprint (well-defined, estimated)
- **Middle 60%**: High-level ideas (need refinement)
- **Bottom 20%**: Future ideas (rough concepts)

**Your Current Backlog**:
```
HIGH PRIORITY (Next Sprint):
  - UC-04: 4 templates (well-defined)
  - UC-05: Subsidy calculation backend

MEDIUM PRIORITY:
  - UC-05: Loan matching UI
  - Testing & automation
  - Performance optimization

LOW PRIORITY (Future):
  - Email notifications
  - Mobile app
  - EHR integration
```

---

### 5. Limit Work in Progress (WIP)

**Kanban Principle**: Finish what you start before starting new work

**WIP Limits**:
- **In Progress**: Max 2 stories per person
- **In Review**: Max 3 stories total
- **Testing**: Max 2 stories total

**Your Context**:
- If you have 5 team members, max 10 stories in progress
- Better to have 2 stories DONE than 5 stories 50% done

---

### 6. Embrace Change

**Scenario**: Professor asks for new feature mid-sprint

**Agile Response**:
1. Add story to backlog
2. Discuss priority in next planning
3. If urgent, swap out lower-priority story
4. Update sprint goal if needed

**Not Agile** ❌:
- Immediately start coding without planning
- Let scope creep derail sprint
- Say "no" without discussion

**Your Example**:
- If professor wants "export to PDF" feature
- Add story: "As a patient, I want to download my analysis as PDF"
- Estimate: 5 points
- Discuss: Can it wait till next sprint, or swap out UC-05 work?

---

### 7. Make Progress Visible

**Daily Updates**:
- Update Jira board before standup
- Move cards across columns as you work
- Add comments on blockers

**Visual Boards**:
- Physical board in team room (sticky notes)
- Digital board in Jira (accessible remotely)

**Metrics to Track**:
- Sprint burndown
- Velocity trend
- Story completion rate
- Blocker frequency

**Your Implementation**:
- Use GitHub Projects or Jira
- Screenshot board at end of each day
- Include in weekly status report to professor

---

### 8. Deliver Working Software

**Not Done Until**:
- Code written ✅
- Tests passing ✅
- Deployed to staging ✅
- Documented ✅
- Peer reviewed ✅
- Demo-ready ✅

**Your Context**:
- Each sprint should have a working demo
- Deploy to `web_app` and test with real users
- Show professor working features, not code

---

### 9. Reflect and Improve

**After Every Sprint**:
- Hold retrospective (don't skip!)
- Try one improvement per sprint
- Track results
- Celebrate wins

**Example Improvements to Try**:
- Sprint 5: Add pre-commit hooks for code quality
- Sprint 6: Start writing unit tests
- Sprint 7: Set up CI/CD pipeline

---

### 10. Collaborate Continuously

**Pair Programming**:
- Complex features: 2 developers, 1 computer
- Reduces bugs, spreads knowledge
- Try for UC-05 backend logic

**Code Reviews**:
- Every PR reviewed by another team member
- Use GitHub PR comments
- Focus on learning, not criticism

**Team Communication**:
- Slack/Discord for quick questions
- GitHub Issues for bugs
- Jira for stories/tasks
- Face-to-face for complex discussions

---

## 📊 Summary Dashboard

### Your Project at a Glance

```
┌─────────────────────────────────────────────────────────┐
│  CLINICAL AI MEDICAL SYSTEM - AGILE METRICS             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Total Epics:           5                               │
│  Completed Epics:       3 ✅                            │
│  In Progress Epics:     1 🔶                            │
│  Planned Epics:         1 🔜                            │
│                                                          │
│  Total Story Points:    110                             │
│  Completed:             84 (76%)                        │
│  In Progress:           13 (12%)                        │
│  Remaining:             13 (12%)                        │
│                                                          │
│  Average Velocity:      21 points/sprint                │
│  Sprints Completed:     3                               │
│  Sprints Remaining:     2                               │
│                                                          │
│  Team Size:             5                               │
│  Project Duration:      14 weeks                        │
│  Current Week:          9                               │
│                                                          │
│  Health Status:         🟢 HEALTHY                      │
│  On Schedule:           ✅ YES                          │
│  Technical Debt:        🟡 LOW                          │
│  Team Morale:           🟢 HIGH                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Action Items for Your Team

### Immediate (This Week):

1. **Create Jira Account** (if Stage 2 requires it)
   - Sign up at atlassian.com
   - Create team project
   - Invite all team members

2. **Import Epics and Stories**
   - Use this document as reference
   - Create 5 epics in Jira
   - Create user stories for UC-04 and UC-05

3. **Set Up Sprint 4**
   - Name: "Review System UI"
   - Duration: 2 weeks
   - Goal: Complete UC-04 templates
   - Stories: CAMS-41 through CAMS-45

4. **Assign Tasks**
   - Break down each story into tasks
   - Assign owners
   - Estimate time

5. **Hold Daily Standup**
   - Every morning, 15 minutes
   - Use this format (see section 8)

---

### Short-term (Next 2 Weeks):

1. **Complete Sprint 4**
   - Finish 4 templates for UC-04
   - Test end-to-end approval workflow
   - Demo to professor/TA

2. **Plan Sprint 5**
   - Estimate UC-05 stories
   - Decide what to include
   - Commit to sprint goal

3. **Start Documentation**
   - User guide for each feature
   - API documentation
   - Deployment guide

4. **Set Up CI/CD**
   - GitHub Actions for testing
   - Automatic deployment to staging
   - Linting and code quality checks

---

### Long-term (Stage 2 and Beyond):

1. **Integrate Jira with GitHub**
   - Link commits to stories (e.g., "CAMS-41: Add pending reviews template")
   - Auto-update story status on PR merge

2. **Add Metrics Dashboard**
   - Burndown charts
   - Velocity trends
   - Cycle time
   - Lead time

3. **Implement Continuous Improvement**
   - Track action items from retrospectives
   - Review and adjust processes
   - Experiment with new practices

4. **Prepare for Deployment**
   - Move from SQLite to PostgreSQL
   - Set up production environment
   - Security hardening
   - Performance testing

---

## 📚 Resources

### Agile Learning

- **Agile Manifesto**: https://agilemanifesto.org
- **Scrum Guide**: https://scrumguides.org
- **Atlassian Agile Guide**: https://www.atlassian.com/agile

### Jira Tutorials

- **Jira Basics**: https://www.atlassian.com/software/jira/guides
- **Scrum with Jira**: https://www.atlassian.com/agile/tutorials/how-to-do-scrum-with-jira-software
- **Story Mapping**: https://www.atlassian.com/agile/project-management/user-story-mapping

### Your Project Docs

- **README.md**: Project overview
- **FEATURES_SUMMARY.md**: Feature status
- **USE_CASE_*_IMPLEMENTATION_STATUS.md**: Detailed UC docs
- **IMPLEMENTATION_SUMMARY_SESSION.md**: Latest progress

---

## 🎓 Key Takeaways

### Agile Principles Applied to Your Project

✅ **Iterative Development**
- You built features incrementally (UC-01 → UC-02 → UC-03 → UC-04)
- Each sprint delivered working software
- Early feedback shaped later features

✅ **Collaboration**
- Each team member owns a use case
- Shared code base with modular architecture
- Integration points well-defined

✅ **Responding to Change**
- Database moved from in-memory to SQLite when needed
- Safety features added based on medical domain learning
- UI improved based on testing feedback

✅ **Working Software Over Documentation**
- 90% complete with working demos
- Documentation supports code, not vice versa
- Focus on user value

✅ **Continuous Improvement**
- Each sprint builds on previous learnings
- Retrospectives would have caught issues early
- Technical debt kept low

---

## 🚀 Next Steps Checklist

### Before Stage 2:

- [ ] Read this entire Agile guide
- [ ] Discuss with team which Agile practices to adopt
- [ ] Set up Jira project (if required)
- [ ] Create first sprint in Jira
- [ ] Hold sprint planning meeting
- [ ] Start daily standups
- [ ] Complete UC-04 templates (Sprint 4)
- [ ] Hold sprint review and demo
- [ ] Hold first retrospective
- [ ] Plan Sprint 5 (UC-05)

### Success Criteria:

You'll know you've mastered Agile when:
- ✅ Team holds regular standups without prompting
- ✅ Sprint planning feels natural, not forced
- ✅ Stories are estimated consistently
- ✅ Retrospectives lead to real improvements
- ✅ Jira board reflects actual work state
- ✅ Velocity is predictable
- ✅ Stakeholders see working software every 2 weeks

---

## 🎉 Congratulations!

You're already practicing Agile principles—now you're just formalizing them!

**Your project demonstrates**:
- ✅ Iterative delivery (4 features shipped)
- ✅ High velocity (21 points/sprint avg)
- ✅ Working software (90% complete, all demos working)
- ✅ Modular architecture (easy to change)
- ✅ Clear ownership (1 UC per person)

**Keep it up!** 🚀

---

**Document Version**: 1.0  
**Last Updated**: October 28, 2025  
**Authors**: HACKERJEE Team - ELEC5620 Group 7  
**University**: University of Sydney

---


