import { useState, useEffect } from 'react';
import api from '../../utils/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  BookOpen,
  Award,
  Calendar,
  Download,
  RefreshCw,
  Target,
  Clock,
  Star
} from 'lucide-react';
import toast from 'react-hot-toast';

const AdminReports = () => {
  const [loading, setLoading] = useState(true);
  const [performanceReport, setPerformanceReport] = useState(null);
  const [userInsights, setUserInsights] = useState(null);
  const [courseRecommendations, setCourseRecommendations] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchAllReports();
  }, []);

  const fetchAllReports = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchPerformanceReport(),
        fetchUserInsights(),
        fetchCourseRecommendations()
      ]);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPerformanceReport = async () => {
    try {
      const response = await api.get('/admin/reports/performance');
      if (response.data.success) {
        setPerformanceReport(response.data.report);
      }
    } catch (error) {
      console.error('Failed to fetch performance report:', error);
    }
  };

  const fetchUserInsights = async () => {
    try {
      const response = await api.get('/admin/ai-analytics/user-insights');
      if (response.data.success) {
        setUserInsights(response.data.insights);
      }
    } catch (error) {
      console.error('Failed to fetch user insights:', error);
    }
  };

  const fetchCourseRecommendations = async () => {
    try {
      const response = await api.get('/admin/ai-analytics/course-recommendations');
      if (response.data.success) {
        setCourseRecommendations(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch course recommendations:', error);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchAllReports();
    setRefreshing(false);
    toast.success('Reports refreshed successfully');
  };

  const exportReport = (reportType) => {
    // In a real implementation, this would generate and download a report
    toast.success(`${reportType} report export started`);
  };

  if (loading) {
    return <LoadingSpinner text="Loading reports..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
            <p className="text-gray-600 mt-2">Comprehensive insights and performance metrics</p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            <button
              onClick={() => exportReport('Full')}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              <Download className="w-4 h-4" />
              <span>Export Report</span>
            </button>
          </div>
        </div>

        {/* Performance Overview */}
        {performanceReport && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Performance Overview</h2>
            
            {/* Assessment Performance */}
            <div className="mb-8">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Assessment Performance</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {performanceReport.assessment_performance?.map((assessment, index) => (
                  <div key={index} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900">{assessment.type}</h4>
                      <Target className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Total Assessments:</span>
                        <span className="font-medium">{assessment.total_assessments}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Average Score:</span>
                        <span className="font-medium text-green-600">{assessment.average_score}%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Range:</span>
                        <span className="font-medium">{assessment.min_score}% - {assessment.max_score}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Course Popularity */}
            <div className="mb-8">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Course Popularity</h3>
              <div className="space-y-3">
                {performanceReport.course_popularity?.slice(0, 5).map((course, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <h4 className="font-medium text-gray-900">{course.course_title}</h4>
                      <p className="text-sm text-gray-600">{course.skill_level} Level</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-primary-600">{course.total_enrollments}</p>
                      <p className="text-xs text-gray-500">enrollments</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>


          </div>
        )}

        {/* User Insights */}
        {userInsights && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">AI User Insights</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Interest Distribution */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Interest Distribution</h3>
                <div className="space-y-3">
                  {userInsights.interest_distribution?.slice(0, 5).map((interest, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-gray-700">{interest.interest}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${interest.percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 w-12">
                          {interest.percentage}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Skill Level Distribution */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Skill Level Distribution</h3>
                <div className="space-y-3">
                  {userInsights.skill_level_distribution?.map((level, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-gray-700">{level.level}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-600 h-2 rounded-full" 
                            style={{ width: `${level.percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 w-12">
                          {level.percentage}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Key Insights */}
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Key Insights</h3>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <ul className="space-y-2">
                  {userInsights.key_insights?.map((insight, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <TrendingUp className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                      <span className="text-blue-800 text-sm">{insight}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Recommendations */}
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recommendations for Admin</h3>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <ul className="space-y-2">
                  {userInsights.recommendations_for_admin?.map((recommendation, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <Star className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                      <span className="text-green-800 text-sm">{recommendation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Course Recommendations */}
        {courseRecommendations && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">AI Course Recommendations</h2>
            
            {/* Demand Analysis */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Demand Analysis</h3>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <p className="text-purple-800 mb-2">
                  <strong>Total Users Analyzed:</strong> {courseRecommendations.demand_analysis?.total_users_analyzed}
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
                  {courseRecommendations.demand_analysis?.top_interests?.map((interest, index) => (
                    <div key={index} className="bg-white rounded-lg p-3 border border-purple-200">
                      <h4 className="font-medium text-gray-900">{interest.interest}</h4>
                      <p className="text-sm text-gray-600">{interest.user_count} users ({interest.percentage}%)</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Course Recommendations */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recommended Courses to Create</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {courseRecommendations.course_recommendations?.slice(0, 6).map((recommendation, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="font-medium text-gray-900 flex-1">{recommendation.suggested_title}</h4>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        recommendation.priority === 'High' ? 'bg-red-100 text-red-800' :
                        recommendation.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {recommendation.priority}
                      </span>
                    </div>
                    
                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex justify-between">
                        <span>Category:</span>
                        <span className="font-medium">{recommendation.category}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Skill Level:</span>
                        <span className="font-medium">{recommendation.skill_level}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Demand Score:</span>
                        <span className="font-bold text-primary-600">{recommendation.demand_score}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Duration:</span>
                        <span className="font-medium">{recommendation.estimated_duration}</span>
                      </div>
                    </div>
                    
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-xs text-gray-600">{recommendation.target_audience}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Export Options */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Export Options</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => exportReport('Performance')}
              className="flex items-center justify-center space-x-2 p-4 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <BarChart3 className="w-5 h-5 text-blue-600" />
              <span>Performance Report</span>
            </button>
            
            <button
              onClick={() => exportReport('User Insights')}
              className="flex items-center justify-center space-x-2 p-4 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Users className="w-5 h-5 text-green-600" />
              <span>User Insights</span>
            </button>
            
            <button
              onClick={() => exportReport('Course Recommendations')}
              className="flex items-center justify-center space-x-2 p-4 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <BookOpen className="w-5 h-5 text-purple-600" />
              <span>Course Recommendations</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminReports;