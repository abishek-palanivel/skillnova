import { useState, useEffect } from 'react';
import api from '../../utils/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import { 
  HelpCircle, 
  Plus, 
  Edit2, 
  Trash2, 
  Search,
  Filter,
  Eye,
  EyeOff,
  CheckCircle,
  XCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

const AdminQuestions = () => {
  const [loading, setLoading] = useState(true);
  const [questions, setQuestions] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterDifficulty, setFilterDifficulty] = useState('all');
  const [showAdvancedForm, setShowAdvancedForm] = useState(false);
  const [courses, setCourses] = useState([]);
  const [newQuestion, setNewQuestion] = useState({
    question_text: '',
    question_type: 'multiple_choice',
    difficulty_level: 'medium',
    category: '',
    course_id: '',
    correct_answer: '',
    options: ['', '', '', ''],
    is_active: true
  });

  useEffect(() => {
    fetchQuestions();
    fetchCourses();
  }, []);

  // Ensure options array is properly initialized when question type changes
  useEffect(() => {
    if (newQuestion.question_type === 'multiple_choice' && !Array.isArray(newQuestion.options)) {
      setNewQuestion(prev => ({
        ...prev,
        options: ['', '', '', '']
      }));
    }
  }, [newQuestion.question_type]);

  const fetchQuestions = async () => {
    try {
      const response = await api.get('/admin/questions');
      if (response.data.success) {
        setQuestions(response.data.questions || []);
      }
    } catch (error) {
      console.error('Failed to fetch questions:', error);
      toast.error('Failed to load questions');
    } finally {
      setLoading(false);
    }
  };

  const fetchCourses = async () => {
    try {
      const response = await api.get('/admin/ai-questions/categories');
      if (response.data.success) {
        setCourses(response.data.courses || []);
      }
    } catch (error) {
      console.error('Failed to fetch courses:', error);
    }
  };

  const handleGenerateAIQuestion = async () => {
    if (!newQuestion.question_type || !newQuestion.difficulty_level) {
      toast.error('Please select question type and difficulty first');
      return;
    }

    try {
      const loadingToast = toast.loading('🤖 AI is generating your question...');
      
      const response = await api.post('/admin/questions/generate-ai', {
        question_type: newQuestion.question_type,
        difficulty: newQuestion.difficulty_level,
        category: newQuestion.category || 'Programming',
        count: 1
      });

      toast.dismiss(loadingToast);

      if (response.data.success && response.data.questions.length > 0) {
        const generatedQuestion = response.data.questions[0];
        
        // Update the form with AI-generated content
        setNewQuestion(prev => ({
          ...prev,
          question_text: generatedQuestion.question_text,
          correct_answer: generatedQuestion.correct_answer,
          options: generatedQuestion.options || prev.options,
          category: generatedQuestion.category || prev.category
        }));
        
        setShowAdvancedForm(true);
        toast.success('🎉 AI question generated successfully!');
        
        // Refresh questions list to show the new question
        fetchQuestions();
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to generate AI question');
    }
  };

  const handleBulkGenerateAI = async () => {
    try {
      const count = parseInt(prompt('How many questions to generate? (1-20)', '5'));
      if (!count || count < 1 || count > 20) {
        toast.error('Please enter a number between 1 and 20');
        return;
      }

      const category = prompt('Category (e.g., Python, JavaScript, Web Development)', 'Programming');
      const difficulty = prompt('Difficulty (easy, medium, hard)', 'medium');

      if (!['easy', 'medium', 'hard'].includes(difficulty)) {
        toast.error('Invalid difficulty. Use: easy, medium, or hard');
        return;
      }

      const loadingToast = toast.loading(`🤖 AI is generating ${count} questions...`);
      
      const response = await api.post('/admin/questions/generate-ai', {
        question_type: 'multiple_choice',
        difficulty: difficulty,
        category: category || 'Programming',
        count: count
      });

      toast.dismiss(loadingToast);

      if (response.data.success) {
        toast.success(`🎉 Successfully generated ${response.data.questions_count} AI questions!`);
        fetchQuestions();
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to generate AI questions');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Clean up options for non-multiple choice questions
      const currentOptions = Array.isArray(newQuestion.options) ? newQuestion.options : [];
      const questionData = {
        ...newQuestion,
        options: newQuestion.question_type === 'multiple_choice' ? 
          currentOptions.filter(opt => opt.trim() !== '') : null
      };

      const url = editingQuestion ? `/admin/questions/${editingQuestion.id}` : '/admin/questions';
      const method = editingQuestion ? 'put' : 'post';
      
      const response = await api[method](url, questionData);
      if (response.data.success) {
        toast.success(editingQuestion ? 'Question updated successfully' : 'Question created successfully');
        setShowAddForm(false);
        setEditingQuestion(null);
        resetForm();
        fetchQuestions();
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to save question');
    }
  };

  const resetForm = () => {
    setNewQuestion({
      question_text: '',
      question_type: 'multiple_choice',
      difficulty_level: 'medium',
      category: '',
      course_id: '',
      correct_answer: '',
      options: ['', '', '', ''],
      is_active: true
    });
    setShowAdvancedForm(false);
  };

  const handleEdit = (question) => {
    setEditingQuestion(question);
    setNewQuestion({
      question_text: question.question_text,
      question_type: question.question_type,
      difficulty_level: question.difficulty_level,
      category: question.category || '',
      course_id: question.course_id || '',
      correct_answer: question.correct_answer,
      options: Array.isArray(question.options) ? question.options : ['', '', '', ''],
      is_active: question.is_active
    });
    setShowAdvancedForm(true); // Show full form when editing
    setShowAddForm(true);
  };

  const handleDelete = async (questionId) => {
    if (!window.confirm('Are you sure you want to delete this question?')) return;
    
    try {
      const response = await api.delete(`/admin/questions/${questionId}`);
      if (response.data.success) {
        toast.success('Question deleted successfully');
        fetchQuestions();
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to delete question');
    }
  };

  const toggleActive = async (questionId, currentStatus) => {
    try {
      const response = await api.put(`/admin/questions/${questionId}/toggle-active`);
      if (response.data.success) {
        toast.success(`Question ${currentStatus ? 'deactivated' : 'activated'} successfully`);
        fetchQuestions();
      }
    } catch (error) {
      toast.error('Failed to update question status');
    }
  };

  const handleOptionChange = (index, value) => {
    const currentOptions = Array.isArray(newQuestion.options) ? newQuestion.options : ['', '', '', ''];
    const newOptions = [...currentOptions];
    newOptions[index] = value;
    setNewQuestion(prev => ({ ...prev, options: newOptions }));
  };

  const addOption = () => {
    const currentOptions = Array.isArray(newQuestion.options) ? newQuestion.options : ['', '', '', ''];
    setNewQuestion(prev => ({
      ...prev,
      options: [...currentOptions, '']
    }));
  };

  const removeOption = (index) => {
    const currentOptions = Array.isArray(newQuestion.options) ? newQuestion.options : ['', '', '', ''];
    if (currentOptions.length > 2) {
      const newOptions = currentOptions.filter((_, i) => i !== index);
      setNewQuestion(prev => ({ ...prev, options: newOptions }));
    }
  };

  const filteredQuestions = questions.filter(question => {
    const matchesSearch = question.question_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         question.category?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = filterType === 'all' || question.question_type === filterType;
    const matchesDifficulty = filterDifficulty === 'all' || question.difficulty_level === filterDifficulty;
    
    return matchesSearch && matchesType && matchesDifficulty;
  });

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'multiple_choice': return 'bg-blue-100 text-blue-800';
      case 'coding': return 'bg-purple-100 text-purple-800';
      case 'essay': return 'bg-indigo-100 text-indigo-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading questions..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Question Management</h1>
            <p className="text-gray-600 mt-2">Create and manage assessment questions</p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleBulkGenerateAI}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              <span>🤖 Bulk Generate AI</span>
            </button>
            <button
              onClick={() => {
                setEditingQuestion(null);
                resetForm();
                setShowAddForm(true);
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              <Plus className="w-4 h-4" />
              <span>Add Question</span>
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center space-x-3">
              <HelpCircle className="w-8 h-8 text-blue-600" />
              <div>
                <p className="text-sm text-gray-600">Total Questions</p>
                <p className="text-2xl font-bold text-gray-900">{questions.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-8 h-8 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Active</p>
                <p className="text-2xl font-bold text-gray-900">
                  {questions.filter(q => q.is_active).length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center space-x-3">
              <XCircle className="w-8 h-8 text-red-600" />
              <div>
                <p className="text-sm text-gray-600">Inactive</p>
                <p className="text-2xl font-bold text-gray-900">
                  {questions.filter(q => !q.is_active).length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center space-x-3">
              <Filter className="w-8 h-8 text-purple-600" />
              <div>
                <p className="text-sm text-gray-600">Categories</p>
                <p className="text-2xl font-bold text-gray-900">
                  {new Set(questions.map(q => q.category).filter(Boolean)).size}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search questions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            
            <div className="flex items-center space-x-2">
              <Filter className="w-5 h-5 text-gray-400" />
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="all">All Types</option>
                <option value="multiple_choice">Multiple Choice</option>
                <option value="coding">Coding</option>
                <option value="essay">Essay</option>
              </select>
              
              <select
                value={filterDifficulty}
                onChange={(e) => setFilterDifficulty(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="all">All Difficulties</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
          </div>
        </div>

        {/* Questions Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Question
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Difficulty
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Course
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredQuestions.map((question) => (
                  <tr key={question.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 max-w-md">
                        <p className="truncate">{question.question_text}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          Created: {new Date(question.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(question.question_type)}`}>
                        {question.question_type.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(question.difficulty_level)}`}>
                        {question.difficulty_level}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {question.category || 'Uncategorized'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {question.course_id ? (
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                            Course Linked
                          </span>
                        ) : (
                          <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                            General
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => toggleActive(question.id, question.is_active)}
                        className={`flex items-center space-x-1 px-2 py-1 text-xs font-medium rounded-full ${
                          question.is_active
                            ? 'bg-green-100 text-green-800 hover:bg-green-200'
                            : 'bg-red-100 text-red-800 hover:bg-red-200'
                        }`}
                      >
                        {question.is_active ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
                        <span>{question.is_active ? 'Active' : 'Inactive'}</span>
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleEdit(question)}
                          className="text-primary-600 hover:text-primary-900"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(question.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {filteredQuestions.length === 0 && (
            <div className="text-center py-12">
              <HelpCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No questions found</h3>
              <p className="text-gray-600">
                {searchTerm || filterType !== 'all' || filterDifficulty !== 'all'
                  ? 'Try adjusting your search or filter criteria'
                  : 'Get started by adding your first question'
                }
              </p>
            </div>
          )}
        </div>

        {/* Add/Edit Question Modal */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                {editingQuestion ? 'Edit Question' : 'Add New Question'}
              </h3>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                {!showAdvancedForm ? (
                  // Simplified form - only basic fields
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Question Type *
                        </label>
                        <select
                          value={newQuestion.question_type}
                          onChange={(e) => setNewQuestion(prev => ({ ...prev, question_type: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          required
                        >
                          <option value="multiple_choice">Multiple Choice</option>
                          <option value="coding">Coding</option>
                          <option value="essay">Essay</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Difficulty *
                        </label>
                        <select
                          value={newQuestion.difficulty_level}
                          onChange={(e) => setNewQuestion(prev => ({ ...prev, difficulty_level: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          required
                        >
                          <option value="easy">Easy</option>
                          <option value="medium">Medium</option>
                          <option value="hard">Hard</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Category
                        </label>
                        <input
                          type="text"
                          value={newQuestion.category}
                          onChange={(e) => setNewQuestion(prev => ({ ...prev, category: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          placeholder="e.g., JavaScript, Python"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Course (Optional)
                        </label>
                        <select
                          value={newQuestion.course_id}
                          onChange={(e) => setNewQuestion(prev => ({ ...prev, course_id: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        >
                          <option value="">No specific course</option>
                          {courses.map(course => (
                            <option key={course.id} value={course.id}>
                              {course.title} ({course.skill_level})
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <div className="text-center py-4 space-y-3">
                      <button
                        type="button"
                        onClick={handleGenerateAIQuestion}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2 mx-auto"
                      >
                        <Plus className="w-4 h-4" />
                        <span>Create Question with AI</span>
                      </button>
                      <p className="text-sm text-gray-500">
                        AI will generate a complete question based on your selections
                      </p>
                      
                      <div className="flex items-center space-x-4">
                        <div className="flex-1 border-t border-gray-300"></div>
                        <span className="text-sm text-gray-500">or</span>
                        <div className="flex-1 border-t border-gray-300"></div>
                      </div>
                      
                      <button
                        type="button"
                        onClick={() => setShowAdvancedForm(true)}
                        className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center space-x-2 mx-auto"
                      >
                        <Edit2 className="w-4 h-4" />
                        <span>Create Manually</span>
                      </button>
                    </div>
                  </>
                ) : (
                  // Full form - all fields
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Question Text *
                      </label>
                      <textarea
                        value={newQuestion.question_text}
                        onChange={(e) => setNewQuestion(prev => ({ ...prev, question_text: e.target.value }))}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        required
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Question Type *
                        </label>
                        <select
                          value={newQuestion.question_type}
                          onChange={(e) => setNewQuestion(prev => ({ ...prev, question_type: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          required
                        >
                          <option value="multiple_choice">Multiple Choice</option>
                          <option value="coding">Coding</option>
                          <option value="essay">Essay</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Difficulty *
                        </label>
                        <select
                          value={newQuestion.difficulty_level}
                          onChange={(e) => setNewQuestion(prev => ({ ...prev, difficulty_level: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          required
                        >
                          <option value="easy">Easy</option>
                          <option value="medium">Medium</option>
                          <option value="hard">Hard</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Category
                        </label>
                        <input
                          type="text"
                          value={newQuestion.category}
                          onChange={(e) => setNewQuestion(prev => ({ ...prev, category: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          placeholder="e.g., JavaScript, Python"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Course (Optional)
                      </label>
                      <select
                        value={newQuestion.course_id}
                        onChange={(e) => setNewQuestion(prev => ({ ...prev, course_id: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      >
                        <option value="">No specific course</option>
                        {courses.map(course => (
                          <option key={course.id} value={course.id}>
                            {course.title} ({course.skill_level})
                          </option>
                        ))}
                      </select>
                    </div>

                    {newQuestion.question_type === 'multiple_choice' && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Answer Options *
                        </label>
                        <div className="space-y-2">
                          {(Array.isArray(newQuestion.options) ? newQuestion.options : ['', '', '', '']).map((option, index) => (
                            <div key={index} className="flex items-center space-x-2">
                              <input
                                type="text"
                                value={option}
                                onChange={(e) => handleOptionChange(index, e.target.value)}
                                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                                placeholder={`Option ${index + 1}`}
                              />
                              {(Array.isArray(newQuestion.options) ? newQuestion.options : ['', '', '', '']).length > 2 && (
                                <button
                                  type="button"
                                  onClick={() => removeOption(index)}
                                  className="text-red-600 hover:text-red-800"
                                >
                                  <XCircle className="w-5 h-5" />
                                </button>
                              )}
                            </div>
                          ))}
                          <button
                            type="button"
                            onClick={addOption}
                            className="text-primary-600 hover:text-primary-800 text-sm"
                          >
                            + Add Option
                          </button>
                        </div>
                      </div>
                    )}

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Correct Answer *
                      </label>
                      {newQuestion.question_type === 'multiple_choice' ? (
                        <select
                          value={newQuestion.correct_answer}
                          onChange={(e) => setNewQuestion(prev => ({ ...prev, correct_answer: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          required
                        >
                          <option value="">Select correct answer</option>
                          {(Array.isArray(newQuestion.options) ? newQuestion.options : []).filter(opt => opt.trim() !== '').map((option, index) => (
                            <option key={index} value={option}>{option}</option>
                          ))}
                        </select>
                      ) : (
                        <textarea
                          value={newQuestion.correct_answer}
                          onChange={(e) => setNewQuestion(prev => ({ ...prev, correct_answer: e.target.value }))}
                          rows={3}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                          placeholder="Enter the correct answer or solution..."
                          required
                        />
                      )}
                    </div>

                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="is_active"
                        checked={newQuestion.is_active}
                        onChange={(e) => setNewQuestion(prev => ({ ...prev, is_active: e.target.checked }))}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                        Active (available for assessments)
                      </label>
                    </div>
                  </>
                )}

                <div className="flex space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddForm(false);
                      setEditingQuestion(null);
                      setShowAdvancedForm(false);
                    }}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  {showAdvancedForm && (
                    <button
                      type="submit"
                      className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                    >
                      {editingQuestion ? 'Update' : 'Create'}
                    </button>
                  )}
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminQuestions;