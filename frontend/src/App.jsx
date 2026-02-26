import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Components
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import LoadingSpinner from './components/LoadingSpinner';
import Chat from './components/Chat';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Dashboard from './pages/Dashboard';
import BioData from './pages/BioData';
import Assessment from './pages/Assessment';
import Courses from './pages/Courses';
import CourseDetail from './pages/CourseDetail';
import Mentors from './pages/Mentors';
import Practice from './pages/Practice';
import PracticeQuestions from './pages/PracticeQuestions';
import Tests from './pages/Tests';
import TestTaking from './pages/TestTaking';
import AssessmentTaking from './pages/AssessmentTaking';
import Certificate from './pages/Certificate';
import Profile from './pages/Profile';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminUsers from './pages/admin/AdminUsers';
import AdminCourses from './pages/admin/AdminCourses';
import AdminMentors from './pages/admin/AdminMentors';
import AdminManageMentors from './pages/admin/AdminManageMentors';
import AdminAnalytics from './pages/admin/AdminAnalytics';
import AdminQuestions from './pages/admin/AdminQuestions';
import AdminReports from './pages/admin/AdminReports';
import AdminWeeklyEvaluations from './pages/admin/AdminWeeklyEvaluations';

// Weekly Questions Pages
import WeeklyEvaluation from './pages/WeeklyEvaluation';
import EvaluationTaking from './pages/EvaluationTaking';
import EvaluationScores from './pages/EvaluationScores';

// Mentor Pages
import MentorDashboard from './pages/mentor/MentorDashboard';
import MentorProfile from './pages/mentor/MentorProfile';
import MentorChats from './pages/mentor/MentorChats';
import MentorSessions from './pages/mentor/MentorSessions';
import MentorStudents from './pages/mentor/MentorStudents';
import MentorBookings from './pages/mentor/MentorBookings';

// Video Call Pages
import VideoCall from './pages/VideoCall';
import VideoCallManagement from './pages/VideoCallManagement';


// Protected Route Component
const ProtectedRoute = ({ children, adminOnly = false, mentorOnly = false }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  if (adminOnly && !user.is_admin) {
    return <Navigate to="/dashboard" replace />;
  }
  
  if (mentorOnly && !user.is_mentor) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

// Public Route Component (redirect if already logged in)
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  if (user) {
    // Redirect based on user role
    if (user.is_admin && !user.is_mentor) {
      return <Navigate to="/admin" replace />;
    } else if (user.is_mentor && !user.is_admin) {
      return <Navigate to="/mentor" replace />;
    } else if (user.is_admin && user.is_mentor) {
      return <Navigate to="/admin" replace />;
    } else {
      return <Navigate to="/dashboard" replace />;
    }
  }
  
  return children;
};

