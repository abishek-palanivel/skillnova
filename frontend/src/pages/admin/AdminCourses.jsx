import { useState, useEffect } from 'react';
import api from '../../utils/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import { 
  BookOpen, 
  Plus, 
  Edit, 
  Trash2, 
  Users, 
  Clock,
  Search,
  Filter,
  Sparkles,
  TrendingUp,
  Eye,
  FileText,
  Target,
  CheckCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

const AdminCourses = () => {
  const [courses, setCourses] = useState([]);
  const [courseRecommendations, setCourseRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterLevel, setFilterLevel] = useState('all');
  const [newCourse, setNewCourse] = useState({
    title: '',
    description: '',
    skill_level: 'Beginner',
    duration_weeks: 8,
    modules_count: 8,
    generate_questions: false
  });
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [courseToDelete, setCourseToDelete] = useState(null);
  const [showEnrollmentsModal, setShowEnrollmentsModal] = useState(false);
  const [selectedCourseEnrollments, setSelectedCourseEnrollments] = useState([]);
  const [showEditModal, setShowEditModal] = useState(false);
  const [courseToEdit, setCourseToEdit] = useState(null);
  const [editCourse, setEditCourse] = useState({
    title: '',
    description: '',
    skill_level: 'Beginner',
    duration_weeks: 8,
    is_active: true
  });
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [courseToPreview, setCourseToPreview] = useState(null);
  const [courseModules, setCourseModules] = useState([]);
  const [courseQuestions, setCourseQuestions] = useState([]);
  const [previewLoading, setPreviewLoading] = useState(false);

  useEffect(() => {
    fetchCourses();
    fetchCourseRecommendations();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await api.get('/admin/courses');
      if (response.data.success) {
        setCourses(response.data.courses || []);
      }
    } catch (error) {
      console.error('Failed to fetch courses:', error);
      toast.error('Failed to load courses');
    }
  };

  const fetchCourseRecommendations = async () => {
    try {
      const response = await api.get('/admin/ai-analytics/course-recommendations');
      if (response.data.success) {
        setCourseRecommendations(response.data.course_recommendations || []);
      }
    } catch (error) {
      console.error('Failed to fetch course recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCourse = async (e) => {
    e.preventDefault();
    try {
      const loadingToast = toast.loading('🤖 AI is generating your complete course with modules, tests, and learning path...');
      
      const response = await api.post('/admin/courses', newCourse);
      
      toast.dismiss(loadingToast);
      
      if (response.data.success) {
        const aiContent = response.data.ai_generated_content;
        
        const successMessage = `🎉 Course created successfully!\n✅ ${aiContent.modules} AI-generated modules\n✅ ${aiContent.assessments} assessments\n✅ Complete learning path` + 
          (aiContent.questions > 0 ? `\n✅ ${aiContent.questions} practice questions` : '\n📝 Questions can be added later in the Questions section');
        
        toast.success(successMessage, { duration: 6000 });
        
        setShowCreateModal(false);
        setNewCourse({
          title: '',
          description: '',
          skill_level: 'Beginner',
          duration_weeks: 8,
          modules_count: 8,
          generate_questions: false
        });
        fetchCourses();
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to create course');
    }
  };

  const handleDeleteCourse = async () => {
    if (!courseToDelete) return;
    
    try {
      const response = await api.delete(`/admin/courses/${courseToDelete.id}`);
      
      if (response.data.success) {
        toast.success(`Course "${courseToDelete.title}" deleted successfully`);
        setShowDeleteModal(false);
        setCourseToDelete(null);
        fetchCourses();
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to delete course');
    }
  };

  const handleViewEnrollments = async (course) => {
    try {
      const response = await api.get(`/admin/courses/${course.id}/enrollments`);
      
      if (response.data.success) {
        setSelectedCourseEnrollments({
          course: response.data.course,
          enrollments: response.data.enrollments
        });
        setShowEnrollmentsModal(true);
      }
    } catch (error) {
      toast.error('Failed to load course enrollments');
    }
  };

  const handleExitStudent = async (enrollmentId, studentName) => {
    try {
      const response = await api.post(`/admin/enrollments/${enrollmentId}/exit`);
      
      if (response.data.success) {
        toast.success(`Student "${studentName}" has been exited from the course`);
        // Refresh enrollments
        if (selectedCourseEnrollments.course) {
          handleViewEnrollments(selectedCourseEnrollments.course);
        }
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to exit student');
    }
  };

  const handleEditCourse = (course) => {
    setCourseToEdit(course);
    setEditCourse({
      title: course.title,
      description: course.description || '',
      skill_level: course.skill_level,
      duration_weeks: course.duration_weeks,
      is_active: course.is_active !== false
    });
    setShowEditModal(true);
  };

  const handleUpdateCourse = async (e) => {
    e.preventDefault();
    if (!courseToEdit) return;
    
    try {
      const response = await api.put(`/admin/courses/${courseToEdit.id}`, editCourse);
      
      if (response.data.success) {
        toast.success(`Course "${editCourse.title}" updated successfully`);
        setShowEditModal(false);
        setCourseToEdit(null);
        fetchCourses();
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to update course');
    }
  };

  const handlePreviewCourse = async (course) => {
    setCourseToPreview(course);
    setPreviewLoading(true);
    setShowPreviewModal(true);
    
    try {
      // Fetch course modules
      const modulesResponse = await api.get(`/admin/courses/${course.id}/modules`);
      if (modulesResponse.data.success) {
        setCourseModules(modulesResponse.data.modules || []);
      }
      
      // Fetch course questions (if any)
      try {
        const questionsResponse = await api.get(`/admin/questions?course_id=${course.id}`);
        if (questionsResponse.data.success) {
          setCourseQuestions(questionsResponse.data.questions || []);
        }
      } catch (error) {
        // Questions might not be available, that's okay
        console.log('No questions found for course:', error);
        setCourseQuestions([]);
      }
      
    } catch (error) {
      toast.error('Failed to load course preview');
      console.error('Preview error:', error);
    } finally {
      setPreviewLoading(false);
    }
  };

  const filteredCourses = courses.filter(course => {
    const matchesSearch = course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         course.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLevel = filterLevel === 'all' || course.skill_level === filterLevel;
    return matchesSearch && matchesLevel;
  });

  if (loading) {
    return <LoadingSpinner text="Loading courses..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Course Management</h1>
            <p className="text-gray-600">Create and manage courses for your platform</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Create Course</span>
          </button>
        </div>

        {/* AI Course Recommendations */}
        {courseRecommendations.length > 0 && (
          <div className="mb-8">
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 border border-purple-200">
              <div className="flex items-center space-x-2 mb-4">
                <Sparkles className="w-6 h-6 text-purple-600" />
                <h2 className="text-xl font-semibold text-gray-900">AI Course Recommendations</h2>
              </div>
              <p className="text-gray-600 mb-4">
                Based on user demand analysis, here are the top course recommendations:
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {courseRecommendations.slice(0, 6).map((rec, index) => (
                  <div key={index} className="bg-white rounded-lg p-4 border border-gray-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        rec.priority === 'High' ? 'bg-red-100 text-red-700' :
                        rec.priority === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {rec.priority} Priority
                      </span>
                      <div className="flex items-center space-x-1">
                        <TrendingUp className="w-4 h-4 text-green-500" />
                        <span className="text-sm font-medium text-gray-900">{rec.demand_score} users</span>
                      </div>
                    </div>
                    
                    <h3 className="font-semibold text-gray-900 mb-2">{rec.suggested_title}</h3>
                    <p className="text-sm text-gray-600 mb-2">{rec.target_audience}</p>
                    
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span>{rec.skill_level}</span>
                      <span>{rec.estimated_duration}</span>
                    </div>
                    
                    <button
                      onClick={() => {
                        setNewCourse({
                          title: rec.suggested_title,
                          description: `${rec.target_audience}. Duration: ${rec.estimated_duration}`,
                          skill_level: rec.skill_level,  // Keep original capitalization
                          duration_weeks: parseInt(rec.estimated_duration.split('-')[0]) || 8,
                          modules_count: 8,
                          generate_questions: false
                        });
                        setShowCreateModal(true);
                      }}
                      className="w-full mt-3 px-3 py-2 bg-purple-600 text-white text-sm rounded-md hover:bg-purple-700 transition-colors"
                    >
                      Create This Course
                    </button>
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
              value={filterLevel}
              onChange={(e) => setFilterLevel(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Levels</option>
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
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
                    <div className="flex items-center space-x-2">
                      <button 
                        onClick={() => handlePreviewCourse(course)}
                        className="p-1 text-gray-400 hover:text-purple-600"
                        title="Preview Course Content"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleViewEnrollments(course)}
                        className="p-1 text-gray-400 hover:text-green-600"
                        title="View Enrollments"
                      >
                        <Users className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleEditCourse(course)}
                        className="p-1 text-gray-400 hover:text-blue-600"
                        title="Edit Course"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => {
                          setCourseToDelete(course);
                          setShowDeleteModal(true);
                        }}
                        className="p-1 text-gray-400 hover:text-red-600"
                        title="Delete Course"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{course.title}</h3>
                  
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                    {course.description || 'No description available'}
                  </p>
                  
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>{course.duration_weeks} weeks</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <BookOpen className="w-4 h-4" />
                      <span>{course.modules_count || 0} modules</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-1">
                      <Users className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-600">{course.enrollment_count || 0} enrolled</span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(course.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No courses found</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || filterLevel !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : 'Get started by creating your first course'
              }
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn-primary"
            >
              Create Course
            </button>
          </div>
        )}

        {/* Create Course Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Create New Course</h2>
              
              <form onSubmit={handleCreateCourse} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Course Title
                  </label>
                  <input
                    type="text"
                    required
                    value={newCourse.title}
                    onChange={(e) => setNewCourse({...newCourse, title: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="Enter course title"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={newCourse.description}
                    onChange={(e) => setNewCourse({...newCourse, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    rows="3"
                    placeholder="Enter course description"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Skill Level
                  </label>
                  <select
                    value={newCourse.skill_level}
                    onChange={(e) => setNewCourse({...newCourse, skill_level: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Advanced">Advanced</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Duration (weeks)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="52"
                    value={newCourse.duration_weeks}
                    onChange={(e) => setNewCourse({...newCourse, duration_weeks: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Number of Modules
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    value={newCourse.modules_count}
                    onChange={(e) => setNewCourse({...newCourse, modules_count: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">AI will generate modules automatically</p>
                </div>
                
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="generate_questions"
                    checked={newCourse.generate_questions}
                    onChange={(e) => setNewCourse({...newCourse, generate_questions: e.target.checked})}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <label htmlFor="generate_questions" className="text-sm font-medium text-gray-700">
                    Generate AI Questions & Tests
                  </label>
                </div>
                
                <div className="flex space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 btn-primary"
                  >
                    Create Course
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Delete Course Modal */}
        {showDeleteModal && courseToDelete && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                  <Trash2 className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Delete Course</h2>
                  <p className="text-gray-600">This action cannot be undone</p>
                </div>
              </div>
              
              <div className="mb-6">
                <p className="text-gray-700 mb-2">
                  Are you sure you want to delete the course:
                </p>
                <p className="font-semibold text-gray-900 bg-gray-50 p-3 rounded">
                  "{courseToDelete.title}"
                </p>
                <p className="text-sm text-red-600 mt-2">
                  This will permanently delete the course, all modules, questions, and enrollment data.
                </p>
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setCourseToDelete(null);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteCourse}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Delete Course
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Edit Course Modal */}
        {showEditModal && courseToEdit && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Edit Course</h2>
              
              <form onSubmit={handleUpdateCourse} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Course Title
                  </label>
                  <input
                    type="text"
                    required
                    value={editCourse.title}
                    onChange={(e) => setEditCourse({...editCourse, title: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="Enter course title"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={editCourse.description}
                    onChange={(e) => setEditCourse({...editCourse, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    rows="3"
                    placeholder="Enter course description"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Skill Level
                  </label>
                  <select
                    value={editCourse.skill_level}
                    onChange={(e) => setEditCourse({...editCourse, skill_level: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Advanced">Advanced</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Duration (weeks)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="52"
                    value={editCourse.duration_weeks}
                    onChange={(e) => setEditCourse({...editCourse, duration_weeks: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={editCourse.is_active}
                    onChange={(e) => setEditCourse({...editCourse, is_active: e.target.checked})}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
                    Course is Active
                  </label>
                </div>
                
                <div className="flex space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowEditModal(false);
                      setCourseToEdit(null);
                    }}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 btn-primary"
                  >
                    Update Course
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Course Enrollments Modal */}
        {showEnrollmentsModal && selectedCourseEnrollments && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">Course Enrollments</h2>
                    <p className="text-gray-600">{selectedCourseEnrollments.course?.title}</p>
                  </div>
                  <button
                    onClick={() => setShowEnrollmentsModal(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>
              </div>
              
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                {selectedCourseEnrollments.enrollments?.length > 0 ? (
                  <div className="space-y-4">
                    {selectedCourseEnrollments.enrollments.map((enrollment) => (
                      <div key={enrollment.enrollment_id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3">
                              <div>
                                <h3 className="font-semibold text-gray-900">{enrollment.user.name}</h3>
                                <p className="text-sm text-gray-600">{enrollment.user.email}</p>
                              </div>
                              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                enrollment.status === 'completed' ? 'bg-green-100 text-green-700' :
                                enrollment.status === 'active' ? 'bg-blue-100 text-blue-700' :
                                'bg-red-100 text-red-700'
                              }`}>
                                {enrollment.status}
                              </span>
                            </div>
                            
                            <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
                              <span>Progress: {enrollment.progress_percentage}%</span>
                              <span>Enrolled: {new Date(enrollment.enrolled_at).toLocaleDateString()}</span>
                              {enrollment.completed_at && (
                                <span>Completed: {new Date(enrollment.completed_at).toLocaleDateString()}</span>
                              )}
                            </div>
                            
                            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full" 
                                style={{ width: `${enrollment.progress_percentage}%` }}
                              ></div>
                            </div>
                          </div>
                          
                          {enrollment.status === 'active' && (
                            <button
                              onClick={() => handleExitStudent(enrollment.enrollment_id, enrollment.user.name)}
                              className="ml-4 px-3 py-1 bg-red-100 text-red-700 text-sm rounded hover:bg-red-200"
                            >
                              Exit Student
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Enrollments</h3>
                    <p className="text-gray-600">No students are currently enrolled in this course.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Course Preview Modal */}
        {showPreviewModal && courseToPreview && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">Course Preview</h2>
                    <p className="text-gray-600">{courseToPreview.title}</p>
                  </div>
                  <button
                    onClick={() => {
                      setShowPreviewModal(false);
                      setCourseToPreview(null);
                      setCourseModules([]);
                      setCourseQuestions([]);
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>
              </div>
              
              <div className="p-6 overflow-y-auto max-h-[70vh]">
                {previewLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading course content...</p>
                  </div>
                ) : (
                  <div className="space-y-8">
                    {/* Course Information */}
                    <div className="bg-gray-50 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Course Information</h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-sm text-gray-600">Skill Level</p>
                          <p className="font-medium text-gray-900">{courseToPreview.skill_level}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Duration</p>
                          <p className="font-medium text-gray-900">{courseToPreview.duration_weeks} weeks</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Modules</p>
                          <p className="font-medium text-gray-900">{courseModules.length}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Questions</p>
                          <p className="font-medium text-gray-900">{courseQuestions.length}</p>
                        </div>
                      </div>
                      {courseToPreview.description && (
                        <div className="mt-4">
                          <p className="text-sm text-gray-600">Description</p>
                          <p className="text-gray-900">{courseToPreview.description}</p>
                        </div>
                      )}
                    </div>

                    {/* Course Modules */}
                    <div>
                      <div className="flex items-center space-x-2 mb-4">
                        <FileText className="w-5 h-5 text-blue-600" />
                        <h3 className="text-lg font-semibold text-gray-900">Course Modules ({courseModules.length})</h3>
                      </div>
                      
                      {courseModules.length > 0 ? (
                        <div className="space-y-4">
                          {courseModules.map((module, index) => (
                            <div key={module.id} className="border border-gray-200 rounded-lg p-4">
                              <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center space-x-3">
                                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                                    <span className="text-blue-600 font-semibold text-sm">{index + 1}</span>
                                  </div>
                                  <div>
                                    <h4 className="font-medium text-gray-900">{module.title}</h4>
                                    <p className="text-sm text-gray-600">Module {module.order_index}</p>
                                  </div>
                                </div>
                                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                  module.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                                }`}>
                                  {module.is_active ? 'Active' : 'Inactive'}
                                </span>
                              </div>
                              
                              {module.content && (
                                <div className="bg-gray-50 rounded p-3 mt-3">
                                  <p className="text-sm text-gray-700 line-clamp-3">
                                    {module.content.substring(0, 200)}
                                    {module.content.length > 200 && '...'}
                                  </p>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8 bg-gray-50 rounded-lg">
                          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                          <p className="text-gray-600">No modules found for this course</p>
                          <p className="text-sm text-gray-500 mt-1">Modules will be generated when the course is created with AI</p>
                        </div>
                      )}
                    </div>

                    {/* Course Questions/Tests */}
                    <div>
                      <div className="flex items-center space-x-2 mb-4">
                        <Target className="w-5 h-5 text-green-600" />
                        <h3 className="text-lg font-semibold text-gray-900">Course Questions & Tests ({courseQuestions.length})</h3>
                      </div>
                      
                      {courseQuestions.length > 0 ? (
                        <div className="space-y-4">
                          {courseQuestions.slice(0, 5).map((question, index) => (
                            <div key={question.id} className="border border-gray-200 rounded-lg p-4">
                              <div className="flex items-start justify-between mb-3">
                                <div className="flex-1">
                                  <div className="flex items-center space-x-2 mb-2">
                                    <span className="text-sm font-medium text-gray-900">Q{index + 1}:</span>
                                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                      question.difficulty_level === 'easy' ? 'bg-green-100 text-green-700' :
                                      question.difficulty_level === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                      'bg-red-100 text-red-700'
                                    }`}>
                                      {question.difficulty_level}
                                    </span>
                                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">
                                      {question.question_type}
                                    </span>
                                  </div>
                                  <p className="text-gray-900 mb-2">{question.question_text}</p>
                                  
                                  {question.question_type === 'multiple_choice' && question.options && (
                                    <div className="mt-2">
                                      <p className="text-xs text-gray-600 mb-1">Options:</p>
                                      <div className="grid grid-cols-2 gap-2">
                                        {(Array.isArray(question.options) ? question.options : Object.values(question.options || {})).map((option, optIndex) => (
                                          <div key={optIndex} className="text-sm text-gray-700 bg-gray-50 px-2 py-1 rounded">
                                            {String.fromCharCode(65 + optIndex)}. {option}
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                                <div className="ml-4">
                                  <CheckCircle className="w-5 h-5 text-green-600" />
                                </div>
                              </div>
                              
                              <div className="text-xs text-gray-500 mt-2">
                                <strong>Correct Answer:</strong> {question.correct_answer}
                              </div>
                            </div>
                          ))}
                          
                          {courseQuestions.length > 5 && (
                            <div className="text-center py-4 bg-gray-50 rounded-lg">
                              <p className="text-sm text-gray-600">
                                And {courseQuestions.length - 5} more questions...
                              </p>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="text-center py-8 bg-gray-50 rounded-lg">
                          <Target className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                          <p className="text-gray-600">No questions found for this course</p>
                          <p className="text-sm text-gray-500 mt-1">Questions will be generated when the course is created with AI</p>
                        </div>
                      )}
                    </div>

                    {/* Course Statistics */}
                    <div className="bg-blue-50 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Course Statistics</h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">{courseToPreview.enrollment_count || 0}</div>
                          <div className="text-sm text-gray-600">Total Enrollments</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">{courseModules.length}</div>
                          <div className="text-sm text-gray-600">Learning Modules</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-purple-600">{courseQuestions.length}</div>
                          <div className="text-sm text-gray-600">Practice Questions</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-orange-600">{courseToPreview.duration_weeks}</div>
                          <div className="text-sm text-gray-600">Weeks Duration</div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="p-6 border-t border-gray-200 bg-gray-50">
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => {
                      setShowPreviewModal(false);
                      setCourseToPreview(null);
                      setCourseModules([]);
                      setCourseQuestions([]);
                    }}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                  >
                    Close Preview
                  </button>
                  <button
                    onClick={() => {
                      setShowPreviewModal(false);
                      handleEditCourse(courseToPreview);
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Edit Course
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminCourses;