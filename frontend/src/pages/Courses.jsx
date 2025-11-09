import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';

import { 
  BookOpen, 
  Clock, 
  Users, 
  Star, 
  TrendingUp,
  Filter,
  Search,
  Sparkles,
  ExternalLink,
  Zap,
  CheckCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

const Courses = () => {
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [enrolledCourses, setEnrolledCourses] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showRecommendations, setShowRecommendations] = useState(true);
  const [activeTab, setActiveTab] = useState('internal'); // 'internal' or 'external'

  useEffect(() => {
    fetchCourses();
    fetchEnrolledCourses();
    fetchRecommendations();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await api.get('/courses');
      if (response.data.success) {
        setCourses(response.data.courses || []);
      }
    } catch (error) {
      console.error('Failed to fetch courses:', error);
      toast.error('Failed to load courses');
    }
  };

  const fetchEnrolledCourses = async () => {
    try {
      const response = await api.get('/courses/my-courses');
      if (response.data.success) {
        const enrolledIds = response.data.my_courses.map(enrollment => enrollment.course.id);
        setEnrolledCourses(enrolledIds);
      }
    } catch (error) {
      console.error('Failed to fetch enrolled courses:', error);
      // Don't show error toast as this is not critical
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await api.get('/courses/ai-recommendations');
      if (response.data.success) {
        setRecommendations(response.data.recommendations?.courses || []);
      }
    } catch (error) {
      console.error('Failed to fetch AI recommendations:', error);
      // Don't show error for recommendations as it's not critical
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async (courseId, courseTitle) => {
    // Check if already enrolled to prevent unnecessary API call
    if (enrolledCourses.includes(courseId)) {
      toast.error(`You are already enrolled in ${courseTitle}`);
      return;
    }

    try {
      const response = await api.post('/courses/enroll', { course_id: courseId });
      if (response.data.success) {
        toast.success(`Successfully enrolled in ${courseTitle}!`);
        // Update enrolled courses list
        setEnrolledCourses(prev => [...prev, courseId]);
      }
    } catch (error) {
      if (error.response?.status === 409) {
        toast.error(`You are already enrolled in ${courseTitle}`);
        // Update local state to reflect enrollment
        setEnrolledCourses(prev => [...prev, courseId]);
      } else {
        toast.error(error.response?.data?.message || 'Failed to enroll in course');
      }
    }
  };

  const isEnrolled = (courseId) => {
    return enrolledCourses.includes(courseId);
  };

  const filteredCourses = courses.filter(course => {
    const matchesSearch = course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         course.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || course.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = ['all', ...new Set(courses.map(course => course.category).filter(Boolean))];

  if (loading) {
    return <LoadingSpinner text="Loading courses..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Courses
          </h1>
          <p className="text-gray-600">
            Discover courses tailored to your learning journey
          </p>
          
          {/* Tab Navigation */}
          <div className="mt-6 border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('internal')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'internal'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <BookOpen className="w-4 h-4" />
                  <span>SkillNova Courses</span>
                </div>
              </button>
              
              <button
                onClick={() => setActiveTab('external')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'external'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Zap className="w-4 h-4" />
                  <span>AI Recommended Courses</span>
                  <ExternalLink className="w-3 h-3" />
                </div>
              </button>
            </nav>
          </div>
        </div>

        {/* Content based on active tab */}
        {activeTab === 'external' ? (
          <div className="mt-8">
            <div className="text-center py-12">
              <Zap className="w-16 h-16 text-purple-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">AI Course Recommendations</h3>
              <p className="text-gray-600 mb-6">
                Complete an assessment to get personalized course recommendations from top platforms like Udemy, Coursera, and more.
              </p>
              <button
                onClick={() => navigate('/assessment')}
                className="btn-primary flex items-center space-x-2 mx-auto"
              >
                <Sparkles className="w-4 h-4" />
                <span>Take Assessment for Recommendations</span>
              </button>
            </div>
          </div>
        ) : (
          <>
            {/* AI Recommendations Section */}
            {recommendations.length > 0 && showRecommendations && (
          <div className="mb-8">
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 border border-purple-200">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-6 h-6 text-purple-600" />
                  <h2 className="text-xl font-semibold text-gray-900">
                    AI Recommended for You
                  </h2>
                </div>
                <button
                  onClick={() => setShowRecommendations(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {recommendations.slice(0, 6).map((course, index) => (
                  <div key={index} className="bg-white rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-purple-600">
                        {course.category}
                      </span>
                      <div className="flex items-center space-x-1">
                        <Star className="w-4 h-4 text-yellow-400 fill-current" />
                        <span className="text-sm text-gray-600">{course.rating}</span>
                      </div>
                    </div>
                    
                    <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                      {course.title}
                    </h3>
                    
                    <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>{course.duration_weeks} weeks</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Users className="w-4 h-4" />
                        <span>{course.students}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-1">
                        <TrendingUp className="w-4 h-4 text-green-500" />
                        <span className="text-sm font-medium text-green-600">
                          {course.match_score}% match
                        </span>
                      </div>
                      <button
                        onClick={() => handleEnroll(course.id, course.title)}
                        className="px-3 py-1 bg-purple-600 text-white text-sm rounded-md hover:bg-purple-700 transition-colors"
                      >
                        Enroll
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Search and Filter */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search courses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category === 'all' ? 'All Categories' : category}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Courses Grid */}
        {filteredCourses.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCourses.map((course) => (
              <div key={course.id} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <span className="px-2 py-1 bg-primary-100 text-primary-700 text-xs font-medium rounded-full">
                      {course.skill_level}
                    </span>
                    <div className="flex items-center space-x-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span className="text-sm text-gray-600">4.8</span>
                    </div>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                    {course.title}
                  </h3>
                  
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                    {course.description || 'Learn essential skills and advance your career with this comprehensive course.'}
                  </p>
                  
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>{course.duration_weeks || 8} weeks</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <BookOpen className="w-4 h-4" />
                      <span>{course.modules?.length || 12} modules</span>
                    </div>
                  </div>
                  
                  {isEnrolled(course.id) ? (
                    <div className="w-full">
                      <div className="flex items-center justify-center space-x-2 text-green-600 mb-2">
                        <CheckCircle className="w-4 h-4" />
                        <span className="text-sm font-medium">Enrolled</span>
                      </div>
                      <button
                        onClick={() => navigate(`/courses/${course.id}`)}
                        className="w-full btn-secondary"
                      >
                        Continue Learning
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleEnroll(course.id, course.title)}
                      className="w-full btn-primary"
                    >
                      Enroll Now
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No courses found</h3>
            <p className="text-gray-600">
              {searchTerm || selectedCategory !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : 'Courses will be available soon'
              }
            </p>
          </div>
        )}
          </>
        )}
      </div>
    </div>
  );
};

export default Courses;