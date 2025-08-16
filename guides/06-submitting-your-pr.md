# 06 – Submitting Your PR (5 mins)

*How to submit your hackathon contribution for evaluation*

## Quick Overview

All hackathon submissions go to the **main summer hackathon repository** where you found the tracks. This keeps everything organized in one place for judging and community visibility.

## Step-by-Step Submission

### 1. 🍴 Fork the Hackathon Repo
```bash
# If you haven't already:
git clone https://github.com/jentic/jentic-summer-hackathon.git
cd summer-hackathon-2025

# Or if you forked it:
git clone https://github.com/YOUR-USERNAME/jentic-summer-hackathon.git
cd summer-hackathon-2025
```

### 2. 🌿 Create Your Feature Branch
Use this naming convention for easy organization:
```bash
# Format: submission/track-XX-your-name-or-team
git checkout -b submission/track-06-jane-doe
git checkout -b submission/track-13-team-awesome
git checkout -b submission/track-02-multitrack-alice
```

### 3. 📁 Add Your Work to the Right Track Folder

**For most tracks:**
```bash
# Add your code/files to your track's submissions folder
tracks/track-06/submissions/your-name/
├── README.md           # Setup & demo instructions
├── your-prompts.md     # Your actual work
├── examples/           # Working examples
└── demo-screenshots/   # Visual proof
```

**For multi-track submissions:**
```bash
# Create a combined submission folder
tracks/multi-track-submissions/your-name/
├── README.md           # Overview of all tracks
├── track-06/          # Track 6 work
├── track-13/          # Track 13 work
└── demo-evidence/     # Screenshots/videos
```

### 4. 📝 Follow Your Track's Submission Structure

Each track has specific requirements - check your track folder for:
- `tracks/track-XX/README.md` - Submission requirements
- `tracks/track-XX/examples/` - Example submissions
- `tracks/track-XX/submission-template/` - File templates

**Essential files for ALL submissions:**
- `README.md` - Clear setup instructions
- `demo-evidence/` - Screenshots or video proof
- Your actual work (code, prompts, docs, etc.)

### 5. ✅ Use the Quality Checklists

Before submitting, run through the relevant checklist:
- **Prompts**: `checklists/prompt-submission-checklist.md`
- **API Specs**: `checklists/api-spec-quality-checklist.md`
- **Code/Tools**: `checklists/demo-readme-checklist.md`

### 6. 🧪 Test in Clean Environment

```bash
# Test your setup instructions work from scratch
cd /tmp
git clone https://github.com/YOUR-USERNAME/summer-hackathon-2025.git
cd summer-hackathon-2025/tracks/track-XX/submissions/your-name/

# Follow your own README - does it work?
# Fix any issues, then push updates
```

### 7. 🚀 Create Your Pull Request

```bash
# Push your branch
git add .
git commit -m "feat: Track XX submission by [Your Name]"
git push origin submission/track-XX-your-name

# Go to GitHub and open PR to main repo
```

**PR Template - Use This Format:**
```markdown
## [SUBMISSION] Track XX - [Project Name] by [Your Name]

### Track & Points
- **Primary Track**: Track XX - [Track Name] ([X] points)
- **Additional Tracks**: [if any]
- **Total Estimated Points**: [X] points

### What I Built
[2-3 sentence elevator pitch]

### Demo Evidence
- 📸 Screenshots: [link to demo-evidence folder]
- 🎥 Video Demo: [YouTube/Loom link if applicable]
- 🔗 Live Demo: [if applicable]

### Key Features
- [Bullet point 1]
- [Bullet point 2]
- [Bullet point 3]

### Setup Instructions
See README in `tracks/track-XX/submissions/[your-name]/README.md`

Quick start:
```bash
cd tracks/track-XX/submissions/[your-name]/
# Add 2-3 key commands here
```

### Files Changed
- `tracks/track-XX/submissions/[your-name]/` - All submission files
- [Any other relevant changes]

### Quality Checklist
- [ ] Followed track-specific submission requirements
- [ ] Included comprehensive README with setup instructions
- [ ] Added demo evidence (screenshots/video)
- [ ] Tested in clean environment
- [ ] Used relevant quality checklist

### Social Media (Bonus Points!)
- 🐦 Twitter: [link if posted]
- 💼 LinkedIn: [link if posted]
```

