import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  Brain, 
  Clock, 
  CheckCircle, 
  ArrowRight, 
  ArrowLeft,
  Target,
  Award,
  BarChart3
} from 'lucide-react';
import toast from 'react-hot-toast';

const Assessment = () => {
  const { } = useAuth();
  const [loading, setLoading] = useState(true);
  const [assessmentStarted, setAssessmentStarted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(1800); // 30 minutes
  const [assessmentComplete, setAssessmentComplete] = useState(false);
  const [results, setResults] = useState(null);
  const [previousAssessments, setPreviousAssessments] = useState([]);
  const [aiRecommendations, setAiRecommendations] = useState(null);
  const [showRecommendations, setShowRecommendations] = useState(false);

  useEffect(() => {
    fetchPreviousAssessments();
  }, []);

  useEffect(() => {
    let timer;
    if (assessmentStarted && timeLeft > 0 && !assessmentComplete) {
      timer = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            handleSubmitAssessment();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [assessmentStarted, timeLeft, assessmentComplete]);

  const fetchPreviousAssessments = async () => {
    try {
      const response = await api.get('/user/assessments');
      if (response.data.success) {
        setPreviousAssessments(response.data.assessments || []);
      }
    } catch (error) {
      console.error('Failed to fetch assessments:', error);
    } finally {
      setLoading(false);
    }
  };

  const startAssessment = async () => {
    try {
      setLoading(true);
      const response = await api.get('/assessments/questions');
      if (response.data.success) {
        setQuestions(response.data.questions);
        setAssessmentStarted(true);
        setCurrentQuestion(0);
        setAnswers({});
        setTimeLeft(1800);
        setAssessmentComplete(false);
      }
    } catch (error) {
      toast.error('Failed to start assessment');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleSubmitAssessment = async () => {
    try {
      setLoading(true);
      const timeTaken = Math.floor((1800 - timeLeft) / 60);
      
      const response = await api.post('/assessments/submit', {
        answers,
        time_taken_minutes: timeTaken,
        assessment_type: 'initial'
      });
      
      if (response.data.success) {
        setResults(response.data.results);
        setAssessmentComplete(true);
        toast.success('Assessment completed successfully!');
        fetchPreviousAssessments();
      }
    } catch (error) {
      toast.error('Failed to submit assessment');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const fetchAIRecommendations = async () => {
    try {
      setLoading(true);
      const response = await api.get('/assessments/recommendations');
      if (response.data.success) {
        setAiRecommendations(response.data.recommendations);
        setShowRecommendations(true);
        toast.success('AI recommendations generated!');
      }
    } catch (error) {
      toast.error('Failed to get AI recommendations');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading assessment..." />;
  }

  // AI Recommendations View
  if (showRecommendations && aiRecommendations) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Brain className="w-8 h-8 text-blue-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">AI-Powered Recommendations</h1>
            <p className="text-gray-600">Personalized learning path based on your assessment results</p>
          </div>

          {/* User Profile Summary */}
          {aiRecommendations.user_profile && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Learning Profile</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-2">Interests</h3>
                  <div className="flex flex-wrap gap-2">
                    {aiRecommendations.user_profile.interests?.map((interest, index) => (
                      <span key={index} className="px-2 py-1 bg-blue-200 text-blue-800 rounded-full text-sm">
                        {interest.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <h3 className="font-semibold text-green-900 mb-2">Skill Level</h3>
                  <span className="px-3 py-1 bg-green-200 text-green-800 rounded-full text-sm font-medium">
                    {aiRecommendations.user_profile.skill_level?.replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <h3 className="font-semibold text-purple-900 mb-2">Profile Completeness</h3>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 bg-purple-200 rounded-full h-2">
                      <div 
                        className="bg-purple-600 h-2 rounded-full" 
                        style={{ width: `${aiRecommendations.user_profile.profile_completeness || 0}%` }}
                      ></div>
                    </div>
                    <span className="text-purple-800 text-sm font-medium">
                      {Math.round(aiRecommendations.user_profile.profile_completeness || 0)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Recommended Courses */}
          {aiRecommendations.courses && aiRecommendations.courses.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Recommended Courses</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {aiRecommendations.courses.map((course, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-2">
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                        {course.skill_level}
                      </span>
                      <span className="text-green-600 font-semibold text-sm">
                        {course.match_score}% match
                      </span>
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-2">{course.title}</h3>
                    <p className="text-gray-600 text-sm mb-3">{course.category}</p>
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span>{course.duration_weeks} weeks</span>
                      <span>⭐ {course.rating}</span>
                    </div>
                    <button className="w-full mt-3 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 text-sm">
                      Enroll Now
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}



          {/* Learning Path */}
          {aiRecommendations.learning_path && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Personalized Learning Path</h2>
              <div className="mb-4">
                <h3 className="font-semibold text-gray-900">{aiRecommendations.learning_path.title}</h3>
                <p className="text-gray-600">Estimated Duration: {aiRecommendations.learning_path.estimated_duration}</p>
              </div>
              
              {aiRecommendations.learning_path.phases && (
                <div className="space-y-4">
                  {aiRecommendations.learning_path.phases.map((phase, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center space-x-3 mb-2">
                        <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                          {phase.phase}
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900">{phase.title}</h4>
                          <p className="text-gray-600 text-sm">{phase.duration}</p>
                        </div>
                      </div>
                      
                      {phase.courses && (
                        <div className="mt-3">
                          <p className="text-sm font-medium text-gray-700 mb-2">Recommended Courses:</p>
                          <div className="flex flex-wrap gap-2">
                            {phase.courses.map((course, courseIndex) => (
                              <span key={courseIndex} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                                {course.title}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="text-center">
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => window.location.href = '/courses'}
                className="btn-primary"
              >
                Browse Courses
              </button>
              <button
                onClick={() => {
                  setShowRecommendations(false);
                  setAssessmentStarted(false);
                  setAssessmentComplete(false);
                  setResults(null);
                  setAiRecommendations(null);
                }}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Take New Assessment
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Assessment Results View
  if (assessmentComplete && results) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Award className="w-8 h-8 text-green-600" />
            </div>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Assessment Complete!</h1>
            <p className="text-gray-600 mb-8">Here are your results</p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-gray-50 rounded-lg p-6">
                <BarChart3 className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <h3 className="font-semibold text-gray-900">Score</h3>
                <p className={`text-2xl font-bold ${getScoreColor(results.score_percentage)}`}>
                  {results.score_percentage}%
                </p>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-6">
                <Target className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                <h3 className="font-semibold text-gray-900">Correct Answers</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {results.correct_answers}/{results.total_questions}
                </p>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-6">
                <Clock className="w-8 h-8 text-orange-600 mx-auto mb-2" />
                <h3 className="font-semibold text-gray-900">Time Taken</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {results.time_taken_minutes} min
                </p>
              </div>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
              <h3 className="font-semibold text-blue-900 mb-2">Skill Level Assessment</h3>
              <p className="text-blue-800">
                Based on your score of {results.score_percentage}%, you are at a{' '}
                <span className="font-semibold">
                  {results.score_percentage >= 80 ? 'Advanced' : 
                   results.score_percentage >= 60 ? 'Intermediate' : 'Beginner'}
                </span> level.
              </p>
            </div>
            
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => fetchAIRecommendations()}
                className="btn-primary"
              >
                Get AI Recommendations
              </button>
              <button
                onClick={() => window.location.href = '/courses'}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Browse All Courses
              </button>
              <button
                onClick={() => {
                  setAssessmentStarted(false);
                  setAssessmentComplete(false);
                  setResults(null);
                }}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Retake Assessment
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Assessment Questions View
  if (assessmentStarted && questions.length > 0) {
    const question = questions[currentQuestion];
    
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          {/* Header */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Brain className="w-6 h-6 text-primary-600" />
                <span className="font-semibold text-gray-900">
                  Question {currentQuestion + 1} of {questions.length}
                </span>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 text-orange-600">
                  <Clock className="w-5 h-5" />
                  <span className="font-mono font-semibold">
                    {formatTime(timeLeft)}
                  </span>
                </div>
              </div>
            </div>
            
            {/* Progress Bar */}
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300" 
                  style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Question */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              {question.question_text}
            </h2>
            
            {question.question_type === 'multiple_choice' && Array.isArray(question.options) && (
              <div className="space-y-3">
                {question.options.map((option, index) => (
                  <label
                    key={index}
                    className={`flex items-center p-4 border rounded-lg cursor-pointer transition-colors ${
                      answers[question.id] === option
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name={`question-${question.id}`}
                      value={option}
                      checked={answers[question.id] === option}
                      onChange={() => handleAnswerSelect(question.id, option)}
                      className="sr-only"
                    />
                    <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                      answers[question.id] === option
                        ? 'border-primary-500 bg-primary-500'
                        : 'border-gray-300'
                    }`}>
                      {answers[question.id] === option && (
                        <div className="w-2 h-2 bg-white rounded-full mx-auto mt-0.5"></div>
                      )}
                    </div>
                    <span className="text-gray-900">{option}</span>
                  </label>
                ))}
              </div>
            )}
            
            {question.question_type === 'coding' && (
              <div>
                <textarea
                  value={answers[question.id] || ''}
                  onChange={(e) => handleAnswerSelect(question.id, e.target.value)}
                  placeholder="Write your code here..."
                  className="w-full h-40 px-4 py-3 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            )}
            
            {/* Navigation */}
            <div className="flex justify-between mt-8">
              <button
                onClick={handlePrevious}
                disabled={currentQuestion === 0}
                className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Previous</span>
              </button>
              
              <div className="flex space-x-3">
                {currentQuestion === questions.length - 1 ? (
                  <button
                    onClick={handleSubmitAssessment}
                    className="flex items-center space-x-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    <CheckCircle className="w-4 h-4" />
                    <span>Submit Assessment</span>
                  </button>
                ) : (
                  <button
                    onClick={handleNext}
                    className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    <span>Next</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Assessment Start View
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Skill Assessment</h1>
          <p className="text-gray-600">
            Take our comprehensive assessment to determine your skill level and get personalized course recommendations.
          </p>
        </div>

        {/* Assessment Info */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2 mb-2">
              <Brain className="w-5 h-5 text-blue-600" />
              <h3 className="font-semibold text-blue-900">AI-Powered Assessment</h3>
            </div>
            <p className="text-blue-800 text-sm">
              Our AI analyzes your bio data and generates personalized questions based on your interests, 
              skills, and goals to provide the most accurate skill assessment and course recommendations.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="text-center">
              <Clock className="w-12 h-12 text-blue-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-1">Duration</h3>
              <p className="text-gray-600">30 minutes</p>
            </div>
            
            <div className="text-center">
              <Target className="w-12 h-12 text-purple-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-1">Questions</h3>
              <p className="text-gray-600">20 AI-generated questions</p>
            </div>
            
            <div className="text-center">
              <Award className="w-12 h-12 text-green-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-1">Result</h3>
              <p className="text-gray-600">Instant feedback</p>
            </div>
          </div>
          
          <div className="text-center">
            <button
              onClick={startAssessment}
              className="btn-primary text-lg px-8 py-3"
            >
              Start Assessment
            </button>
          </div>
        </div>

        {/* Previous Assessments */}
        {previousAssessments.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Previous Assessments</h2>
            
            <div className="space-y-3">
              {previousAssessments.map((assessment) => (
                <div key={assessment.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">
                      {assessment.assessment_type.replace('_', ' ').toUpperCase()} Assessment
                    </p>
                    <p className="text-sm text-gray-600">
                      {new Date(assessment.completed_at).toLocaleDateString()}
                    </p>
                  </div>
                  
                  <div className="text-right">
                    <p className={`font-bold ${getScoreColor(assessment.score_percentage)}`}>
                      {assessment.score_percentage}%
                    </p>
                    <p className="text-sm text-gray-600">
                      {assessment.correct_answers}/{assessment.total_questions} correct
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Assessment;