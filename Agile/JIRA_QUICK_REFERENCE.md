# 🎯 JIRA Quick Reference Card
## Clinical AI Medical System - Daily Workflow

**Print this page and keep it handy!**

---

## 🌅 Morning Routine (5 minutes)

1. **Open Jira** → Your board
2. **Filter** → "My Items"
3. **Update cards**:
   - Move completed items to DONE
   - Move items you'll work on today to IN PROGRESS
4. **Check for** @mentions and comments
5. **Ready for standup** ✅

---

## 💬 During Standup (15 minutes)

**Your turn to speak**:

1. **Yesterday**: Point to cards moved to DONE or IN REVIEW
2. **Today**: Point to cards in IN PROGRESS
3. **Blockers**: Mention any BLOCKED items

**Scrum Master updates board live during meeting**

---

## 🔨 While Working

### Starting a Task

```
1. Find your task/story
2. Click and drag to "IN PROGRESS"
3. (Optional) Add comment: "Starting [feature name]"
```

### Making Progress

```
Every 2-3 hours:
1. Open your task
2. Add comment with progress update
3. Example: "Backend complete ✅, working on frontend now"
```

### When Stuck (Blocker)

```
1. Open the task
2. Click "..." menu → "Block issue"
3. Describe the blocker
4. Notify team in Slack: "🚨 Blocked on CAMS-41"
```

### Ready for Review

```
1. Move card to "IN REVIEW"
2. Add comment: "@reviewer-name ready for review"
3. (Optional) Link GitHub PR
```

### Completing a Task

```
1. Ensure all acceptance criteria met ✅
2. Add comment: "All tests passed, moving to DONE"
3. Drag to "DONE" column
4. 🎉 Celebrate!
```

---

## 🔍 Quick Actions

| I Want To... | How To Do It |
|-------------|-------------|
| **Create new story** | Press `C` → Select "Story" → Fill form |
| **Add sub-task** | Open story → "Add child issue" → "Sub-task" |
| **Assign to myself** | Open issue → Click assignee → Select me |
| **Change priority** | Open issue → Click priority → Select level |
| **Add comment** | Open issue → Scroll to bottom → Type |
| **Link GitHub PR** | Open issue → "Link" → Paste PR URL |
| **Flag as blocked** | Open issue → "..." → "Block issue" |
| **Log time worked** | Open issue → "..." → "Log work" → Enter time |
| **Search for issue** | Press `/` → Type issue key (e.g., CAMS-41) |
| **View my tasks** | Board → Quick Filter → "My Items" |
| **View sprint progress** | Reports → Burndown chart |

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `C` | **C**reate new issue |
| `E` | **E**dit current issue |
| `A` | **A**ssign to me |
| `M` | Add co**m**ment |
| `/` | Quick search |
| `?` | Show all shortcuts |

---

## 📝 Comment Templates

### Progress Update
```
✅ Completed: [What you finished]
🔧 Working on: [Current task]
⏱️ ETA: [Time remaining]
```

### Code Review Request
```
@reviewer-name Ready for review

Changes:
- [Change 1]
- [Change 2]

Testing:
- [How you tested]

GitHub PR: [link]
```

### Blocker Alert
```
🚨 BLOCKED

Issue: [What's blocking you]
Impact: [How it affects progress]
Need: [What you need to unblock]
```

### Testing Results
```
Testing Results:
✅ [Passed test 1]
✅ [Passed test 2]
❌ [Failed test 3] - see bug CAMS-XX
✅ [Passed test 4]

Overall: [Pass/Fail with conditions]
```

---

## 🎨 Label Guide

| Label | Use When |
|-------|----------|
| `frontend` | HTML/CSS/JS work |
| `backend` | Python/Flask work |
| `database` | Database schema/queries |
| `ai-pipeline` | AI module work |
| `critical` | Must finish this sprint |
| `bug` | Something is broken |
| `uc-01` to `uc-05` | Label by use case |
| `doctor-feature` | Doctor-facing feature |
| `patient-feature` | Patient-facing feature |

**Add labels**: Open issue → Click "Labels" → Type to search/create

---

## 📊 Your Sprint at a Glance

### Check Sprint Health

**Daily** (before standup):
```
Board → Active Sprint
Look for:
- ✅ Cards moving right (good!)
- ⚠️ Cards stuck in one column (investigate)
- 🚨 Red "Blocked" flags (address immediately)
```

**Weekly** (Monday):
```
Reports → Burndown Chart
Check:
- Red line vs. ideal gray line
- Above = behind schedule
- Below = ahead of schedule
- Adjust workload if needed
```

---

## 🎯 Story Point Reference

Use during estimation:

| Points | Complexity | Examples | Time Estimate |
|--------|-----------|----------|---------------|
| **1** | Trivial | Fix typo, add button | < 1 hour |
| **2** | Simple | Small template, basic route | 1-2 hours |
| **3** | Moderate | Template with logic, simple feature | 3-5 hours |
| **5** | Complex | Multi-step workflow, integration | 1-2 days |
| **8** | Very Complex | Full feature with testing | 3-5 days |
| **13** | Epic-sized | Too big! Break it down | > 1 week |

**If story is 13+ points, split it into smaller stories!**

---

