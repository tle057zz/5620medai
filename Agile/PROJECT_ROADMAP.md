# 🗺️ Project Roadmap - Visual Guide
## Clinical AI Medical System - Sprint Timeline

**Print this page for your team room!** 🖨️

---

## 📅 Sprint Timeline Overview

```
SPRINT 0 │ SPRINT 1 │ SPRINT 2 │ SPRINT 3 │ SPRINT 4 │ SPRINT 5 │ FINAL
Week 1-2 │ Week 3-4 │ Week 5-6 │ Week 7-8 │ Week 9-10│Week 11-12│Week 13-14
─────────┼──────────┼──────────┼──────────┼──────────┼──────────┼──────────
Foundation  Insurance  Clinical   Patient    Review     Finance    Polish
  Setup      Quotes    Analysis   History    & Approve  Assist    & Deploy
   ✅         ✅         ✅         ✅          🔶         🔜         🔜
  8 pts      21 pts     34 pts     21 pts     13 pts     21 pts     TBD
```

---

## 🎯 Sprint Breakdown

### ✅ SPRINT 0: Foundation (COMPLETE)
**Weeks 1-2 | 8 Story Points**

```
┌────────────────────────────────────────┐
│  🏗️  FOUNDATION SETUP                  │
├────────────────────────────────────────┤
│  ✅ User authentication system          │
│  ✅ Role-based access (P/D/A)           │
│  ✅ Flask web app + Bootstrap UI        │
│  ✅ Database schema design              │
│  ✅ Project structure                   │
└────────────────────────────────────────┘

Demo: Working login system with 3 dashboards
```

---

### ✅ SPRINT 1: Insurance Quote (COMPLETE)
**Weeks 3-4 | 21 Story Points | Owner: Chadwick Ng**

```
┌────────────────────────────────────────┐
│  💼 UC-01: INSURANCE QUOTES            │
├────────────────────────────────────────┤
│  ✅ Health data entry form              │
│  ✅ Medical document upload             │
│  ✅ AI risk assessment engine           │
│  ✅ Ranked quote generation             │
│  ✅ Plan comparison view                │
│  ✅ Cost breakdown & simulation         │
│  ✅ Doctor review workflow              │
│  ✅ Quote history tracking              │
└────────────────────────────────────────┘

Demo: Patient requests quote → AI ranks options → 
      Compare plans → Share with doctor
```

---

### ✅ SPRINT 2: Clinical Analysis (COMPLETE)
**Weeks 5-6 | 34 Story Points | Owner: Saahir Khan**

```
┌────────────────────────────────────────┐
│  🧠 UC-02: CLINICAL ANALYSIS           │
├────────────────────────────────────────┤
│  ✅ Multi-format upload (PDF/TXT/IMG)   │
│  ✅ Stage 1: OCR text extraction        │
│  ✅ Stage 2: Clinical sectionizer       │
│  ✅ Stage 3: NER entity recognition     │
│  ✅ Stage 4: Ontology linking           │
│  ✅ Stage 5: FHIR R4 bundle             │
│  ✅ Stage 6: Patient explanations       │
│  ✅ Stage 7: Safety checker             │
│  ✅ Analysis history view               │
└────────────────────────────────────────┘

Demo: Upload medical PDF → AI processes → 
      FHIR data + Explanation + Safety alerts
```

---

### ✅ SPRINT 3: Patient History (COMPLETE)
**Weeks 7-8 | 21 Story Points | Owner: Sarvadnya Kamble**

```
┌────────────────────────────────────────┐
│  📊 UC-03: PATIENT HISTORY             │
├────────────────────────────────────────┤
│  ✅ Database integration (SQLite)       │
│  ✅ Patient history dashboard           │
│  ✅ Medical timeline (interactive)      │
│  ✅ Data quality assessment             │
│  ✅ Gap detection & alerts              │
│  ✅ Trend analysis (conditions/vitals)  │
│  ✅ JSON export functionality           │
│  ✅ Empty state UX                      │
└────────────────────────────────────────┘

Demo: Doctor searches patient → Dashboard shows 
      history → Timeline view → Export report
```

---

### 🔶 SPRINT 4: Review & Approve (IN PROGRESS)
**Weeks 9-10 | 13 Story Points | Owner: Thanh Le**

