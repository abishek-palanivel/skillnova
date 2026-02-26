# Git Push Commands for SkillNova

## Step 1: Check Git Status
```bash
git status
```

## Step 2: Add All Changes
```bash
git add .
```

## Step 3: Commit Changes
```bash
git commit -m "feat: Universal AI-powered learning platform with auto-generation

- Added AI question generation for ALL topics (AutoCAD, Photoshop, Python, etc.)
- Implemented auto-generation in tests, practice, and evaluations
- Fixed Gemini API initialization with graceful fallback
- Added support for 40+ course categories
- Enhanced AI course generator with smart topic detection
- Improved code evaluator with 14+ language support
- Added personalized AI certificate generation
- Implemented smart recommendations for all backgrounds
- Updated documentation with comprehensive guides
- Added .env.example for easy setup
- Cleaned up unwanted files and improved .gitignore

Features:
✅ Universal topic support (not just programming)
✅ Automatic question generation on demand
✅ AI-powered course creation
✅ Multi-language code evaluation
✅ Personalized certificates with QR codes
✅ Smart recommendations and learning paths
✅ Weekly automated evaluations
✅ Mentor system with video calls and chat
✅ Complete admin dashboard

Tech Stack: React.js, Flask, PostgreSQL, Google Gemini AI"
```

## Step 4: Push to GitHub

### If this is a new repository:
```bash
# Create repository on GitHub first, then:
git remote add origin https://github.com/yourusername/skillnova.git
git branch -M main
git push -u origin main
```

### If repository already exists:
```bash
git push origin main
```

## Step 5: Verify Push
```bash
git log --oneline -5
```

## Alternative: Push with Tags
```bash
# Create a version tag
git tag -a v3.0.0 -m "Universal AI-Powered Learning Platform"
git push origin main --tags
```

## Troubleshooting

### If you get "rejected" error:
```bash
# Pull first, then push
git pull origin main --rebase
git push origin main
```

### If you need to force push (use with caution):
```bash
git push origin main --force
```

### If you have large files:
```bash
# Check file sizes
git ls-files -z | xargs -0 du -h | sort -h | tail -20

# If needed, use Git LFS for large files
git lfs install
git lfs track "*.pdf"
git add .gitattributes
```

## GitHub Repository Description

**Short Description (for GitHub):**
```
Universal AI-powered learning platform supporting ANY topic with auto-generated questions, courses, and certificates. Built with React, Flask, PostgreSQL, and Google Gemini AI.
```

**Topics/Tags (for GitHub):**
```
ai, machine-learning, education, learning-platform, react, flask, postgresql, 
python, javascript, gemini-ai, code-evaluation, certificate-generation, 
autocad, photoshop, programming, web-development, online-learning, 
e-learning, lms, education-technology
```

**Website (if deployed):**
```
https://skillnova.example.com
```

## After Pushing

1. Go to your GitHub repository
2. Click "Settings" → "General"
3. Add description and topics
4. Enable "Issues" and "Discussions" if desired
5. Add a LICENSE file (MIT recommended)
6. Create a GitHub Pages site (optional)
7. Add repository social preview image (optional)

## Creating a Release

```bash
# After pushing, create a release on GitHub:
# 1. Go to repository → Releases → Create new release
# 2. Tag: v3.0.0
# 3. Title: "Universal AI-Powered Learning Platform v3.0.0"
# 4. Description: Copy from COMPLETE_AI_FIX_SUMMARY.md
# 5. Attach any release assets (optional)
# 6. Publish release
```

## Keeping Repository Updated

```bash
# Regular updates
git add .
git commit -m "fix: your fix description"
git push origin main

# For features
git commit -m "feat: your feature description"

# For documentation
git commit -m "docs: update documentation"

# For bug fixes
git commit -m "fix: fix bug description"
```