## 🔄 Sprint Cycle

```
Week 1, Day 1: Sprint Planning (2-4 hours)
├── Review backlog
├── Estimate stories
├── Commit to sprint
└── Break down into tasks

Week 1-2, Daily: Standup (15 min)
├── Update board
├── Share progress
└── Flag blockers

Week 2, Day 13: Sprint Review (1-2 hours)
├── Demo completed work
├── Gather feedback
└── Update backlog

Week 2, Day 14: Retrospective (1-2 hours)
├── What went well
├── What to improve
└── Action items for next sprint

🔁 Repeat every 2 weeks
```

---

## 🚨 When Things Go Wrong

### Issue: Can't find my task
**Solution**: Press `/` → Type issue key (e.g., CAMS-41)

### Issue: Board is messy
**Solution**: Quick Filter → "My Items" to see only yours

### Issue: Forgot to update before standup
**Solution**: Take 2 min before meeting to update cards

### Issue: Story is too big (13+ points)
**Solution**: Break into smaller stories (3-5 points each)

### Issue: Sprint is behind schedule
**Solution**: 
1. Check burndown chart
2. Identify bottlenecks
3. Ask for help or reduce scope
4. Discuss in next standup

### Issue: Too many blockers
**Solution**:
1. Call ad-hoc meeting (don't wait for standup)
2. Address blockers first
3. Adjust sprint plan if needed

---

## 📋 Definition of DONE Checklist

Before moving to DONE, verify:

- [ ] Code written and tested
- [ ] All acceptance criteria met
- [ ] Code reviewed (if applicable)
- [ ] No console errors
- [ ] Works on mobile and desktop
- [ ] Documentation updated
- [ ] Committed to GitHub
- [ ] Comments added in Jira

---

## 🎓 Issue Hierarchy

```
Epic (UC-01, UC-02, etc.)
  │
  ├── Story (User story)
  │     │
  │     ├── Sub-task (Backend)
  │     ├── Sub-task (Frontend)
  │     └── Sub-task (Testing)
  │
  └── Bug (If something breaks)
```

**Epic** = Large feature (insurance, analysis)  
**Story** = User-facing functionality  
**Sub-task** = Technical implementation step  
**Bug** = Something that doesn't work

---

## 💡 Pro Tips

### Tip 1: Update in Real-Time
Don't wait for standup to update your board. Update as you work!

### Tip 2: Use Comments
Add comments when you make progress. Helps team visibility.

### Tip 3: Link Everything
Link related issues, GitHub PRs, and documentation URLs.

### Tip 4: Keep Stories Small
3-5 points is ideal. Easy to complete in a sprint.

### Tip 5: Celebrate Wins
When you move something to DONE, take a moment to feel good! 🎉

---

## 📱 Mobile Access

**Jira Mobile App**:
- iOS: https://apps.apple.com/app/jira-cloud/id1006972087
- Android: https://play.google.com/store/apps/details?id=com.atlassian.android.jira.core

**Quick actions on mobile**:
- View your tasks
- Add comments
- Update status
- Get notifications

---

## 🆘 Get Help

### In Jira
- Click **?** icon (bottom right) → "Contact support"
- Built-in chat available

### Team Resources
- Team Slack/Discord → `#jira-help` channel
- Project wiki → Jira documentation section
- Scrum Master → Ask during standup

### Official Docs
- https://support.atlassian.com/jira-software-cloud/
- https://university.atlassian.com/ (free courses)

---

## 🎯 Your UC-04 Sprint Goals

**Current Sprint**: Sprint 4 (Weeks 9-10)  
**Goal**: Complete Review & Approve frontend

### Stories in Sprint:
- ✅ CAMS-41: View Pending Reviews (3 pts) - 60% done
- 🔜 CAMS-42: Review AI Summary (5 pts)
- 🔜 CAMS-43: Approve/Reject (5 pts)
- 🔜 CAMS-44: Override Flags (3 pts)
- 🔜 CAMS-45: View History (3 pts)

**Total**: 19 points  
**Completed**: 8 points  
**Remaining**: 11 points

---

## ✅ Daily Checklist

Print this and check off daily:

**Morning**:
- [ ] Opened Jira board
- [ ] Reviewed my items
- [ ] Updated card statuses
- [ ] Ready for standup

**During Work**:
- [ ] Started tasks (moved to IN PROGRESS)
- [ ] Added progress comments
- [ ] Flagged any blockers
- [ ] Helped teammates if needed

**End of Day**:
- [ ] Moved completed tasks to DONE
- [ ] Added final comments
- [ ] Noted tomorrow's plan
- [ ] Board reflects reality

---

## 🏆 Success Metrics

Your team is doing well when:

✅ **Velocity is consistent** (18-22 points per sprint)  
✅ **Few blockers** (< 2 per sprint)  
✅ **Cards move steadily** (not stuck in one column)  
✅ **Board is up-to-date** (updated daily)  
✅ **Sprint goal achieved** (demo-ready features)  
✅ **Team is happy** (retrospectives show improvement)

---

**Keep this handy! You'll reference it daily.** 📌

---

**Version**: 1.0  
**Last Updated**: October 28, 2025  
**Team**: HACKERJEE - ELEC5620 Group 7

