# SkillNova - AI-Powered Learning Platform with Weekly Evaluation System

💫 **"Shine with Skills. Grow with Guidance."**

## 🎯 Overview
SkillNova is a comprehensive AI-powered learning platform featuring automated weekly evaluations, multi-language code execution, and intelligent opportunity matching that connects learners with real-world career opportunities.

## ✨ Key Features

### 🤖 Weekly AI Evaluation System
- **Automated Weekly Tests**: AI generates 10 questions every Sunday (5 MCQ + 5 Coding)
- **Multi-Language Code Execution**: Python, JavaScript, Java, C++, C with real-time testing
- **Instant AI Scoring**: Immediate evaluation and detailed feedback
- **Opportunity Matching**: Automatic matching with internships and scholarships
- **Admin Workflow**: Complete management for sessions and opportunities

### 🎓 Core Learning Platform
- **User Registration & Authentication**: Secure JWT-based authentication
- **Skill Assessment & Testing**: Comprehensive evaluation system
- **Personalized Course Recommendations**: AI-driven learning paths
- **Mentor Matching & Sessions**: Expert guidance and mentorship
- **Practice Modules & Quizzes**: Interactive learning exercises
- **Admin Management Dashboard**: Complete system administration

## 🛠️ Tech Stack
- **Frontend**: React.js + Tailwind CSS + Monaco Editor
- **Backend**: Python 3.13.3 + Flask + SQLAlchemy
- **Database**: PostgreSQL with JSON support
- **AI Services**: Custom question generation and code evaluation
- **Code Execution**: Multi-language sandboxed execution
- **Email Service**: SMTP integration for notifications
- **Automation**: Schedule-based weekly task automation

## 📁 Project Structure
```
skillnova/
├── frontend/                    # React.js application
│   ├── src/pages/
│   │   ├── WeeklyEvaluation.jsx        # User evaluation interface
│   │   ├── OpportunityMatches.jsx      # Opportunity matching
│   │   └── admin/
│   │       └── AdminWeeklyEvaluation.jsx # Admin management
│   └── src/components/
│       └── CodeEditor.jsx              # Monaco code editor
├── backend/                     # Flask API server
│   ├── routes/
│   │   └── weekly_evaluation.py        # Weekly evaluation API
│   ├── models.py                       # Database models
│   ├── ai_question_generator.py        # AI question generation
│   ├── code_execution_service.py       # Multi-language execution
│   ├── weekly_automation.py            # Automated tasks
│   └── setup_weekly_evaluation.py      # Database setup
├── database/                    # PostgreSQL schemas
│   └── weekly_content_schema.sql       # Weekly evaluation schema
└── WEEKLY_EVALUATION_SYSTEM_SUMMARY.md # Complete documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- PostgreSQL 12+

### Installation & Setup

1. **Clone and Setup Database**
   ```bash
   git clone <repository-url>
   cd skillnova
   python backend/setup_weekly_evaluation.py
   ```

2. **Start Backend**
   ```bash
   start_system.bat
   # OR manually: cd backend && python app.py
   ```

3. **Start Frontend** (new terminal)
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Access the System**
   - **Frontend**: http://localhost:3000
   - **Admin Portal**: http://localhost:3000/admin/weekly-evaluation
   - **Weekly Evaluation**: http://localhost:3000/weekly-evaluation
   - **Backend API**: http://localhost:5000

### 👤 Test Accounts
- **Admin**: abishekopennova@gmail.com / abi@1234
- **Mentor**: abishekpopennova@gmail.com / abi@1234
- **Student**: abishekpalanivel212@gmail.com / abi@1234

## 🎮 User Experience

### For Students
1. **Take Weekly Evaluations** → Complete AI-generated assessments
2. **Code in Real-time** → Write and test code in multiple languages
3. **Get Instant Results** → Receive immediate AI scoring and feedback
4. **Discover Opportunities** → View matched internships and scholarships
5. **Request Connections** → Ask admin to connect with employers

### For Admins
1. **Manage Sessions** → Create and oversee weekly evaluations
2. **Add Opportunities** → Post internships and scholarships
3. **Review Requests** → Approve student contact requests
4. **Send Communications** → Email opportunities to qualified users

## 🤖 AI-Powered Features

- **Smart Question Generation**: Context-aware questions across multiple categories
- **Code Evaluation**: Secure multi-language execution with automatic scoring
- **Opportunity Matching**: Score-based algorithm with AI recommendations
- **Performance Analytics**: Detailed insights and progress tracking

## 🔄 Automation

- **Sunday 00:00**: Auto-generate new weekly evaluation sessions
- **Monday 01:00**: Cleanup old inactive sessions
- **Continuous**: Email notifications and opportunity matching

## 📊 System Status

✅ **Production Ready**  
✅ **Weekly Evaluation System**: Fully operational  
✅ **Multi-language Code Execution**: Python, JS, Java, C++, C  
✅ **Opportunity Matching**: Active with email workflow  
✅ **Admin Management**: Complete CRUD operations  
✅ **Email Notifications**: Configured and tested  

## 👨‍💻 Developer Information
- **Developer**: Abishek
- **LinkedIn**: https://www.linkedin.com/in/abishek-p-9ab80a326
- **Email**: abishekopennova@gmail.com

---

**SkillNova** - Empowering learners worldwide with AI-driven education and automated career opportunities.

