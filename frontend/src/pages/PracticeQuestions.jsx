import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  Brain, 
  Filter, 
  RefreshCw, 
  CheckCircle, 
  XCircle,
  ArrowLeft,
  BookOpen,
  Target,
  Lightbulb,
  Award
} from 'lucide-react';
import toast from 'react-hot-toast';

const PracticeQuestions = () => {
  const { questionId } = useParams();
  const [loading, setLoading] = useState(true);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [showResults, setShowResults] = useState({});
  const [score, setScore] = useState({ correct: 0, total: 0 });
  
  // Filters
  const [categories, setCategories] = useState([]);
  const [difficulties, setDifficulties] = useState([]);
  const [questionTypes, setQuestionTypes] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchCategories();
    fetchQuestions();
  }, []);

  useEffect(() => {
    if (!questionId) {
      fetchQuestions();
    }
  }, [selectedCategory, selectedDifficulty, selectedType]);

  const fetchCategories = async () => {
    try {
      const response = await api.get('/user/questions/categories');
      if (response.data.success) {
        setCategories(response.data.categories);
        setDifficulties(response.data.difficulties);
        setQuestionTypes(response.data.question_types);
      }
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      
      if (questionId) {
        // Fetch specific question from practice endpoint
        const response = await api.get('/practice/questions');
        if (response.data.success) {
          const specificQuestion = response.data.questions.find(q => q.id === questionId);
          if (specificQuestion) {
            setQuestions([specificQuestion]);
            setCurrentQuestionIndex(0);
            setUserAnswers({});
            setShowResults({});
            setScore({ correct: 0, total: 0 });
          } else {
            toast.error('Question not found');
            setQuestions([]);
          }
        } else {
          toast.error(response.data.message || 'Failed to load question');
        }
      } else {
        // Fetch questions with filters (original behavior)
        const params = new URLSearchParams();
        if (selectedCategory) params.append('category', selectedCategory);
        if (selectedDifficulty) params.append('difficulty', selectedDifficulty);
        if (selectedType) params.append('type', selectedType);
        params.append('limit', '20');

        const response = await api.get(`/practice/questions?${params}`);
        if (response.data.success) {
          setQuestions(response.data.questions);
          setCurrentQuestionIndex(0);
          setUserAnswers({});
          setShowResults({});
          setScore({ correct: 0, total: 0 });
          
          if (response.data.questions.length === 0) {
            toast.info('No questions found for the selected filters');
          }
        } else {
          toast.error(response.data.message || 'Failed to load questions');
        }
      }
    } catch (error) {
      console.error('Failed to fetch questions:', error);
      toast.error('Failed to load questions');
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async (questionId, answer) => {
    try {
      const response = await api.post('/practice/submit-answer', {
        question_id: questionId,
        answer: answer
      });
      
      if (response.data.success) {
        setShowResults(prev => ({
          ...prev,
          [questionId]: {
            is_correct: response.data.is_correct,
            correct_answer: response.data.correct_answer,
            explanation: response.data.explanation,
            user_answer: response.data.user_answer
          }
        }));
        
        // Update score
        setScore(prev => ({
          correct: prev.correct + (response.data.is_correct ? 1 : 0),
          total: prev.total + 1
        }));
        
        if (response.data.is_correct) {
          toast.success('Correct! 🎉');
        } else {
          toast.error('Incorrect. Check the explanation below.');
        }
      }
    } catch (error) {
      console.error('Failed to submit answer:', error);
      toast.error('Failed to submit answer');
    }
  };

  const handleAnswerSelect = (questionId, answer) => {
    setUserAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
    
    // Auto-submit for multiple choice after a short delay to show selection
    const question = questions.find(q => q.id === questionId);
    if (question && question.question_type === 'multiple_choice') {
      setTimeout(() => {
        submitAnswer(questionId, answer);
      }, 300);
    }
  };

  const handleSubmitAnswer = (questionId) => {
    const answer = userAnswers[questionId];
    if (answer) {
      submitAnswer(questionId, answer);
    } else {
      toast.error('Please provide an answer');
    }
  };

  const nextQuestion = () => {
    const currentQ = questions[currentQuestionIndex];
    const hasAnswered = currentQ && showResults[currentQ.id];
    
    if (!hasAnswered) {
      toast.error('Please answer the current question before proceeding');
      return;
    }
    
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const prevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const resetQuiz = () => {
    setCurrentQuestionIndex(0);
    setUserAnswers({});
    setShowResults({});
    setScore({ correct: 0, total: 0 });
    fetchQuestions();
  };

  if (loading) {
    return <LoadingSpinner text="Loading practice questions..." />;
  }

  const currentQuestion = questions[currentQuestionIndex];
  const result = currentQuestion ? showResults[currentQuestion.id] : null;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            to={questionId ? "/practice" : "/dashboard"}
            className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            {questionId ? "Back to Practice" : "Back to Dashboard"}
          </Link>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Brain className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Practice Questions</h1>
                <p className="text-gray-600">Test your knowledge with AI-generated questions</p>
              </div>
            </div>
            
            {/* Score */}
            {score.total > 0 && (
              <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
                <div className="flex items-center space-x-2">
                  <Award className="w-5 h-5 text-yellow-600" />
                  <span className="font-medium text-gray-900">
                    Score: {score.correct}/{score.total}
                  </span>
                  <span className="text-sm text-gray-600">
                    ({Math.round((score.correct / score.total) * 100)}%)
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Filters - Only show when not viewing a specific question */}
        {!questionId && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center space-x-2 text-blue-600 hover:text-blue-700"
            >
              <Filter className="w-4 h-4" />
              <span>{showFilters ? 'Hide' : 'Show'} Filters</span>
            </button>
          </div>
          
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Categories</option>
                  {categories.map((category) => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Difficulty</label>
                <select
                  value={selectedDifficulty}
                  onChange={(e) => setSelectedDifficulty(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Difficulties</option>
                  {difficulties.map((difficulty) => (
                    <option key={difficulty} value={difficulty}>
                      {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Types</option>
                  {questionTypes.map((type) => (
                    <option key={type} value={type}>
                      {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="flex items-end">
                <button
                  onClick={resetQuiz}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Refresh</span>
                </button>
              </div>
            </div>
          )}
        </div>
        )}

        {questions.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Questions Available</h3>
            <p className="text-gray-600 mb-4">
              No questions found for the selected filters. Try adjusting your filters or check back later.
            </p>
            <button
              onClick={resetQuiz}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 mx-auto"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh Questions</span>
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Question Navigation */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">
                    Question {currentQuestionIndex + 1} of {questions.length}
                  </span>
                  <div className="flex space-x-1">
                    {questions.map((question, index) => (
                      <button
                        key={index}
                        onClick={() => setCurrentQuestionIndex(index)}
                        className={`w-3 h-3 rounded-full transition-colors ${
                          index === currentQuestionIndex
                            ? 'bg-blue-600 ring-2 ring-blue-200'
                            : showResults[question.id]
                            ? showResults[question.id].is_correct
                              ? 'bg-green-500'
                              : 'bg-red-500'
                            : userAnswers[question.id]
                            ? 'bg-yellow-400'
                            : 'bg-gray-300'
                        }`}
                        title={
                          showResults[question.id]
                            ? showResults[question.id].is_correct
                              ? 'Correct'
                              : 'Incorrect'
                            : userAnswers[question.id]
                            ? 'Answered (not submitted)'
                            : 'Not answered'
                        }
                      />
                    ))}
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={prevQuestion}
                    disabled={currentQuestionIndex === 0}
                    className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={nextQuestion}
                    disabled={currentQuestionIndex === questions.length - 1}
                    className={`px-3 py-1 text-sm border rounded-md disabled:opacity-50 disabled:cursor-not-allowed ${
                      currentQuestion && showResults[currentQuestion.id]
                        ? 'border-gray-300 hover:bg-gray-50'
                        : 'border-orange-300 bg-orange-50 text-orange-700 hover:bg-orange-100'
                    }`}
                  >
                    {currentQuestion && showResults[currentQuestion.id] ? 'Next' : 'Answer First'}
                  </button>
                </div>
              </div>
            </div>

            {/* Quiz Completion */}
            {questions.length > 0 && score.total === questions.length && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
                <div className="flex items-center justify-center space-x-2 mb-4">
                  <Award className="w-8 h-8 text-yellow-600" />
                  <h2 className="text-2xl font-bold text-gray-900">Quiz Completed!</h2>
                </div>
                <p className="text-lg text-gray-700 mb-4">
                  Final Score: {score.correct}/{score.total} ({Math.round((score.correct / score.total) * 100)}%)
                </p>
                <div className="flex justify-center space-x-4">
                  <button
                    onClick={resetQuiz}
                    className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>Try Again</span>
                  </button>
                  <Link
                    to="/dashboard"
                    className="flex items-center space-x-2 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    <span>Back to Dashboard</span>
                  </Link>
                </div>
              </div>
            )}

            {/* Current Question */}
            {currentQuestion && score.total < questions.length && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    currentQuestion.difficulty_level === 'easy' ? 'bg-green-100 text-green-700' :
                    currentQuestion.difficulty_level === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {currentQuestion.difficulty_level}
                  </span>
                  <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                    {currentQuestion.category}
                  </span>
                  <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full">
                    {currentQuestion.question_type.replace('_', ' ')}
                  </span>
                </div>

                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  {currentQuestion.question_text}
                </h3>

                {/* Multiple Choice Options */}
                {currentQuestion.question_type === 'multiple_choice' && currentQuestion.options && (
                  <div className="space-y-2 mb-4">
                    {!userAnswers[currentQuestion.id] && !result && (
                      <div className="text-sm text-orange-600 bg-orange-50 p-2 rounded-md mb-2">
                        <Target className="w-4 h-4 inline mr-1" />
                        Please select an answer to continue
                      </div>
                    )}
                    {Object.entries(currentQuestion.options).map(([key, value]) => (
                      <button
                        key={key}
                        onClick={() => handleAnswerSelect(currentQuestion.id, key)}
                        disabled={result}
                        className={`w-full text-left p-3 border rounded-lg transition-colors ${
                          result
                            ? // After answer is submitted
                              key === result.correct_answer
                                ? 'border-green-500 bg-green-50 text-green-800' // Correct answer (always green)
                                : userAnswers[currentQuestion.id] === key
                                ? 'border-red-500 bg-red-50 text-red-800' // Wrong answer selected by user (red)
                                : 'border-gray-300 bg-gray-50 text-gray-600' // Other options (grayed out)
                            : // Before answer is submitted
                              userAnswers[currentQuestion.id] === key
                                ? 'border-blue-500 bg-blue-50 text-blue-800' // Selected option (blue)
                                : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50' // Unselected options
                        } ${result ? 'cursor-not-allowed' : 'cursor-pointer'}`}
                      >
                        <span className="font-medium">{key}:</span> {value}
                        {result && key === result.correct_answer && (
                          <CheckCircle className="w-4 h-4 inline ml-2 text-green-600" />
                        )}
                        {result && userAnswers[currentQuestion.id] === key && key !== result.correct_answer && (
                          <XCircle className="w-4 h-4 inline ml-2 text-red-600" />
                        )}
                      </button>
                    ))}
                  </div>
                )}

                {/* Text Input for Other Question Types */}
                {currentQuestion.question_type !== 'multiple_choice' && (
                  <div className="mb-4">
                    <textarea
                      value={userAnswers[currentQuestion.id] || ''}
                      onChange={(e) => handleAnswerSelect(currentQuestion.id, e.target.value)}
                      placeholder="Enter your answer..."
                      disabled={result}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                      rows={4}
                    />
                    {!result && (
                      <button
                        onClick={() => handleSubmitAnswer(currentQuestion.id)}
                        className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                      >
                        Submit Answer
                      </button>
                    )}
                  </div>
                )}

                {/* Result and Explanation */}
                {result && (
                  <div className={`p-4 rounded-lg ${
                    result.is_correct ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                  }`}>
                    <div className="flex items-center space-x-2 mb-2">
                      {result.is_correct ? (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-600" />
                      )}
                      <span className={`font-medium ${
                        result.is_correct ? 'text-green-800' : 'text-red-800'
                      }`}>
                        {result.is_correct ? 'Correct!' : 'Incorrect'}
                      </span>
                    </div>
                    
                    {!result.is_correct && (
                      <div className="mb-2">
                        <p className="text-sm text-red-700 font-medium">
                          Your answer: {result.user_answer}
                        </p>
                        <p className="text-sm text-green-700 font-medium">
                          Correct answer: {result.correct_answer}
                        </p>
                      </div>
                    )}
                    
                    {result.explanation && (
                      <div className="flex items-start space-x-2">
                        <Lightbulb className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-gray-700">{result.explanation}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PracticeQuestions;