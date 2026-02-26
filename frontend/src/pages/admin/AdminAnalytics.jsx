import { useState, useEffect } from 'react';
import api from '../../utils/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts';
import { 
  TrendingUp, 
  Users, 
  BookOpen, 
  Award,
  MessageSquare,
  Video,
  Calendar,
  Target,
  Activity,
  BarChart3
} from 'lucide-react';
import toast from 'react-hot-toast';

const AdminAnalytics = () => {
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);
  const [userPerformance, setUserPerformance] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAnalytics();
    fetchUserPerformance();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/admin/analytics/dashboard');
      if (response.data.success) {
        const data = response.data.analytics;
        
        // Transform backend data to match frontend expectations
        const transformedData = {
          totalUsers: data.overview?.total_users || 0,
          totalCourses: data.overview?.total_courses || 0,
          totalCertificates: 0, // Placeholder
          totalVideoCalls: data.mentoring?.total_sessions || 0,
          userRegistrationTrend: (data.charts?.user_registrations || []).length > 0 
            ? (data.charts?.user_registrations || []).map(item => ({
                date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                users: item.count
              }))
            : [{ date: 'No Data', users: 0 }],
          courseCompletionRate: [
            { name: 'Completed', value: data.overview?.completion_rate || 0 },
            { name: 'In Progress', value: 100 - (data.overview?.completion_rate || 0) }
          ],
          userActivity: (data.charts?.user_registrations || []).length > 0
            ? (data.charts?.user_registrations || []).slice(-7).map(item => ({
                date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                activeUsers: item.count,
                newUsers: item.count
              }))
            : [{ date: 'No Data', activeUsers: 0, newUsers: 0 }],
          coursePerformance: (data.charts?.course_enrollments || []).length > 0
            ? (data.charts?.course_enrollments || []).slice(0, 10).map(item => ({
                courseName: item.course.substring(0, 20) + (item.course.length > 20 ? '...' : ''),
                enrollments: item.enrollments,
                completions: Math.floor(item.enrollments * (data.overview?.completion_rate || 0) / 100)
              }))
            : [{ courseName: 'No Courses', enrollments: 0, completions: 0 }]
        };
        
        setAnalytics(transformedData);
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      const errorMsg = error.response?.data?.message || 'Failed to load analytics data. Please check database connection.';
      toast.error(errorMsg);
      // Set empty analytics data
      setAnalytics({
        totalUsers: 0,
        totalCourses: 0,
        totalCertificates: 0,
        totalVideoCalls: 0,
        userRegistrationTrend: [{ date: 'No Data', users: 0 }],
        courseCompletionRate: [{ name: 'Completed', value: 0 }, { name: 'In Progress', value: 100 }],
        userActivity: [{ date: 'No Data', activeUsers: 0, newUsers: 0 }],
        coursePerformance: [{ courseName: 'No Courses', enrollments: 0, completions: 0 }]
      });
    }
  };

  const fetchUserPerformance = async () => {
    try {
      const response = await api.get('/admin/analytics/user-performance');
      if (response.data.success) {
        const data = response.data.user_performance;
        
        // Transform backend data to match frontend expectations
        const transformedData = {
          trends: (data.top_performers || []).length > 0
            ? (data.top_performers || []).map((user, index) => ({
                date: `User ${index + 1}`,
                averageScore: user.avg_score || 0,
                completionRate: user.course_count > 0 ? Math.round((user.assessment_count / user.course_count) * 100) : 0
              }))
            : [{ date: 'No Data', averageScore: 0, completionRate: 0 }]
        };
        
        setUserPerformance(transformedData);
      }
    } catch (error) {
      console.error('Failed to fetch user performance:', error);
      const errorMsg = error.response?.data?.message || 'Failed to load user performance data';
      toast.error(errorMsg);
      // Set empty performance data
      setUserPerformance({
        trends: [{ date: 'No Data', averageScore: 0, completionRate: 0 }]
      });
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header with gradient */}
        <div className="mb-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-8 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">Analytics Dashboard</h1>
              <p className="text-blue-100">Comprehensive insights into platform performance</p>
            </div>
            <Activity className="w-16 h-16 opacity-20" />
          </div>
        </div>

        {/* Tab Navigation with enhanced styling */}
        <div className="mb-6 bg-white rounded-lg shadow-sm p-2">
          <nav className="flex space-x-2">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'users', label: 'Users', icon: Users },
              { id: 'courses', label: 'Courses', icon: BookOpen },
              { id: 'performance', label: 'Performance', icon: TrendingUp }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-4 py-3 rounded-lg font-medium text-sm transition-all ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && analytics && (
          <div className="space-y-6">
            {/* Key Metrics with gradient cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-xl shadow-lg text-white transform hover:scale-105 transition-transform">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-100 mb-1">Total Users</p>
                    <p className="text-3xl font-bold">{analytics.totalUsers || 0}</p>
                    <p className="text-xs text-blue-100 mt-2">↑ Active platform users</p>
                  </div>
                  <Users className="w-12 h-12 opacity-30" />
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-green-500 to-green-600 p-6 rounded-xl shadow-lg text-white transform hover:scale-105 transition-transform">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-green-100 mb-1">Total Courses</p>
                    <p className="text-3xl font-bold">{analytics.totalCourses || 0}</p>
                    <p className="text-xs text-green-100 mt-2">↑ Available courses</p>
                  </div>
                  <BookOpen className="w-12 h-12 opacity-30" />
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-yellow-500 to-orange-500 p-6 rounded-xl shadow-lg text-white transform hover:scale-105 transition-transform">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-yellow-100 mb-1">Certificates</p>
                    <p className="text-3xl font-bold">{analytics.totalCertificates || 0}</p>
                    <p className="text-xs text-yellow-100 mt-2">↑ Issued certificates</p>
                  </div>
                  <Award className="w-12 h-12 opacity-30" />
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 p-6 rounded-xl shadow-lg text-white transform hover:scale-105 transition-transform">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-purple-100 mb-1">Video Calls</p>
                    <p className="text-3xl font-bold">{analytics.totalVideoCalls || 0}</p>
                    <p className="text-xs text-purple-100 mt-2">↑ Mentor sessions</p>
                  </div>
                  <Video className="w-12 h-12 opacity-30" />
                </div>
              </div>
            </div>

            {/* Charts with enhanced styling */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* User Registration Trend */}
              <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">User Registration Trend</h3>
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={analytics.userRegistrationTrend || []}>
                    <defs>
                      <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                    <XAxis dataKey="date" stroke="#6B7280" />
                    <YAxis stroke="#6B7280" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#fff', border: '1px solid #E5E7EB', borderRadius: '8px' }}
                    />
                    <Area type="monotone" dataKey="users" stroke="#3B82F6" fillOpacity={1} fill="url(#colorUsers)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Course Completion Rate */}
              <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Course Completion Rate</h3>
                  <Target className="w-5 h-5 text-green-600" />
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analytics.courseCompletionRate || []}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {(analytics.courseCompletionRate || []).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={['#10B981', '#3B82F6'][index % 2]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#fff', border: '1px solid #E5E7EB', borderRadius: '8px' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && analytics && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">User Activity</h3>
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={analytics.userActivity || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="date" stroke="#6B7280" />
                  <YAxis stroke="#6B7280" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #E5E7EB', borderRadius: '8px' }}
                  />
                  <Legend />
                  <Bar dataKey="activeUsers" fill="#3B82F6" name="Active Users" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="newUsers" fill="#10B981" name="New Users" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Courses Tab */}
        {activeTab === 'courses' && analytics && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">Course Performance</h3>
                <BookOpen className="w-6 h-6 text-green-600" />
              </div>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={analytics.coursePerformance || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="courseName" stroke="#6B7280" angle={-45} textAnchor="end" height={100} />
                  <YAxis stroke="#6B7280" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #E5E7EB', borderRadius: '8px' }}
                  />
                  <Legend />
                  <Bar dataKey="enrollments" fill="#3B82F6" name="Enrollments" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="completions" fill="#10B981" name="Completions" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Performance Tab */}
        {activeTab === 'performance' && userPerformance && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">User Performance Trends</h3>
                <TrendingUp className="w-6 h-6 text-purple-600" />
              </div>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={userPerformance.trends || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="date" stroke="#6B7280" />
                  <YAxis stroke="#6B7280" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #E5E7EB', borderRadius: '8px' }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="averageScore" stroke="#3B82F6" strokeWidth={3} name="Average Score" dot={{ fill: '#3B82F6', r: 5 }} />
                  <Line type="monotone" dataKey="completionRate" stroke="#10B981" strokeWidth={3} name="Completion Rate" dot={{ fill: '#10B981', r: 5 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminAnalytics;
     