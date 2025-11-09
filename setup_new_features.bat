@echo off
echo Setting up new SkillNova features...
echo.

echo Installing frontend dependencies...
cd frontend
call npm install recharts
echo Frontend dependencies installed!
echo.

cd ..
echo.
echo New features added:
echo 1. Admin Manage Mentors section - Add/Edit/Delete mentors with email notifications
echo 2. Admin Analytics Dashboard - Charts and insights
echo 3. User Video Call Management - Accept/Reject calls, view history
echo 4. Video Call Interface - Real-time video calls with WebRTC
echo.
echo To start the system:
echo 1. Run start_system.bat
echo 2. Navigate to http://localhost:3000
echo 3. Login as admin: admin@skillnova.com / abi@1234
echo.
echo New Admin Features:
echo - /admin/manage-mentors - Add mentors with auto-generated passwords
echo - /admin/analytics - View platform analytics and charts
echo.
echo New User Features:
echo - /video-calls - Manage video call sessions
echo - Video call interface with screen sharing and chat
echo.
pause