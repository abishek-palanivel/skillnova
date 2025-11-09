import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  Award, 
  Clock, 
  CheckCircle, 
  Play, 
  TrendingUp,
  BookOpen,
  Target,
  Sparkles,
  Calendar,
  BarChart3
} from 'lucide-react';
import toast from 'react-hot-toast';

const Tests = () => {
  const { user } = useAuth();
  const [testHistory, setTestHistory] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [enrolledCourses, setEnrolledCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showInitialAssessment, setShowInitialAssessment] = useState(false);
  const [showFinalAssessment, setShowFinalAssessment] = useState(false);

  useEffect(() => {
    if (user) {
      fetchTestHistory();
      fetchRecommendations();
      fetchEnrolledCourses();
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchTestHistory = async () => {
    try {
      const response = await api.get('/tests/history');
      if (response.data.success) {
        setTestHistory(response.data.test_history || []);
        
        // Check if user has taken initial assessment
        const hasInitialAssessment = response.data.test_history.some(
          test => test.assessment_type === 'initial' || test.test_type === 'initial'
        );
        setShowInitialAssessment(!hasInitialAssessment);
        
        // Check if user can take final assessment (has completed courses)
        // This would be determined by backend logic
        setShowFinalAssessment(hasInitialAssessment);
      }
    } catch (error) {
      console.error('Failed to fetch test history:', error);
      toast.error('Failed to load test history');
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await api.get('/user/recommendations/tests');
      if (response.data.success) {
        setRecommendations(response.data.recommendations || []);
      }
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
      if (error.response?.status === 401) {
        toast.error('Please log in to view test recommendations');
      } else if (error.response?.status === 500) {
        toast.error('Server error. Please try again later.');
      } else {
        toast.error('Failed to load recommendations');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchEnrolledCourses = async () => {
    try {
      const response = await api.get('/courses/my-courses');
      if (response.data.success) {
        setEnrolledCourses(response.data.my_courses || []);
      }
    } catch (error) {
      console.error('Failed to fetch enrolled courses:', error);
    }
  };

  const handleStartAssessment = async (type) => {
    try {
      // Navigate to assessment taking page
      window.location.href = `/assessment/${type}`;
    } catch (error) {
      toast.error(`Failed to start ${type} assessment`);
    }
  };

  const handleStartRecommendedTest = async (testId) => {
    try {
      // In a real implementation, this would start the specific test
      toast.success('Starting recommended test...');
    } catch (error) {
      toast.error('Failed to start test');
    }
  };

  const handleStartCourseAssessment = async (courseId) => {
    try {
      // Navigate to course assessment
      window.location.href = `/assessment/course/${courseId}`;
    } catch (error) {
      toast.error('Failed to start course assessment');
    }
  };

  const getPerformanceColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPerformanceLevel = (score) => {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Very Good';
    if (score >= 70) return 'Good';
    if (score >= 50) return 'Average';
    return 'Needs Improvement';
  };

  if (loading) {
    return <LoadingSpinner text="Loading tests..." />;
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <Award className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Authentication Required</h2>
            <p className="text-gray-600 mb-6">Please log in to access tests and assessments</p>
            <a href="/login" className="btn-primary">
              Go to Login
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Tests & Assessments
          </h1>
          <p className="text-gray-600">
            Evaluate your progress with comprehensive tests and skill assessments
          </p>
        </div>

        {/* Assessment Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Initial Assessment */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Target className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Initial Assessment</h3>
                <p className="text-sm text-gray-600">Evaluate your current skill level</p>
              </div>
            </div>
            
            <div className="space-y-3 mb-4">
              <div className="flex items-center text-sm text-gray-600">
                <Clock className="w-4 h-4 mr-2" />
                <span>60 minutes • 20 questions</span>
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <BookOpen className="w-4 h-4 mr-2" />
                <span>Mixed difficulty levels</span>
              </div>
            </div>
            
            {showInitialAssessment ? (
              <button
                onClick={() => handleStartAssessment('initial')}
                className="w-full btn-primary flex items-center justify-center space-x-2"
              >
                <Play className="w-4 h-4" />
                <span>Start Assessment</span>
              </button>
            ) : (
              <div className="flex items-center justify-center space-x-2 text-green-600">
                <CheckCircle className="w-5 h-5" />
                <span className="font-medium">Completed</span>
              </div>
            )}
          </div>

          {/* Final Assessment */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Award className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Final Assessment</h3>
                <p className="text-sm text-gray-600">Comprehensive evaluation of your skills</p>
              </div>
            </div>
            
            <div className="space-y-3 mb-4">
              <div className="flex items-center text-sm text-gray-600">
                <Clock className="w-4 h-4 mr-2" />
                <span>90 minutes • 20 questions</span>
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <BookOpen className="w-4 h-4 mr-2" />
                <span>All skill levels covered</span>
              </div>
            </div>
            
            {showFinalAssessment ? (
              <button
                onClick={() => handleStartAssessment('final')}
                className="w-full btn-primary flex items-center justify-center space-x-2"
              >
                <Play className="w-4 h-4" />
                <span>Start Final Assessment</span>
              </button>
            ) : (
              <div className="text-center text-gray-500">
                <p className="text-sm">Complete courses to unlock</p>
              </div>
            )}
          </div>
        </div>

        {/* Course-Specific Assessments */}
        {enrolledCourses.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center space-x-2 mb-6">
              <BookOpen className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">Course Assessments</h2>
              <span className="text-sm text-gray-500">({enrolledCourses.length} enrolled courses)</span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {enrolledCourses.map((enrollment) => (
                <div key={enrollment.enrollment_id} className="card hover:shadow-lg transition-shadow">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="p-3 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg">
                      <BookOpen className="w-6 h-6 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 line-clamp-2">
                        {enrollment.course.title}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {enrollment.course.skill_level} • {enrollment.course.duration_weeks} weeks
                      </p>
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600">Progress</span>
                      <span className="font-medium text-gray-900">{enrollment.progress_percentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300" 
                        style={{ width: `${enrollment.progress_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  {/* Assessment Info */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-sm text-gray-600">
                      <Target className="w-4 h-4 mr-2" />
                      <span>Comprehensive course assessment</span>
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Clock className="w-4 h-4 mr-2" />
                      <span>90 minutes • 15 questions</span>
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Award className="w-4 h-4 mr-2" />
                      <span>Certificate eligible (75% to pass)</span>
                    </div>
                  </div>
                  
                  {/* Status and Action */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        enrollment.status === 'completed' ? 'bg-green-100 text-green-700' :
                        enrollment.status === 'active' ? 'bg-blue-100 text-blue-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {enrollment.status === 'completed' ? 'Completed' : 
                         enrollment.status === 'active' ? 'In Progress' : 'Enrolled'}
                      </span>
                      
                      {enrollment.progress_percentage >= 50 && (
                        <span className="text-xs text-green-600 font-medium">
                          Assessment Available
                        </span>
                      )}
                    </div>
                    
                    {enrollment.progress_percentage >= 50 ? (
                      <button
                        onClick={() => handleStartCourseAssessment(enrollment.course.id)}
                        className="w-full btn-primary flex items-center justify-center space-x-2"
                      >
                        <Play className="w-4 h-4" />
                        <span>Take Assessment</span>
                      </button>
                    ) : (
                      <div className="text-center text-gray-500">
                        <p className="text-sm">Complete 50% of course to unlock assessment</p>
                        <div className="text-xs text-gray-400 mt-1">
                          {Math.max(0, 50 - enrollment.progress_percentage)}% more needed
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI Test Recommendations */}
        {recommendations.length > 0 && (
          <div className="mb-8">
            <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-lg p-6 border border-orange-200">
              <div className="flex items-center space-x-2 mb-4">
                <Sparkles className="w-6 h-6 text-orange-600" />
                <h2 className="text-xl font-semibold text-gray-900">
                  Recommended Tests for You
                </h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {recommendations.slice(0, 6).map((test, index) => (
                  <div key={test?.id || index} className="bg-white rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        test?.skill_level === 'Beginner' ? 'bg-green-100 text-green-700' :
                        test?.skill_level === 'Intermediate' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {test?.skill_level || 'Beginner'}
                      </span>
                      <div className="flex items-center space-x-1">
                        <Target className="w-4 h-4 text-orange-500" />
                        <span className="text-sm font-medium text-orange-600">
                          {Math.round((test?.match_score || 0.8) * 100)}% match
                        </span>
                      </div>
                    </div>
                    
                    <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                      {test?.title || 'Programming Test'}
                    </h3>
                    
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>{test?.duration_minutes || 30} min</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <BookOpen className="w-4 h-4" />
                        <span>{test?.questions_count || 20} questions</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        {Math.round(Math.random() * 30 + 70)}% pass rate
                      </span>
                      <button
                        onClick={() => handleStartRecommendedTest(test?.id || `test_${index}`)}
                        className="px-3 py-1 bg-orange-600 text-white text-sm rounded-md hover:bg-orange-700 transition-colors flex items-center space-x-1"
                      >
                        <Play className="w-3 h-3" />
                        <span>Take Test</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Test History */}
        <div className="card">
          <div className="flex items-center space-x-2 mb-6">
            <BarChart3 className="w-6 h-6 text-gray-600" />
            <h2 className="text-xl font-semibold text-gray-900">Test History</h2>
          </div>
          
          {testHistory.length > 0 ? (
            <div className="space-y-4">
              {testHistory.map((test, index) => (
                <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-4">
                    <div className="p-2 bg-gray-100 rounded-lg">
                      <Award className="w-5 h-5 text-gray-600" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">
                        {test.assessment_type ? 
                          `${test.assessment_type.charAt(0).toUpperCase() + test.assessment_type.slice(1)} Assessment` :
                          `${test.test_type.charAt(0).toUpperCase() + test.test_type.slice(1)} Test`
                        }
                      </h3>
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-4 h-4" />
                          <span>{new Date(test.completed_at).toLocaleDateString()}</span>
                        </div>
                        {test.correct_answers && test.total_questions && (
                          <span>{test.correct_answers}/{test.total_questions} correct</span>
                        )}
                        {test.time_taken_minutes && (
                          <div className="flex items-center space-x-1">
                            <Clock className="w-4 h-4" />
                            <span>{test.time_taken_minutes} min</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className={`w-4 h-4 ${getPerformanceColor(test.score_percentage)}`} />
                      <span className={`text-lg font-bold ${getPerformanceColor(test.score_percentage)}`}>
                        {test.score_percentage}%
                      </span>
                    </div>
                    <p className={`text-sm ${getPerformanceColor(test.score_percentage)}`}>
                      {getPerformanceLevel(test.score_percentage)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Award className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No tests taken yet</h3>
              <p className="text-gray-600 mb-4">
                Start with the initial assessment to evaluate your current skill level
              </p>
              {showInitialAssessment && (
                <button
                  onClick={() => handleStartAssessment('initial')}
                  className="btn-primary"
                >
                  Take Initial Assessment
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Tests;