function AppContent() {
  const { user } = useAuth();
  
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      
      <main className="flex-grow">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Home />} />
          <Route path="/login" element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          } />
          <Route path="/signup" element={
            <PublicRoute>
              <Signup />
            </PublicRoute>
          } />
          <Route path="/forgot-password" element={
            <PublicRoute>
              <ForgotPassword />
            </PublicRoute>
          } />
          <Route path="/reset-password" element={
            <PublicRoute>
              <ResetPassword />
            </PublicRoute>
          } />
          
          {/* Protected User Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/bio-data" element={
            <ProtectedRoute>
              <BioData />
            </ProtectedRoute>
          } />
          <Route path="/assessment" element={
            <ProtectedRoute>
              <Assessment />
            </ProtectedRoute>
          } />
          <Route path="/assessment/ai-personalized" element={
            <ProtectedRoute>
              <AssessmentTaking />
            </ProtectedRoute>
          } />
          <Route path="/assessment/:type" element={
            <ProtectedRoute>
              <AssessmentTaking />
            </ProtectedRoute>
          } />
          <Route path="/assessment/course/:courseId" element={
            <ProtectedRoute>
              <AssessmentTaking />
            </ProtectedRoute>
          } />
          <Route path="/courses" element={
            <ProtectedRoute>
              <Courses />
            </ProtectedRoute>
          } />
          <Route path="/courses/:courseId" element={
            <ProtectedRoute>
              <CourseDetail />
            </ProtectedRoute>
          } />
          <Route path="/courses/:courseId/test/:moduleId" element={
            <ProtectedRoute>
              <TestTaking />
            </ProtectedRoute>
          } />
          <Route path="/courses/:courseId/final-test" element={
            <ProtectedRoute>
              <TestTaking />
            </ProtectedRoute>
          } />
          <Route path="/courses/:courseId/certificate" element={
            <ProtectedRoute>
              <Certificate />
            </ProtectedRoute>
          } />
          <Route path="/certificates" element={
            <ProtectedRoute>
              <Certificate />
            </ProtectedRoute>
          } />
          <Route path="/mentors" element={
            <ProtectedRoute>
              <Mentors />
            </ProtectedRoute>
          } />
          <Route path="/practice" element={
            <ProtectedRoute>
              <Practice />
            </ProtectedRoute>
          } />
          <Route path="/practice-questions" element={
            <ProtectedRoute>
              <PracticeQuestions />
            </ProtectedRoute>
          } />
          <Route path="/practice/question/:questionId" element={
            <ProtectedRoute>
              <PracticeQuestions />
            </ProtectedRoute>
          } />
          <Route path="/tests" element={
            <ProtectedRoute>
              <Tests />
            </ProtectedRoute>
          } />
          <Route path="/test/:testId" element={
            <ProtectedRoute>
              <TestTaking />
            </ProtectedRoute>
          } />

          <Route path="/profile" element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } />
          
          {/* Weekly Questions Routes */}
          <Route path="/weekly-evaluation" element={
            <ProtectedRoute>
              <WeeklyEvaluation />
            </ProtectedRoute>
          } />
          <Route path="/evaluation/:attemptId" element={
            <ProtectedRoute>
              <EvaluationTaking />
            </ProtectedRoute>
          } />
          <Route path="/evaluation-scores" element={
            <ProtectedRoute>
              <EvaluationScores />
            </ProtectedRoute>
          } />
          
          {/* Video Call Routes */}
          <Route path="/video-calls" element={
            <ProtectedRoute>
              <VideoCallManagement />
            </ProtectedRoute>
          } />
          <Route path="/video-call/:callId" element={
            <ProtectedRoute>
              <VideoCall />
            </ProtectedRoute>
          } />

          
          {/* Mentor Routes */}
          <Route path="/mentor" element={
            <ProtectedRoute mentorOnly>
              <MentorDashboard />
            </ProtectedRoute>
          } />
          <Route path="/mentor/profile" element={
            <ProtectedRoute mentorOnly>
              <MentorProfile />
            </ProtectedRoute>
          } />
          <Route path="/mentor/chats" element={
            <ProtectedRoute mentorOnly>
              <MentorChats />
            </ProtectedRoute>
          } />
          <Route path="/mentor/sessions" element={
            <ProtectedRoute mentorOnly>
              <MentorSessions />
            </ProtectedRoute>
          } />

          <Route path="/mentor/students" element={
            <ProtectedRoute mentorOnly>
              <MentorStudents />
            </ProtectedRoute>
          } />
          <Route path="/mentor/bookings" element={
            <ProtectedRoute mentorOnly>
              <MentorBookings />
            </ProtectedRoute>
          } />


          
          {/* Admin Routes */}
          <Route path="/admin" element={
            <ProtectedRoute adminOnly>
              <AdminDashboard />
            </ProtectedRoute>
          } />
          <Route path="/admin/users" element={
            <ProtectedRoute adminOnly>
              <AdminUsers />
            </ProtectedRoute>
          } />
          <Route path="/admin/courses" element={
            <ProtectedRoute adminOnly>
              <AdminCourses />
            </ProtectedRoute>
          } />
          <Route path="/admin/mentors" element={
            <ProtectedRoute adminOnly>
              <AdminMentors />
            </ProtectedRoute>
          } />
          <Route path="/admin/questions" element={
            <ProtectedRoute adminOnly>
              <AdminQuestions />
            </ProtectedRoute>
          } />
          <Route path="/admin/reports" element={
            <ProtectedRoute adminOnly>
              <AdminReports />
            </ProtectedRoute>
          } />
          <Route path="/admin/weekly-evaluations" element={
            <ProtectedRoute adminOnly>
              <AdminWeeklyEvaluations />
            </ProtectedRoute>
          } />
          <Route path="/admin/manage-mentors" element={
            <ProtectedRoute adminOnly>
              <AdminManageMentors />
            </ProtectedRoute>
          } />
          <Route path="/admin/analytics" element={
            <ProtectedRoute adminOnly>
              <AdminAnalytics />
            </ProtectedRoute>
          } />
          
          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      
      <Footer />
      
      {/* Chat Support - Available for all logged-in users */}
      {user && <Chat />}
      
      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            theme: {
              primary: '#4aed88',
            },
          },
          error: {
            duration: 4000,
            theme: {
              primary: '#ff6b6b',
            },
          },
        }}
      />
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;