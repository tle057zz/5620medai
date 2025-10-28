# 📋 JIRA Setup Guide - Step by Step
## Clinical AI Medical System - ELEC5620 Group 7

**Purpose**: Complete guide to set up your project in Jira for Stage 2  
**Time Required**: 2-3 hours  
**Team**: HACKERJEE - University of Sydney

---

## 📑 Table of Contents

1. [Create Jira Account & Project](#step-1-create-jira-account--project)
2. [Set Up Project Board](#step-2-set-up-project-board)
3. [Create Epics](#step-3-create-epics)
4. [Create User Stories](#step-4-create-user-stories)
5. [Break Down into Tasks](#step-5-break-down-into-tasks)
6. [Set Up Sprints](#step-6-set-up-sprints)
7. [Configure Board](#step-7-configure-board)
8. [Add Team Members](#step-8-add-team-members)
9. [Daily Workflow](#step-9-daily-workflow)
10. [Best Practices](#step-10-best-practices)

---

## Step 1: Create Jira Account & Project

### 1.1 Sign Up for Jira

**Go to**: https://www.atlassian.com/software/jira/free

1. Click **"Get it free"**
2. Enter your email address (use university email if required)
3. Click **"Sign up"**
4. Check your email and verify your account
5. Choose **"Jira Software"** (not Jira Service Management or Work Management)

**Account Setup**:
- **Your site name**: `hackerjee-elec5620` (becomes hackerjee-elec5620.atlassian.net)
- **Team name**: HACKERJEE
- **What will you use Jira for?**: Software development

---

### 1.2 Create New Project

1. Click **"Create project"** (top right)
2. Select **"Scrum"** template
   - Alternatively, choose **"Kanban"** if you prefer continuous flow over sprints
3. Select **"Team-managed project"** (easier for small teams)
4. Enter project details:

```
Project name: Clinical AI Medical System
Project key: CAMS (auto-generated, you can change it)
```

5. Click **"Create"**

---

### 1.3 Initial Project Configuration

After creation, Jira shows a quick setup wizard:

1. **Skip** the tutorial for now (you can revisit later)
2. You'll see an empty board
3. Navigate to **Project settings** (gear icon, bottom left)

---

## Step 2: Set Up Project Board

### 2.1 Configure Board Columns

**Path**: Project settings → Board → Columns

Default columns are:
- To Do
- In Progress  
- Done

**Recommended for your project**:

1. Click **"Add column"** to add new columns
2. Set up these columns in order:

```
1. BACKLOG (gray)
2. TO DO (blue)
3. IN PROGRESS (yellow)
4. IN REVIEW (purple)
5. TESTING (orange)
6. DONE (green)
```

3. For each column, set the **status mapping**:

| Column | Status |
|--------|--------|
| BACKLOG | To Do |
| TO DO | To Do |
| IN PROGRESS | In Progress |
| IN REVIEW | In Progress |
| TESTING | In Progress |
| DONE | Done |

4. Click **"Save"**

---

### 2.2 Set WIP Limits (Optional)

**Path**: Board → Board settings → Columns

For each column, set Work In Progress limits:

- **IN PROGRESS**: Max 10 (2 per team member × 5 members)
- **IN REVIEW**: Max 5
- **TESTING**: Max 3

This prevents too much work piling up in one stage.

---

## Step 3: Create Epics

### 3.1 What Are Epics?

Epics are large bodies of work (your 5 use cases). Each epic contains multiple user stories.

---

### 3.2 Create Epic #1: Insurance Quote

1. Click **"Create"** button (top nav)
2. Select **Issue Type**: Epic
3. Fill in:

```
Epic name: Insurance Quote Generation
Summary: UC-01: Request Insurance Quote
Description:
AI-powered insurance quote generation based on patient health data, 
medical history, and income. Provides ranked quotes with cost simulations 
and doctor review workflow.

Reporter: [Your name]
Assignee: Chadwick Ng
Priority: High
Labels: use-case, patient-feature, completed
Epic color: Purple
Story point estimate: 21
```

4. Click **"Create"**

---

### 3.3 Create Epic #2: Clinical Analysis

1. Click **"Create"** button
2. Select **Issue Type**: Epic
3. Fill in:

```
Epic name: Clinical Record Analysis
Summary: UC-02: Analyze Patient Medical Record
Description:
Complete AI medical pipeline with 7 stages: OCR, Sectionizer, NER, 
Entity Linking, FHIR Mapping, Explanation Generation, and Safety Checking. 
Outputs FHIR R4 bundles and patient-friendly explanations.

Reporter: [Your name]
Assignee: Saahir Khan
Priority: High
Labels: use-case, ai-pipeline, completed
Epic color: Blue
Story point estimate: 34
```

4. Click **"Create"**

---

### 3.4 Create Epic #3: Patient History

```
Epic name: Patient History Documentation
Summary: UC-03: Patient History & Timeline
Description:
Longitudinal patient data aggregation with trend analysis, interactive 
timeline visualization, data quality assessment, and gap detection.

Reporter: [Your name]
Assignee: Sarvadnya Kamble
Priority: High
Labels: use-case, doctor-feature, completed
Epic color: Green
Story point estimate: 21
```

---

### 3.5 Create Epic #4: Review & Approve

```
Epic name: Review AI Output & Approve
Summary: UC-04: Doctor Reviews AI Analysis
Description:
Doctor workflow to review, validate, and approve AI-generated medical 
summaries with safety flag evaluation, digital signatures, and 
immutable audit trail.

Reporter: [Your name]
Assignee: Thanh Le
Priority: High
Labels: use-case, doctor-feature, in-progress
Epic color: Red
Story point estimate: 13
```

---

### 3.6 Create Epic #5: Financial Assistance

```
Epic name: Financial Assistance & Loan Matching
Summary: UC-05: Financial Assistance Request
Description:
Subsidy eligibility checking, out-of-pocket cost calculation, 
personalized insurance recommendations, and loan matching for patients.

Reporter: [Your name]
Assignee: Venkatesh Badri Narayanan
Priority: Medium
Labels: use-case, patient-feature, planned
Epic color: Orange
Story point estimate: 21
```

---

### 3.7 Verify Epics

1. Go to **Roadmap** view (left sidebar)
2. You should see all 5 epics
3. Drag to order by priority (UC-04, UC-05 at top)

---

## Step 4: Create User Stories

### 4.1 User Story Template

**Format**:
```
Summary: As a [role], I want [feature] so that [benefit]
Issue Type: Story
Epic Link: [Select parent epic]
Description: [Detailed requirements]
Acceptance Criteria: [Bullet list]
Story Points: [Fibonacci: 1, 2, 3, 5, 8, 13]
Priority: [High/Medium/Low]
Labels: [frontend, backend, etc.]
```

---

### 4.2 Create Stories for UC-04 (Example)

#### Story 1: View Pending Reviews

1. Click **"Create"**
2. Select **Issue Type**: Story
3. Fill in:

```
Summary: As a doctor, I want to view pending AI reviews so I can prioritize urgent cases
Issue Type: Story
Epic Link: Review AI Output & Approve
Priority: High

Description:
Display a queue of AI-generated analyses awaiting doctor review. 
Show patient name, document type, processing date, and risk level. 
Highlight critical safety flag cases in red.

Acceptance Criteria:
- [ ] Pending reviews displayed in sortable table
- [ ] Columns: Patient Name, Document Type, Date, Risk Level, Action
- [ ] High-risk cases highlighted in red
- [ ] Click row opens detailed review page
- [ ] Empty state message when no reviews pending
- [ ] Table responsive on mobile devices

Story Points: 3
Labels: frontend, doctor-feature, uc-04
Assignee: Thanh Le
Sprint: Sprint 4
```

4. Click **"Create"**

---

#### Story 2: Review AI Summary

```
Summary: As a doctor, I want to review AI summaries and FHIR data so I can validate accuracy

Issue Type: Story
Epic Link: Review AI Output & Approve
Priority: High

Description:
Display complete AI analysis including patient summary, extracted entities, 
FHIR bundle, and safety flags. Provide systematic review checklist.

Acceptance Criteria:
- [ ] Display patient summary in readable markdown format
- [ ] Show conditions, medications, observations in organized sections
- [ ] FHIR bundle viewable in expandable JSON viewer
- [ ] Safety flags listed with severity badges
- [ ] AI confidence scores shown for key extractions
- [ ] Checklist for systematic review (8 items)
- [ ] Print-friendly layout

Story Points: 5
Labels: frontend, backend, doctor-feature, uc-04
Assignee: Thanh Le
Sprint: Sprint 4
```

---

#### Story 3: Approve or Reject Output

```
Summary: As a doctor, I want to approve or reject AI outputs with notes

Issue Type: Story
Epic Link: Review AI Output & Approve
Priority: High

Description:
Allow doctor to make approval decision with clinical notes, modifications, 
and digital signature.

Acceptance Criteria:
- [ ] Green "Approve" button with confirmation modal
- [ ] Red "Reject" button with required reason field
- [ ] Optional modification textarea for corrections
- [ ] Digital signature confirmation checkbox
- [ ] System validates all critical flags addressed
- [ ] Audit log entry created on submission
- [ ] Success message with next actions
- [ ] Redirect to pending reviews after save

Story Points: 5
Labels: frontend, backend, doctor-feature, uc-04
Assignee: Thanh Le
Sprint: Sprint 4
```

---

#### Story 4: Override Safety Flags

```
Summary: As a doctor, I want to override safety flags with justification

Issue Type: Story
Epic Link: Review AI Output & Approve
Priority: Medium

Description:
Enable doctors to override AI safety flags when clinically appropriate, 
with required justification.

Acceptance Criteria:
- [ ] Critical flags prevent approval until addressed
- [ ] Override checkbox for each flag
- [ ] Justification textarea (min 20 characters)
- [ ] Warning message confirms override action
- [ ] Override logged separately in audit trail
- [ ] Senior review required for >3 overrides

Story Points: 3
Labels: frontend, backend, doctor-feature, uc-04
Assignee: Thanh Le
Sprint: Sprint 4
```

---

#### Story 5: View Approval History

```
Summary: As a doctor, I want to view my approval history

Issue Type: Story
Epic Link: Review AI Output & Approve
Priority: Low

Description:
Display past approval decisions with filters and search.

Acceptance Criteria:
- [ ] Table of past approvals/rejections
- [ ] Filter by status (approved/rejected/escalated)
- [ ] Filter by date range (dropdown)
- [ ] Search by patient name or ID
- [ ] Click row to view decision details
- [ ] Export to CSV button
- [ ] Pagination for >20 results

Story Points: 3
Labels: frontend, doctor-feature, uc-04
Assignee: Thanh Le
Sprint: Sprint 4
```

---

### 4.3 Bulk Create Stories (Faster Method)

For remaining use cases, you can import from CSV:

1. Go to **Project settings** → **Import**
2. Download template CSV
3. Fill in spreadsheet:

| Issue Type | Summary | Epic Link | Story Points | Priority | Assignee | Status |
|------------|---------|-----------|--------------|----------|----------|--------|
| Story | As a patient, I want to check subsidy eligibility | Financial Assistance | 5 | High | Venkatesh | To Do |
| Story | As a patient, I want to see out-of-pocket costs | Financial Assistance | 3 | High | Venkatesh | To Do |

4. Upload CSV
5. Review and confirm import

---

## Step 5: Break Down into Tasks

### 5.1 Add Sub-tasks to Stories

1. Open a story (e.g., "View Pending Reviews")
2. Click **"Add a child issue"** → **"Sub-task"**
3. Create sub-tasks:

---

#### Sub-task 1: Backend Route

```
Summary: Create Flask route /review/pending
Issue Type: Sub-task
Parent: [Story name]
Description:
Implement backend route to fetch pending analyses from database, 
sort by priority (critical flags first), and pass to template.

Estimate: 1h
Status: Done
Assignee: Thanh Le
```

---

#### Sub-task 2: HTML Template

```
Summary: Create pending_ai_reviews.html template
Issue Type: Sub-task
Parent: [Story name]
Description:
Design table layout with Bootstrap 5, add status badges, 
implement empty state, and ensure mobile responsiveness.

Estimate: 2h
Status: In Progress
Assignee: Thanh Le
```

---

#### Sub-task 3: CSS Styling

```
Summary: Add custom CSS for review queue
Issue Type: Sub-task
Description:
Style table with hover effects, color-code risk levels, 
add badge styles for status indicators.

Estimate: 30min
Status: To Do
```

---

#### Sub-task 4: JavaScript Interactivity

```
Summary: Add table sorting and filtering
Issue Type: Sub-task
Description:
Implement client-side sorting by column, filter by status, 
search functionality.

Estimate: 1h
Status: To Do
```

---

#### Sub-task 5: Testing

```
Summary: Manual testing of pending reviews page
Issue Type: Sub-task
Description:
Test with 0, 1, 5, 20 pending reviews. Test sorting, filtering, 
mobile layout, empty state. Test on Chrome, Safari, Firefox.

Estimate: 30min
Status: To Do
```

---

### 5.2 Repeat for All Stories

Create sub-tasks for each of the 5 UC-04 stories following the same pattern.

**Total sub-tasks for UC-04**: ~25 tasks

---

## Step 6: Set Up Sprints

### 6.1 Create Sprint 4

1. Go to **Backlog** view (left sidebar)
2. Click **"Create sprint"** (top right)
3. Name it: **"Sprint 4 - Review System UI"**
4. Set dates:
   - **Start date**: Monday of Week 9
   - **End date**: Friday of Week 10 (2 weeks)
5. Click **"Create"**

---

### 6.2 Add Stories to Sprint

1. In Backlog view, you'll see two sections:
   - Sprint 4 (empty)
   - Backlog (all your stories)

2. **Drag stories** from Backlog into Sprint 4:
   - ✅ View Pending Reviews (3 points)
   - ✅ Review AI Summary (5 points)
   - ✅ Approve or Reject (5 points)
   - ✅ Override Safety Flags (3 points)
   - ✅ View Approval History (3 points)

3. **Total**: 19 story points (slightly over your velocity of 21, but manageable)

---

### 6.3 Set Sprint Goal

1. Click sprint name to expand details
2. Add **Sprint Goal**:

```
Complete UC-04 frontend templates and enable doctors to review and 
approve AI-generated medical analyses with full audit trail.
```

3. Click **"Save"**

---

### 6.4 Start Sprint

1. Click **"Start sprint"** button
2. Confirm sprint duration (2 weeks)
3. Sprint is now active!
4. Stories move to **Active sprint** view

---

## Step 7: Configure Board

### 7.1 Add Quick Filters

**Path**: Board view → Click "..." (top right) → Board settings → Quick filters

Add these filters for easy navigation:

**Filter 1: My Items**
```
Name: My Items
JQL: assignee = currentUser()
```

**Filter 2: High Priority**
```
Name: High Priority
JQL: priority = High
```

**Filter 3: UC-04 Only**
```
Name: UC-04
JQL: labels = uc-04
```

**Filter 4: Blocked**
```
Name: Blocked
JQL: status = Blocked
```

Click **"Save"** after each

---

### 7.2 Customize Card Layout

**Path**: Board settings → Card layout

Choose what fields to show on cards:

**Card Front**:
- ☑ Summary
- ☑ Assignee (avatar)
- ☑ Story Points
- ☑ Epic Link (colored bar)
- ☑ Labels

**Card Back** (when you flip):
- ☑ Description
- ☑ Acceptance Criteria
- ☑ Comments

---

### 7.3 Set Up Swimlanes

**Path**: Board settings → Swimlanes

Change from default to:

**Group by**: Epic

This creates horizontal lanes for each epic (UC-01, UC-02, etc.)

Or alternatively:

**Group by**: Assignee

This creates lanes for each team member

---

## Step 8: Add Team Members

### 8.1 Invite Team

1. Go to **Project settings** → **People**
2. Click **"Add people"**
3. Enter email addresses:

```
chadwick.ng@[university].edu.au
saahir.khan@[university].edu.au
sarvadnya.kamble@[university].edu.au
venkatesh.badri@[university].edu.au
thanh.le@[university].edu.au
```

4. Select role: **Member** (not Admin for now)
5. Click **"Add"**

---

### 8.2 Assign Roles

Each team member gets assigned to their epic:

| Team Member | Epic | Stories |
|-------------|------|---------|
| Chadwick Ng | UC-01 | All insurance stories |
| Saahir Khan | UC-02 | All clinical analysis stories |
| Sarvadnya Kamble | UC-03 | All patient history stories |
| Venkatesh Badri | UC-05 | All financial assistance stories |
| Thanh Le | UC-04 | All review & approve stories |

**To bulk assign**:
1. Go to Backlog
2. Select multiple stories (Shift+Click)
3. Click **"Bulk change"** → **"Edit issues"**
4. Change **Assignee** field
5. Click **"Update"**

---

### 8.3 Set Permissions

**Path**: Project settings → Permissions

Recommended scheme for your team:

| Permission | Role | Who |
|------------|------|-----|
| Administer Projects | Admin | 1 person (project lead) |
| Edit Issues | Member | All team members |
| Create Issues | Member | All team members |
| Delete Issues | Admin | Project lead only |
| Transition Issues | Member | All team members |
| Assign Issues | Member | All team members |

Leave other permissions at default.

---

## Step 9: Daily Workflow

### 9.1 Morning Standup Routine

**Before standup** (each team member):

1. Open Jira board
2. Check **"My Items"** filter
3. Update status of your tasks:
   - Drag cards between columns
   - Add comments on progress
   - Flag blockers

---

**During standup** (15 minutes):

1. Open board on shared screen
2. Go person by person (alphabetical)
3. Each person answers:
   - **Yesterday**: Point to cards in DONE or IN REVIEW
   - **Today**: Point to cards in TO DO or IN PROGRESS
   - **Blockers**: Click on blocked items, explain

4. Scrum Master updates board live
5. Take notes in sprint comments

---

### 9.2 Work on Tasks

**When starting a task**:

1. Open the task/story
2. Click **"Start progress"** (or drag to IN PROGRESS column)
3. Add yourself as assignee (if not already)
4. Add comment: "Starting work on [feature]"

**While working**:

5. Update time spent (optional):
   - Click **"Log work"**
   - Enter time: "2h 30m"
   - Add note on what you did

6. Add comments for progress updates:
   - "Completed backend route ✅"
   - "Frontend 50% done, styling remaining"

**When stuck (blocker)**:

7. Click **"..." → Block issue**
8. Select blocking issue or describe blocker
9. Add comment explaining the problem
10. Notify team in Slack/Discord

**When done**:

11. Move to **IN REVIEW** column
12. Add comment: "Ready for review"
13. Tag reviewer: `@reviewer-name please review`

---

### 9.3 Code Review in Jira

**Reviewer**:

1. Open story/task
2. Click on linked GitHub PR (see Step 9.5 for setup)
3. Review code on GitHub
4. Return to Jira, add comment:
   - "✅ LGTM (Looks Good To Me)"
   - Or: "Requested changes in PR"

5. If approved, move to **TESTING**

---

### 9.4 Testing Tasks

**Tester** (can be assignee or another team member):

1. Pull latest code
2. Test all acceptance criteria
3. Record results in Jira comment:

```
Testing Results:
✅ Pending reviews display correctly
✅ Sorting works on all columns
✅ Mobile layout responsive
❌ Empty state message not showing (BUG)
✅ Risk level highlighting correct
```

4. If bugs found:
   - Create linked Bug issue
   - Move story back to IN PROGRESS
5. If all pass:
   - Move to DONE
   - Add comment: "All tests passed ✅"

---

### 9.5 Link GitHub Commits (Optional but Recommended)

**Setup** (one time):

1. Go to **Project settings** → **Integrations**
2. Click **"GitHub"** → **"Add repository"**
3. Authenticate with GitHub
4. Select your repository: `5620medai`
5. Click **"Connect"**

**Usage**:

In your commit messages, include Jira issue key:

```bash
git commit -m "CAMS-41: Add pending reviews template"
git commit -m "CAMS-42: Implement review form validation"
```

Jira will automatically:
- Link commits to issues
- Show commit count on cards
- Display code changes in issue view

---

### 9.6 End of Day

**Each team member**:

1. Review your board
2. Ensure all cards in correct columns
3. Add comments on unfinished work
4. Update estimates for remaining work
5. Flag any blockers for tomorrow

---

## Step 10: Best Practices

### 10.1 Keep Jira Updated

**✅ DO**:
- Update status within 1 hour of changing
- Add comments when making progress
- Log blockers immediately
- Close completed issues same day

**❌ DON'T**:
- Let issues sit in wrong column for days
- Update board only before standup
- Forget to link related issues
- Leave issues in "In Progress" forever

---

### 10.2 Write Good Comments

**Bad Comment** ❌:
> "Working on it"

**Good Comment** ✅:
> "Completed backend route. Tested with 5 pending reviews. Now working on frontend template. ETA: 2 hours."

**Template**:
```
Progress: [What you completed]
Current: [What you're working on now]
Next: [What's next]
Blockers: [Any issues]
ETA: [Time remaining]
```

---

### 10.3 Use Labels Effectively

Add these labels to organize work:

**By Layer**:
- `frontend` - HTML/CSS/JS work
- `backend` - Python/Flask work
- `database` - Schema/queries
- `ai-pipeline` - AI module work

**By Priority**:
- `critical` - Must be done this sprint
- `nice-to-have` - Can defer if needed

**By Type**:
- `bug` - Something broken
- `enhancement` - Improvement to existing feature
- `documentation` - Docs work
- `technical-debt` - Refactoring needed

**By Use Case**:
- `uc-01`, `uc-02`, `uc-03`, `uc-04`, `uc-05`

**By Feature**:
- `patient-feature` - Patient-facing
- `doctor-feature` - Doctor-facing
- `admin-feature` - Admin-facing

---

### 10.4 Sprint Ceremonies in Jira

#### Sprint Planning

**Before meeting**:
1. Product owner orders backlog by priority
2. Team reviews stories (read descriptions)

**During meeting**:
1. Open Backlog view
2. Product owner presents top stories
3. Team estimates using Planning Poker
4. Drag estimated stories into sprint
5. Stop when sprint capacity reached (21 points)
6. Set sprint goal
7. Start sprint

**After meeting**:
8. Each member opens their assigned stories
9. Creates sub-tasks
10. Estimates sub-tasks

---

#### Daily Standup

1. Open **Active sprint** board view
2. Filter by team member
3. Go person by person
4. Update cards live during meeting
5. Note action items in sprint description

---

#### Sprint Review

1. Open **Sprint report** (Reports → Sprint report)
2. Show completed stories (in DONE column)
3. Demo each story (live on localhost)
4. Gather feedback in comments
5. Create new stories for feedback

---

#### Sprint Retrospective

1. Create a new Epic: "Sprint 4 Retrospective"
2. Create 3 sub-tasks:
   - What went well
   - What needs improvement
   - Action items

3. During meeting, add comments to each
4. Convert action items to stories for next sprint

---

### 10.5 Reports to Review Weekly

**Burndown Chart**:
- **Path**: Reports → Burndown chart
- Shows if you're on track to finish sprint
- Red line above ideal = behind schedule
- Update daily for accuracy

**Velocity Chart**:
- **Path**: Reports → Velocity chart
- Shows story points per sprint
- Use to predict capacity
- Aim for consistency

**Cumulative Flow Diagram**:
- **Path**: Reports → Cumulative flow
- Shows work distribution across columns
- Large "In Progress" band = too much WIP
- Flat "Done" line = bottleneck

**Sprint Report**:
- **Path**: Reports → Sprint report
- Shows completed vs committed work
- Check after sprint ends
- Use in retrospective

---

## 📊 Your Complete Jira Structure

```
PROJECT: Clinical AI Medical System (CAMS)
│
├── EPIC: CAMS-1 Insurance Quote (21 pts) ✅ DONE
│   ├── Story: Enter health data (3 pts)
│   ├── Story: Upload documents (5 pts)
│   ├── Story: View ranked quotes (5 pts)
│   ├── Story: Compare plans (3 pts)
│   └── Story: Share with doctor (5 pts)
│
├── EPIC: CAMS-2 Clinical Analysis (34 pts) ✅ DONE
│   ├── Story: Upload document (3 pts)
│   ├── Story: OCR extraction (5 pts)
│   ├── Story: NER entities (8 pts)
│   ├── Story: Entity linking (8 pts)
│   ├── Story: FHIR generation (5 pts)
│   └── Story: Safety checking (5 pts)
│
├── EPIC: CAMS-3 Patient History (21 pts) ✅ DONE
│   ├── Story: View dashboard (5 pts)
│   ├── Story: Interactive timeline (8 pts)
│   ├── Story: Data quality alerts (3 pts)
│   └── Story: Export report (5 pts)
│
├── EPIC: CAMS-4 Review & Approve (13 pts) 🔶 IN PROGRESS
│   ├── Story: CAMS-41 View pending (3 pts) 🔶
│   │   ├── Sub-task: Backend route ✅
│   │   ├── Sub-task: HTML template 🔶
│   │   ├── Sub-task: CSS styling
│   │   ├── Sub-task: JavaScript sorting
│   │   └── Sub-task: Testing
│   │
│   ├── Story: CAMS-42 Review summary (5 pts)
│   │   ├── Sub-task: Backend data prep
│   │   ├── Sub-task: HTML template
│   │   ├── Sub-task: FHIR viewer
│   │   ├── Sub-task: Safety flag display
│   │   └── Sub-task: Testing
│   │
│   ├── Story: CAMS-43 Approve/reject (5 pts)
│   ├── Story: CAMS-44 Override flags (3 pts)
│   └── Story: CAMS-45 View history (3 pts)
│
└── EPIC: CAMS-5 Financial Assistance (21 pts) 🔜 TO DO
    ├── Story: Check eligibility (5 pts)
    ├── Story: Calculate costs (5 pts)
    ├── Story: Compare plans (5 pts)
    ├── Story: Loan options (3 pts)
    └── Story: Advisor request (3 pts)

SPRINTS:
├── Sprint 1 (Weeks 3-4) ✅ DONE - 21 pts completed
├── Sprint 2 (Weeks 5-6) ✅ DONE - 34 pts completed
├── Sprint 3 (Weeks 7-8) ✅ DONE - 21 pts completed
├── Sprint 4 (Weeks 9-10) 🔶 ACTIVE - 8/13 pts done
└── Sprint 5 (Weeks 11-12) 🔜 PLANNED - 21 pts

TEAM:
├── Chadwick Ng (UC-01 owner)
├── Saahir Khan (UC-02 owner)
├── Sarvadnya Kamble (UC-03 owner)
├── Thanh Le (UC-04 owner)
└── Venkatesh Badri (UC-05 owner)
```

---

## ✅ Setup Checklist

Use this to verify you've completed all steps:

### Account & Project
- [ ] Created Jira account
- [ ] Created project "Clinical AI Medical System" (CAMS)
- [ ] Configured board columns (6 columns)
- [ ] Set WIP limits
- [ ] Invited all team members

### Epics
- [ ] Created UC-01 Epic (Insurance)
- [ ] Created UC-02 Epic (Clinical Analysis)
- [ ] Created UC-03 Epic (Patient History)
- [ ] Created UC-04 Epic (Review & Approve)
- [ ] Created UC-05 Epic (Financial Assistance)

### User Stories
- [ ] Created 5 stories for UC-04
- [ ] Added acceptance criteria to each
- [ ] Estimated story points
- [ ] Assigned to team members
- [ ] Added labels and priorities

### Tasks
- [ ] Broke down UC-04 stories into sub-tasks
- [ ] Estimated time for each sub-task
- [ ] Created ~25 total sub-tasks

### Sprints
- [ ] Created Sprint 4
- [ ] Added UC-04 stories to sprint
- [ ] Set sprint goal
- [ ] Set start/end dates
- [ ] Started sprint

### Configuration
- [ ] Added quick filters
- [ ] Customized card layout
- [ ] Set up swimlanes
- [ ] Configured permissions
- [ ] Linked GitHub (optional)

### Team Readiness
- [ ] All members can access board
- [ ] All members know their assignments
- [ ] Daily standup time scheduled
- [ ] Sprint review date set
- [ ] Retrospective date set

---

## 🎯 Quick Reference

### Common Actions

| Action | How To |
|--------|--------|
| Create story | Click "Create" → Select "Story" |
| Add sub-task | Open story → "Add child issue" → "Sub-task" |
| Start working | Drag card to "In Progress" |
| Mark complete | Drag card to "Done" |
| Add comment | Open issue → Type in comment box |
| Assign to me | Open issue → Click assignee → Select yourself |
| Set priority | Open issue → Click priority dropdown |
| Add label | Open issue → Click labels → Type & create |
| Link issues | Open issue → "Link issue" → Select type |
| Flag blocker | Open issue → "..." → "Block issue" |
| Log time | Open issue → "..." → "Log work" |

---

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `C` | Create issue |
| `G` then `D` | Go to dashboard |
| `G` then `B` | Go to backlog |
| `/` | Quick search |
| `.` | Open command palette |
| `J` | Next issue |
| `K` | Previous issue |
| `E` | Edit issue |
| `A` | Assign to me |
| `I` | Assign to someone |

Press `?` in Jira to see all shortcuts.

---

## 📚 Resources

### Jira Help
- **Official Docs**: https://support.atlassian.com/jira-software-cloud/
- **Video Tutorials**: https://university.atlassian.com/
- **Community**: https://community.atlassian.com/

### Your Project Docs
- `AGILE_PROJECT_GUIDE.md` - Agile principles
- `FEATURES_SUMMARY.md` - Feature status
- `IMPLEMENTATION_SUMMARY_SESSION.md` - Latest progress

---

## 🎉 You're Ready!

Once you complete this setup, you'll have:
- ✅ Professional project tracking
- ✅ Clear visibility into progress
- ✅ Organized sprint planning
- ✅ Team collaboration tools
- ✅ Automatic reporting
- ✅ Audit trail for coursework

**Time to setup**: 2-3 hours  
**Time saved per week**: 5+ hours  
**ROI**: Massive! 🚀

---

**Need Help?**
- Jira has built-in chat support (bottom right corner)
- Post in your team Slack/Discord
- Review Atlassian University tutorials

**Good luck with Stage 2!** 🎓

---

**Document Version**: 1.0  
**Last Updated**: October 28, 2025  
**Authors**: HACKERJEE Team - ELEC5620 Group 7  
**University**: University of Sydney

