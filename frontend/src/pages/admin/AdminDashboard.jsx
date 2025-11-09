import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../utils/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import { 
  Users, 
  BookOpen, 
  Award,
  Clock,
  UserCheck,
  GraduationCap
} from 'lucide-react';
import toast from 'react-hot-toast';

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/admin/dashboard');
      if (response.data.success) {
        setDashboardData(response.data.dashboard);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading admin dashboard..." />;
  }

  const stats = dashboardData?.statistics || {};

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
          <p className="text-gray-600">
            Manage users, courses, mentors, and monitor system performance.
          </p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Users className="w-8 h-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Users</p>
                <p className="text-2xl font-bold text-gray-900">{stats.users?.total || 0}</p>
                <p className="text-sm text-green-600">{stats.users?.active || 0} active</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <BookOpen className="w-8 h-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Courses</p>
                <p className="text-2xl font-bold text-gray-900">{stats.courses?.total || 0}</p>
                <p className="text-sm text-green-600">{stats.courses?.active || 0} active</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Award className="w-8 h-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Assessments</p>
                <p className="text-2xl font-bold text-gray-900">{stats.assessments?.total || 0}</p>
                <p className="text-sm text-gray-600">Avg: {stats.assessments?.average_score || 0}%</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <GraduationCap className="w-8 h-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Certificates</p>
                <p className="text-2xl font-bold text-gray-900">{stats.certificates?.total || 0}</p>
                <p className="text-sm text-green-600">{stats.certificates?.issued || 0} issued</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Quick Actions */}
          <div>
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Quick Actions</h2>
              <div className="space-y-4">
                <Link
                  to="/admin/users"
                  className="flex items-center p-3 border border-gray-200 rounded-lg hover:border-primary-300 hover:shadow-sm transition-all group"
                >
                  <Users className="w-5 h-5 text-gray-500 group-hover:text-primary-600" />
                  <div className="ml-3">
                    <p className="font-medium text-gray-900 group-hover:text-primary-600">Manage Users</p>
                    <p className="text-sm text-gray-600">View and manage user accounts</p>
                  </div>
                </Link>

                <Link
                  to="/admin/courses"
                  className="flex items-center p-3 border border-gray-200 rounded-lg hover:border-primary-300 hover:shadow-sm transition-all group"
                >
                  <BookOpen className="w-5 h-5 text-gray-500 group-hover:text-primary-600" />
                  <div className="ml-3">
                    <p className="font-medium text-gray-900 group-hover:text-primary-600">Manage Courses</p>
                    <p className="text-sm text-gray-600">Create and edit courses</p>
                  </div>
                </Link>






              </div>
            </div>

            {/* Recent Activities */}
            <div className="card mt-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Recent Activities</h2>
              <div className="space-y-4">
                {dashboardData?.recent_activities?.new_users?.slice(0, 3).map((user, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <UserCheck className="w-4 h-4 text-green-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{user.name}</p>
                      <p className="text-xs text-gray-500">New user registered</p>
                    </div>
                    <span className="text-xs text-gray-400">
                      {new Date(user.created_at).toLocaleDateString()}
                    </span>
                  </div>
                ))}

                {dashboardData?.recent_activities?.recent_assessments?.slice(0, 2).map((assessment, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Award className="w-4 h-4 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{assessment.user_name}</p>
                      <p className="text-xs text-gray-500">
                        Completed {assessment.type} assessment ({assessment.score}%)
                      </p>
                    </div>
                    <span className="text-xs text-gray-400">
                      {new Date(assessment.completed_at).toLocaleDateString()}
                    </span>
                  </div>
                ))}

                {(!dashboardData?.recent_activities?.new_users?.length && 
                  !dashboardData?.recent_activities?.recent_assessments?.length) && (
                  <div className="text-center py-4">
                    <Clock className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">No recent activities</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>


      </div>
    </div>
  );
};

export default AdminDashboard;