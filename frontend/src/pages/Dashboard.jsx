import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import { formatDateTime, getRelativeTime } from '../utils/dateUtils';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  BookOpen, 
  Users, 
  Award, 
  TrendingUp, 
  CheckCircle,
  Clock,
  Star,
  ArrowRight
} from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/user/dashboard');
      if (response.data.success) {
        setDashboardData(response.data.dashboard);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading your dashboard..." />;
  }

  const progress = dashboardData?.progress || {};
  const recentActivities = dashboardData?.recent_activities || [];

  const quickActions = [
    {
      title: 'Complete Bio Data',
      description: 'Fill out your profile information',
      link: '/bio-data',
      icon: Users,
      completed: progress.bio_data_completed,
      color: 'bg-blue-500'
    },
    {
      title: 'Take Assessment',
      description: 'Complete your skill assessment',
      link: '/assessment',
      icon: Award,
      completed: progress.total_assessments > 0,
      color: 'bg-green-500'
    },
    {
      title: 'Browse Courses',
      description: 'Explore available courses',
      link: '/courses',
      icon: BookOpen,
      completed: progress.total_courses > 0,
      color: 'bg-purple-500'
    },
    {
      title: 'Find Mentors',
      description: 'Connect with expert mentors',
      link: '/mentors',
      icon: Users,
      completed: false,
      color: 'bg-orange-500'
    },
    {
      title: 'Practice Questions',
      description: 'Test your knowledge with AI questions',
      link: '/practice-questions',
      icon: BookOpen,
      completed: false,
      color: 'bg-purple-500'
    },

  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.name}! 👋
          </h1>
          <p className="text-gray-600 mt-2">
            Continue your learning journey with SkillNova
          </p>
        </div>

        {/* Progress Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BookOpen className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Courses</p>
                <p className="text-2xl font-bold text-gray-900">
                  {progress.completed_courses}/{progress.total_courses}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Award className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Assessments</p>
                <p className="text-2xl font-bold text-gray-900">
                  {progress.total_assessments}
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Score</p>
                <p className="text-2xl font-bold text-gray-900">
                  {progress.average_score}%
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Star className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Status</p>
                <p className="text-lg font-bold text-gray-900">
                  In Progress
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="lg:col-span-2">
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {quickActions.map((action, index) => {
                  const Icon = action.icon;
                  return (
                    <Link
                      key={index}
                      to={action.link}
                      className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:shadow-sm transition-all group"
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`p-2 ${action.color} rounded-lg`}>
                          <Icon className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <h3 className="font-medium text-gray-900 group-hover:text-primary-600">
                              {action.title}
                            </h3>
                            {action.completed && (
                              <CheckCircle className="w-4 h-4 text-green-500" />
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            {action.description}
                          </p>
                        </div>
                        <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-primary-600" />
                      </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Recent Activities */}
          <div>
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Recent Activities</h2>
              {recentActivities.length > 0 ? (
                <div className="space-y-4">
                  {recentActivities.map((activity, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="p-2 bg-gray-100 rounded-lg">
                        <Clock className="w-4 h-4 text-gray-600" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          {activity.description}
                        </p>
                        <p className="text-xs text-gray-500 mt-1" title={formatDateTime(activity.date)}>
                          {getRelativeTime(activity.date)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Clock className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No recent activities</p>
                  <p className="text-sm text-gray-400">
                    Start by completing your bio data or taking an assessment
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Next Steps */}
        <div className="mt-8">
          <div className="card bg-gradient-to-r from-primary-50 to-accent-50 border-primary-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Complete Your Journey
                </h2>
                <p className="text-gray-600">
                  Follow these steps to enhance your skills
                </p>
              </div>
              <div className="hidden md:block">
                <Star className="w-16 h-16 text-primary-300" />
              </div>
            </div>
            
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="text-center">
                <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-2 text-sm font-bold">
                  1
                </div>
                <p className="text-sm font-medium">Complete Assessment</p>
              </div>
              <div className="text-center">
                <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-2 text-sm font-bold">
                  2
                </div>
                <p className="text-sm font-medium">Enroll in Courses</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;