```
┌────────────────────────────────────────┐
│  ✍️  UC-04: REVIEW AI OUTPUT           │
├────────────────────────────────────────┤
│  ✅ Backend: Approval models            │
│  ✅ Backend: 5 Flask routes             │
│  ✅ Backend: Safety validation          │
│  ✅ Backend: Digital signatures         │
│  🔶 Frontend: Pending reviews           │ ← YOU ARE HERE
│  🔜 Frontend: Review form               │
│  🔜 Frontend: Approval history          │
│  🔜 Frontend: Decision details          │
└────────────────────────────────────────┘

Progress: 8/13 points (62%)
Remaining: 4 templates (~3-4 hours)

Demo Goal: Doctor reviews AI output → 
           Evaluates safety → Approves/rejects
```

---

### 🔜 SPRINT 5: Financial Assistance (PLANNED)
**Weeks 11-12 | 21 Story Points | Owner: Venkatesh Badri**

```
┌────────────────────────────────────────┐
│  💰 UC-05: FINANCIAL ASSISTANCE        │
├────────────────────────────────────────┤
│  🔜 Subsidy eligibility checker         │
│  🔜 Out-of-pocket cost calculator       │
│  🔜 Subsidized plan comparison          │
│  🔜 Affordability scoring               │
│  🔜 Loan matching engine                │
│  🔜 Human advisor request               │
│  🔜 Doctor plan review                  │
│  🔜 Financial assistance export         │
└────────────────────────────────────────┘

Demo Plan: Patient checks eligibility → 
           System calculates costs → Recommends 
           affordable plans → Loan options
```

---

### 🔜 SPRINT 6: Polish & Deploy (PLANNED)
**Weeks 13-14 | TBD Story Points**

```
┌────────────────────────────────────────┐
│  🚀 FINAL POLISH & DEPLOYMENT          │
├────────────────────────────────────────┤
│  🔜 Automated testing (pytest)          │
│  🔜 Performance optimization            │
│  🔜 Database migration (PostgreSQL)     │
│  🔜 Security hardening                  │
│  🔜 User documentation                  │
│  🔜 Deployment guide                    │
│  🔜 CI/CD pipeline                      │
│  🔜 Final demo preparation              │
└────────────────────────────────────────┘

Demo Goal: Full end-to-end workflow demo
```

---

## 📊 Feature Completion Matrix

```
╔═══════════════════════════════════════════════════════════════════╗
║  FEATURE          │ BACKEND │ FRONTEND │ TESTING │ DOCS │ STATUS  ║
╠═══════════════════════════════════════════════════════════════════╣
║  UC-01: Insurance │   ✅    │    ✅    │   ✅    │  ✅  │   ✅    ║
║  UC-02: Analysis  │   ✅    │    ✅    │   ✅    │  ✅  │   ✅    ║
║  UC-03: History   │   ✅    │    ✅    │   ✅    │  ✅  │   ✅    ║
║  UC-04: Review    │   ✅    │    🔶    │   🔜    │  ✅  │   🔶    ║
║  UC-05: Finance   │   🔜    │    🔜    │   🔜    │  🔜  │   🔜    ║
╚═══════════════════════════════════════════════════════════════════╝

Legend: ✅ Done | 🔶 In Progress | 🔜 Planned
```

---

## 🎯 Story Point Distribution

```
Total Project: 110 Story Points

COMPLETED (76 pts - 69%):
████████████████████████████████████░░░░░ 
├─ Sprint 0: 8 pts  ████
├─ Sprint 1: 21 pts ███████████
├─ Sprint 2: 34 pts ██████████████████
└─ Sprint 3: 21 pts ███████████

IN PROGRESS (13 pts - 12%):
██████░░░░
└─ Sprint 4: 13 pts (8 done, 5 remaining)

REMAINING (21 pts - 19%):
███████░░░
└─ Sprint 5: 21 pts
```

---

## 🏃‍♂️ Team Velocity Trend

```
Story Points per Sprint

40│                  
  │                  ●34
35│                  │
  │                  │
30│                  │
  │                  │
25│                  │
  │         ●21      │      ●21
20│         │        │      │
  │         │        │      │      ●13 (planned)
15│         │        │      │      │
  │         │        │      │      │
10│  ●8     │        │      │      │
  │  │      │        │      │      │
 5│  │      │        │      │      │
  │  │      │        │      │      │
 0└──┴──────┴────────┴──────┴──────┴──────►
   S0   S1      S2      S3      S4

Average Velocity: 21 points/sprint
Trend: Consistent and healthy ✅
```