### 8. 🏆 Submit the Official Issue

After your PR is open:

1. Go to **Issues** tab in the hackathon repo
2. Click **New Issue**
3. Choose **"Project Submission"** template
4. Fill out completely (this is for official judging)
5. Link to your PR in the "Main PR Link" field

## 📋 Submission Requirements by Track Type

### 🎨 Prompt-Based Tracks (06)
```
your-name/
├── README.md                    # Setup & usage
├── prompts/
│   ├── base-prompts.md         # Your core prompts
│   ├── specialized-prompts.md  # Advanced variants
│   └── examples.md             # Working examples
├── demo-evidence/
│   ├── before-after.png        # Show improvement
│   └── conversation-logs.md    # Example conversations
└── evaluation/
    └── results.md              # Testing results
```

### 💻 Code-Based Tracks (01, 03, 04, 05, 07-09, 11-16, 18-20)
```
your-name/
├── README.md              # Setup & demo instructions
├── src/                   # Your source code
├── requirements.txt       # Dependencies
├── examples/             # Working examples
├── tests/                # Basic tests (if applicable)
├── demo-evidence/        # Screenshots/videos
└── docs/                 # Additional documentation
```

### 📊 Research Tracks (17)
```
your-name/
├── README.md              # Executive summary
├── research-report.md     # Main findings
├── methodology.md         # How you conducted research
├── data/                  # Any datasets/analysis
├── references.md          # Sources and citations
└── demo-evidence/         # Visualizations/charts
```

## 🆘 Common Issues & Solutions

### "I can't find the right folder structure"
Check `tracks/track-XX/examples/` for reference submissions from previous events.

### "My PR conflicts with main"
```bash
git checkout main
git pull upstream main
git checkout your-branch
git rebase main
# Resolve conflicts, then git push --force-with-lease
```

### "I worked on multiple tracks"
Create a `multi-track-submissions/your-name/` folder with clear organization by track.

### "I forked the wrong repo"
You want to fork `jentic/summer-hackathon-2025`, not the individual Jentic tool repos.

### "My submission is too large"
- Use `.gitignore` for large files
- Put videos on YouTube/Loom and link them
- Compress images before committing

## 🎯 Pro Tips for Strong Submissions

### Make It Easy for Judges
- **Clear README** - Judges should understand your project in 30 seconds
- **One-command demo** - `python demo.py` should just work
- **Visual evidence** - Screenshots speak louder than code

### Stand Out from the Crowd  
- **Solve real problems** - Address pain points you've experienced
- **Show measurable impact** - "Reduces setup time from 2 hours to 5 minutes"
- **Polish the presentation** - Clean code, good docs, professional README

### Maximize Your Points
- **Complete the core requirements** first, then add bonuses
- **Document thoroughly** - Good docs can bump you up a tier
- **Test everything** - Broken demos lose points fast
- **Share on social media** - Easy bonus points for posting

## 🎉 After Submission

### What Happens Next
1. **Automated checks** run on your PR (linting, basic tests)
2. **Community feedback** - Other participants may comment
3. **Judge evaluation** - Usually within 2-3 days
4. **Results announced** - Check Discord for updates

### Keep Building
- **Iterate based on feedback** - You can update your submission until deadline
- **Help others** - Comment on other PRs, share knowledge
- **Plan next steps** - Think about turning this into a real project

---

## 🚀 Ready to Submit?

**Checklist before opening PR:**
- [ ] Work is in correct track folder
- [ ] README has clear setup instructions
- [ ] Tested setup in clean environment
- [ ] Demo evidence included
- [ ] Quality checklist completed
- [ ] Branch named correctly
- [ ] PR description follows template

**Questions?** Ask in Discord `#summer-hackathon` - we're here to help!

---

*Remember: The goal isn't perfection, it's building something useful and learning. Ship it! 🚢*
