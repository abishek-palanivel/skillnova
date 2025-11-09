import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { useAuth } from '../contexts/AuthContext';
import { 
  Code, 
  Play, 
  Clock, 
  Trophy,
  Filter,
  Search,
  Sparkles
} from 'lucide-react';
import toast from 'react-hot-toast';

const Practice = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    if (isAuthenticated) {
      fetchPracticeExercises();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const fetchPracticeExercises = async () => {
    try {
      const response = await api.get('/practice/questions');
      if (response.data.success) {
        setExercises(response.data.questions || []);
      }
    } catch (error) {
      console.error('Failed to fetch practice exercises:', error);
      if (error.response?.status === 401) {
        toast.error('Please log in to access practice exercises');
      } else if (error.response?.status === 500) {
        toast.error('Server error. Please try again later.');
      } else {
        toast.error('Failed to load practice exercises');
      }
    } finally {
      setLoading(false);
    }
  };



  const handleStartExercise = async (questionId) => {
    try {
      // Navigate to practice question page
      navigate(`/practice/question/${questionId}`);
    } catch (error) {
      toast.error('Failed to start exercise');
    }
  };

  const filteredExercises = exercises.filter(exercise => {
    const matchesSearch = exercise.question_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         exercise.category?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDifficulty = selectedDifficulty === 'all' || exercise.difficulty_level === selectedDifficulty;
    const matchesCategory = selectedCategory === 'all' || exercise.category === selectedCategory;
    return matchesSearch && matchesDifficulty && matchesCategory;
  });

  const difficulties = ['all', 'easy', 'medium', 'hard'];
  const categories = ['all', ...new Set(exercises.map(ex => ex.category).filter(Boolean))];

  if (loading) {
    return <LoadingSpinner text="Loading practice exercises..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Practice Exercises
          </h1>
          <p className="text-gray-600">
            Sharpen your skills with interactive exercises and coding challenges
          </p>
        </div>



        {/* Search and Filter */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search exercises..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              {difficulties.map(difficulty => (
                <option key={difficulty} value={difficulty}>
                  {difficulty === 'all' ? 'All Difficulties' : difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                </option>
              ))}
            </select>
            
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

        {/* Exercises Grid */}
        {filteredExercises.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredExercises.map((exercise) => (
              <div key={exercise.id} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      exercise.difficulty_level === 'easy' ? 'bg-green-100 text-green-700' :
                      exercise.difficulty_level === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {exercise.difficulty_level.charAt(0).toUpperCase() + exercise.difficulty_level.slice(1)}
                    </span>
                    <div className="flex items-center space-x-1">
                      <Code className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-600">{exercise.question_type}</span>
                    </div>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                    {exercise.question_text.length > 60 
                      ? `${exercise.question_text.substring(0, 60)}...` 
                      : exercise.question_text}
                  </h3>
                  
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>~30 min</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Trophy className="w-4 h-4" />
                      <span>100 pts</span>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => handleStartExercise(exercise.id)}
                    className="w-full btn-primary flex items-center justify-center space-x-2"
                  >
                    <Play className="w-4 h-4" />
                    <span>Start Exercise</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Code className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No practice questions available</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || selectedDifficulty !== 'all' || selectedCategory !== 'all'
                ? 'Try adjusting your search or filter criteria'
                : 'Admin needs to create practice questions using AI generation'
              }
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
              <div className="flex items-center space-x-2 text-blue-700">
                <Sparkles className="w-5 h-5" />
                <span className="font-medium">For Admins</span>
              </div>
              <p className="text-blue-600 text-sm mt-1">
                Use the admin panel to generate AI-powered practice questions for students
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Practice;