---

## 📅 Milestone Timeline

```
WEEK 1-2   ██████ Setup Complete
           └─ Login system ready

WEEK 3-4   ██████ Insurance Feature
           └─ Quote generation working

WEEK 5-6   ██████ AI Pipeline Complete
           └─ Full 7-stage processing

WEEK 7-8   ██████ Patient History
           └─ Timeline & trends ready

WEEK 9-10  ███░░░ Review System        ← YOU ARE HERE
           └─ Backend done, UI in progress

WEEK 11-12 ░░░░░░ Financial Assistance
           └─ Planned

WEEK 13-14 ░░░░░░ Polish & Deploy
           └─ Final demo
```

---

## 🎨 Tech Stack Overview

```
┌─────────────────────────────────────────────┐
│  FRONTEND                                    │
│  • HTML5 + Bootstrap 5                      │
│  • JavaScript (vanilla)                     │
│  • Responsive design                        │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  BACKEND                                     │
│  • Python 3.10+                             │
│  • Flask web framework                      │
│  • Flask-Login (auth)                       │
│  • Flask-SQLAlchemy (ORM)                   │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  AI/ML PIPELINE                              │
│  • SpaCy (NER)                              │
│  • Tesseract (OCR)                          │
│  • SapBERT (entity linking)                 │
│  • Custom FHIR mapper                       │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  DATABASE                                    │
│  • SQLite (development)                     │
│  • PostgreSQL (production ready)            │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  PROJECT MANAGEMENT                          │
│  • Git + GitHub                             │
│  • Jira (Sprint tracking)                   │
│  • Agile/Scrum methodology                  │
└─────────────────────────────────────────────┘
```

---

## 👥 Team Roles & Ownership

```
┌─────────────────────────────────────────────┐
│  TEAM MEMBER          │ USE CASE │ ROLE     │
├───────────────────────┼──────────┼──────────┤
│  Chadwick Ng          │ UC-01    │ Dev      │
│  Insurance Quotes     │ 21 pts   │ ✅ Done  │
├───────────────────────┼──────────┼──────────┤
│  Saahir Khan          │ UC-02    │ Dev      │
│  Clinical Analysis    │ 34 pts   │ ✅ Done  │
├───────────────────────┼──────────┼──────────┤
│  Sarvadnya Kamble     │ UC-03    │ Dev      │
│  Patient History      │ 21 pts   │ ✅ Done  │
├───────────────────────┼──────────┼──────────┤
│  Thanh Le             │ UC-04    │ Dev      │
│  Review & Approve     │ 13 pts   │ 🔶 62%   │
├───────────────────────┼──────────┼──────────┤
│  Venkatesh Badri      │ UC-05    │ Dev      │
│  Financial Assist     │ 21 pts   │ 🔜 Plan  │
└───────────────────────┴──────────┴──────────┘

Cross-functional: All team members contribute to
integration, testing, and documentation
```

---

## 🎯 Sprint 4 Focus (Current)

### Week 9 (This Week)

**Monday**:
- ✅ Sprint planning meeting
- ✅ Stories assigned
- ✅ Tasks broken down

**Tuesday-Thursday**:
- 🔶 Create `pending_ai_reviews.html`
- 🔶 Create `review_ai_output.html`
- 🔜 Create `review_history.html`

**Friday**:
- 🔜 Create `approval_decision_detail.html`
- 🔜 Integration testing
- 🔜 Code review

---

### Week 10 (Next Week)

**Monday-Tuesday**:
- 🔜 Bug fixes from testing
- 🔜 UI polish and refinement

**Wednesday**:
- 🔜 End-to-end testing
- 🔜 Documentation updates

**Thursday**:
- 🔜 Sprint review preparation
- 🔜 Demo practice

**Friday**:
- 🔜 Sprint review (demo)
- 🔜 Sprint retrospective
- 🔜 Sprint 5 planning

---

## 📋 Definition of Done

Before marking UC-04 as complete:

### Code Complete
- [ ] All 4 templates created
- [ ] All routes working
- [ ] No console errors
- [ ] Code reviewed

### Functionality
- [ ] Pending reviews page works
- [ ] Review form functional
- [ ] Approval/reject working
- [ ] History view displays
- [ ] Digital signatures generated

### Testing
- [ ] Manual testing complete
- [ ] All acceptance criteria met
- [ ] Mobile responsive
- [ ] Cross-browser tested

### Documentation
- [ ] Code comments added
- [ ] README updated
- [ ] User guide written
- [ ] API documented

### Integration
- [ ] Merged to main branch
- [ ] No merge conflicts
- [ ] Deployed to staging
- [ ] Demo ready

---

## 🚀 Critical Path to Completion

```
Current State (90%)
    ↓
[UC-04 Templates] ← CRITICAL (3-4 hours)
    ↓
[UC-04 Testing] (2-3 hours)
    ↓
Sprint 4 Complete (95%)
    ↓
[UC-05 Backend] (1-2 days)
    ↓
[UC-05 Frontend] (1-2 days)
    ↓
[UC-05 Testing] (4-6 hours)
    ↓
Sprint 5 Complete (100%)
    ↓
[Polish & Testing] (1 week)
    ↓
PROJECT COMPLETE 🎉
```

**Estimated Time to 100%**: 3-4 weeks

---

## 🎓 Learning Objectives (Agile Focus)

### Sprint Planning ✅
- [x] Understand backlog prioritization
- [x] Estimate story points
- [x] Commit to realistic sprint goals

### Daily Standup 🔜
- [ ] Run effective 15-min standups
- [ ] Identify blockers early
- [ ] Update board in real-time

### Sprint Review 🔜
- [ ] Demo working software
- [ ] Gather stakeholder feedback
- [ ] Adjust backlog priorities

### Retrospective 🔜
- [ ] Reflect on process
- [ ] Identify improvements
- [ ] Implement action items

### Jira Mastery 🔜
- [ ] Set up epics and stories
- [ ] Track velocity
- [ ] Generate reports
- [ ] Link to GitHub

---

## 📊 Success Metrics

### Quantitative

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Story Points Complete | 110 | 76 | 🟡 69% |
| Sprints on Time | 100% | 100% | 🟢 |
| Velocity Consistency | ±3 pts | ✅ | 🟢 |
| Code Coverage | >60% | TBD | 🟡 |
| Bugs per Sprint | <5 | 2 | 🟢 |

### Qualitative

- ✅ Working demos every sprint
- ✅ Stakeholder satisfaction
- ✅ Team collaboration strong
- ✅ Clear documentation
- 🔜 Automated testing
- 🔜 Production ready

---

## 🎉 Achievements Unlocked

- ✅ **Foundation Builder**: Set up full-stack app
- ✅ **AI Integrator**: Connected 7-stage pipeline
- ✅ **FHIR Master**: Generated valid FHIR R4 bundles
- ✅ **Data Wizard**: Built patient history analytics
- ✅ **Agile Practitioner**: 3 successful sprints
- 🔜 **Workflow Orchestrator**: Review system (in progress)
- 🔜 **Full Stack Champion**: Complete all 5 use cases

---

## 🗓️ Key Dates

| Date | Milestone | Status |
|------|-----------|--------|
| Week 2 | Foundation complete | ✅ |
| Week 4 | UC-01 demo | ✅ |
| Week 6 | UC-02 demo | ✅ |
| Week 8 | UC-03 demo | ✅ |
| **Week 10** | **UC-04 demo** | **🔶 This Week!** |
| Week 12 | UC-05 demo | 🔜 |
| Week 14 | Final presentation | 🔜 |

---

## 🎯 Your Mission (Sprint 4)

```
┌──────────────────────────────────────────────┐
│  SPRINT GOAL                                  │
│  "Complete UC-04 Review & Approve frontend"  │
│                                               │
│  TASKS THIS WEEK:                             │
│  1. Create pending_ai_reviews.html           │
│  2. Create review_ai_output.html             │
│  3. Create review_history.html               │
│  4. Create approval_decision_detail.html     │
│  5. Integration testing                       │
│  6. Demo preparation                          │
│                                               │
│  SUCCESS CRITERIA:                            │
│  ✓ All templates render correctly            │
│  ✓ Doctor can review and approve AI output   │
│  ✓ Audit trail works                          │
│  ✓ Demo-ready for Friday                     │
└──────────────────────────────────────────────┘
```

---

**Print this roadmap and put it on your wall!** 📌

Track your progress daily. You're almost there! 🚀

---

**Version**: 1.0  
**Last Updated**: October 28, 2025  
**Team**: HACKERJEE - ELEC5620 Group 7  
**University**: University of Sydney

**Current Status**: 90% Complete | Sprint 4 Active | UC-04 62% Done

