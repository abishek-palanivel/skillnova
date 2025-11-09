import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  ArrowRight, 
  ArrowLeft,
  BookOpen,
  Target,
  Award,
  TrendingUp
} from 'lucide-react';
import toast from 'react-hot-toast';

const AssessmentTaking = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { type, courseId } = useParams(); // 'initial', 'final', or 'course'
  
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(3600); // 60 minutes in seconds
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    if (user) {
      fetchAssessmentQuestions();
    }
  }, [user, type]);

  useEffect(() => {
    if (timeLeft > 0 && !showResults) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0) {
      handleSubmitAssessment();
    }
  }, [timeLeft, showResults]);

  // Add keyboard event handler to prevent bypassing validation
  useEffect(() => {
    const handleKeyPress = (event) => {
      // Prevent Enter or Arrow Right from proceeding without an answer
      if ((event.key === 'Enter' || event.key === 'ArrowRight') && !showResults) {
        const currentQuestionId = questions[currentQuestion]?.id;
        if (!currentQuestionId || !answers[currentQuestionId] || answers[currentQuestionId] === '') {
          event.preventDefault();
          toast.error('Please select an answer before proceeding');
          return false;
        }
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [currentQuestion, answers, questions, showResults]);

  const fetchAssessmentQuestions = async () => {
    try {
      setLoading(true);
      
      // Check if this is a course-specific assessment
      if (type === 'course' && courseId) {
        console.log('Loading course assessment for course:', courseId);
        const response = await api.get(`/tests/course-assessment/${courseId}`);
        
        if (response.data.success) {
          const assessmentData = response.data.assessment;
          setQuestions(assessmentData.questions || []);
          setUserProfile(null);
          
          // Set timer for course assessment (90 minutes)
          setTimeLeft(assessmentData.duration_minutes * 60 || 5400);
          
          toast.success(`🎓 ${assessmentData.title} loaded successfully!`);
          setLoading(false);
          return;
        }
      }
      
      // Check if this is an AI personalized assessment
      const isAIPersonalized = window.location.pathname.includes('ai-personalized');
      
      let response;
      if (isAIPersonalized) {
        // Get AI personalized assessment
        response = await api.get('/assessments/ai-personalized');
        
        if (response.data.success) {
          const questionsData = response.data.questions || [];
          console.log('AI Personalized assessment loaded:', questionsData.length, 'questions');
          
          setQuestions(questionsData);
          setUserProfile(response.data.user_profile);
          
          // Set timer for AI assessment (60 minutes)
          setTimeLeft(3600);
          
          toast.success(response.data.message || '🤖 AI personalized assessment ready!');
          setLoading(false);
          return;
        }
      } else {
        // Try regular assessments endpoint first
        try {
          response = await api.get('/assessments/questions');
        } catch (assessmentError) {
          console.log('Assessment endpoint failed, trying tests endpoint');
          // Fallback to tests endpoint
          if (type === 'final') {
            response = await api.get('/tests/final-assessment');
          } else {
            response = await api.get('/tests/initial-assessment');
          }
          if (response.data.success) {
            const assessmentData = response.data.assessment;
            setQuestions(assessmentData.questions || []);
            setUserProfile(null);
            
            // Set timer based on assessment type
            const timeLimit = type === 'final' ? 5400 : 3600; // 90 min for final, 60 min for initial
            setTimeLeft(timeLimit);
            
            toast.success('Assessment loaded successfully');
            setLoading(false);
            return;
          }
        }
        
        if (response && response.data.success) {
          const questionsData = response.data.questions || [];
          console.log('Assessment questions loaded:', questionsData);
          if (questionsData.length > 0) {
            console.log('First question:', questionsData[0]);
          }
          setQuestions(questionsData);
          setUserProfile(response.data.user_profile);
          
          // Set timer based on assessment type
          const timeLimit = type === 'final' ? 5400 : 3600; // 90 min for final, 60 min for initial
          setTimeLeft(timeLimit);
          
          toast.success(response.data.message || 'Assessment loaded successfully');
        } else {
          toast.error(response?.data?.message || 'Failed to load assessment');
          navigate('/tests');
        }
      }
    } catch (error) {
      console.error('Failed to fetch assessment questions:', error);
      toast.error('Failed to load assessment questions');
      navigate('/tests');
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

  const handleNextQuestion = () => {
    const currentQuestionId = questions[currentQuestion]?.id;
    
    // Strong validation - prevent proceeding without an answer
    if (!currentQuestionId || !answers[currentQuestionId] || answers[currentQuestionId] === '') {
      toast.error('Please select an answer before proceeding to the next question');
      return;
    }
    
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmitAssessment = async () => {
    // Check if all questions are answered
    const unansweredQuestions = questions.filter(q => !answers[q.id]);
    if (unansweredQuestions.length > 0) {
      toast.error(`Please answer all questions before submitting. ${unansweredQuestions.length} questions remaining.`);
      return;
    }
    
    try {
      setSubmitting(true);
      
      const timeTaken = type === 'final' ? 
        Math.round((5400 - timeLeft) / 60) : 
        Math.round((3600 - timeLeft) / 60);

      // Determine the submission endpoint and data based on assessment type
      let submitData = {
        answers: Object.keys(answers).map(questionId => ({
          question_id: questionId,
          answer: answers[questionId]
        })),
        time_taken_minutes: timeTaken
      };

      let submitEndpoint = '/assessments/submit';
      
      if (type === 'course' && courseId) {
        submitData.test_type = 'course_final';
        submitData.course_id = courseId;
        submitEndpoint = '/tests/submit';
      } else {
        submitData.test_type = type || 'initial';
        submitEndpoint = '/tests/submit';
      }

      const response = await api.post(submitEndpoint, submitData);

      if (response.data.success) {
        setResults(response.data.results);
        setShowResults(true);
        toast.success('🎉 Assessment completed! Your personalized recommendations are ready!');
      } else {
        toast.error(response.data.message || 'Failed to submit assessment');
      }
    } catch (error) {
      console.error('Failed to submit assessment:', error);
      toast.error('Failed to submit assessment');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = () => {
    return ((currentQuestion + 1) / questions.length) * 100;
  };

  const getAnsweredCount = () => {
    return Object.keys(answers).length;
  };

  if (loading) {
    return <LoadingSpinner text="Loading assessment..." />;
  }

  if (!user) {
    navigate('/login');
    return null;
  }

  if (showResults && results) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow-lg p-8">
            {/* Results Header */}
            <div className="text-center mb-8">
              <div className={`w-20 h-20 mx-auto mb-4 rounded-full flex items-center justify-center ${
                results.passed ? 'bg-green-100' : 'bg-red-100'
              }`}>
                {results.passed ? (
                  <CheckCircle className="w-10 h-10 text-green-600" />
                ) : (
                  <AlertCircle className="w-10 h-10 text-red-600" />
                )}
              </div>
              
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Assessment {results.passed ? 'Completed' : 'Needs Improvement'}
              </h1>
              
              <p className="text-gray-600">
                {type === 'initial' ? 'Initial' : 'Final'} Assessment Results
              </p>
            </div>

            {/* Score Display */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="text-center p-6 bg-blue-50 rounded-lg">
                <div className="text-3xl font-bold text-blue-600 mb-2">
                  {results.score_percentage}%
                </div>
                <div className="text-sm text-gray-600">Final Score</div>
              </div>
              
              <div className="text-center p-6 bg-green-50 rounded-lg">
                <div className="text-3xl font-bold text-green-600 mb-2">
                  {results.correct_answers}/{results.total_questions}
                </div>
                <div className="text-sm text-gray-600">Correct Answers</div>
              </div>
              
              <div className="text-center p-6 bg-purple-50 rounded-lg">
                <div className="text-3xl font-bold text-purple-600 mb-2">
                  {results.time_taken_minutes}m
                </div>
                <div className="text-sm text-gray-600">Time Taken</div>
              </div>
            </div>

            {/* Performance Level */}
            <div className="mb-8">
              <div className="flex items-center justify-center space-x-2 mb-4">
                <TrendingUp className={`w-6 h-6 ${
                  results.passed ? 'text-green-600' : 'text-red-600'
                }`} />
                <span className={`text-xl font-semibold ${
                  results.passed ? 'text-green-600' : 'text-red-600'
                }`}>
                  {results.performance_level}
                </span>
              </div>
              
              <div className="text-center">
                <p className="text-gray-700 mb-4">{results.recommendation}</p>
                
                {results.passed ? (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-green-800 font-medium">
                      🎉 Congratulations! You passed with {results.score_percentage}%
                    </p>
                    <p className="text-green-700 text-sm mt-1">
                      You've met the 60% passing requirement and can proceed to advanced courses.
                    </p>
                  </div>
                ) : (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800 font-medium">
                      You scored {results.score_percentage}% (Need 60% to pass)
                    </p>
                    <p className="text-red-700 text-sm mt-1">
                      Don't worry! Review the recommended courses and retake when ready.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Certificate Section */}
            {results.certificate && (
              <div className="mb-8">
                <div className="bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-300 rounded-lg p-6">
                  <div className="text-center">
                    <Award className="w-16 h-16 text-yellow-600 mx-auto mb-4" />
                    <h3 className="text-2xl font-bold text-yellow-900 mb-2">🎉 Certificate Earned!</h3>
                    <p className="text-yellow-800 mb-4">
                      Congratulations! You've successfully completed the course and earned your certificate.
                    </p>
                    
                    <div className="bg-white rounded-lg p-4 mb-4 border border-yellow-200">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-600">Certificate Number</p>
                          <p className="font-mono font-semibold text-gray-900">
                            #{results.certificate.certificate_number?.slice(-8)}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-600">Final Score</p>
                          <p className="font-semibold text-gray-900">{results.certificate.final_score}%</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Course</p>
                          <p className="font-semibold text-gray-900">{results.certificate.course_title}</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Issued Date</p>
                          <p className="font-semibold text-gray-900">
                            {new Date(results.certificate.issued_date).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => {
                        const link = document.createElement('a');
                        link.href = `/api${results.certificate.download_url}`;
                        link.download = `certificate_${results.certificate.certificate_number}.pdf`;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        toast.success('Certificate download started!');
                      }}
                      className="px-6 py-3 bg-gradient-to-r from-yellow-600 to-orange-600 text-white rounded-lg hover:from-yellow-700 hover:to-orange-700 font-medium flex items-center justify-center space-x-2 mx-auto"
                    >
                      <Award className="w-5 h-5" />
                      <span>Download Certificate</span>
                    </button>
                    
                    <p className="text-xs text-yellow-700 mt-3">
                      AI-generated certificate with verification • PDF format
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* AI Course Recommendations */}
            {results.ai_course_recommendations && results.ai_course_recommendations.length > 0 && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                  <Target className="w-5 h-5 mr-2 text-orange-500" />
                  🤖 AI Course Recommendations
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {results.ai_course_recommendations.slice(0, 6).map((course, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <h4 className="font-semibold text-gray-900 mb-2">{course.title}</h4>
                      <p className="text-sm text-gray-600 mb-3">{course.description}</p>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-blue-600">{course.skill_level}</span>
                        <span className="text-green-600">{course.duration}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI Course Recommendations */}
            {results.course_recommendations && results.course_recommendations.recommendations && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                  <Target className="w-5 h-5 mr-2 text-orange-500" />
                  🤖 AI-Personalized Course Recommendations
                </h3>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                  <p className="text-blue-800 text-sm">
                    Based on your bio data and test performance, AI has found {results.course_recommendations.total_recommendations} personalized courses:
                    <span className="font-semibold"> {results.course_recommendations.skillnova_courses} SkillNova courses</span> and 
                    <span className="font-semibold"> {results.course_recommendations.external_courses} external courses</span>
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {results.course_recommendations.recommendations.slice(0, 9).map((course, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          course.source === 'SkillNova' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'
                        }`}>
                          {course.source}
                        </span>
                        <span className="text-sm text-orange-600 font-medium">
                          {Math.round((course.match_score || 0.8) * 100)}% match
                        </span>
                      </div>
                      
                      <h4 className="font-semibold text-gray-900 mb-2 text-sm">{course.title}</h4>
                      <p className="text-xs text-gray-600 mb-3 line-clamp-2">{course.description}</p>
                      
                      <div className="flex items-center justify-between text-xs mb-2">
                        <span className={`px-2 py-1 rounded-full ${
                          course.skill_level === 'Beginner' ? 'bg-green-100 text-green-700' :
                          course.skill_level === 'Intermediate' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          {course.skill_level}
                        </span>
                        <span className="text-yellow-600">★ {course.rating}</span>
                      </div>
                      
                      <div className="flex items-center justify-between text-xs mb-2">
                        <span className="text-gray-500">
                          {course.duration_weeks ? `${course.duration_weeks} weeks` : course.duration || 'Self-paced'}
                        </span>
                        <span className="font-semibold text-green-600">{course.price}</span>
                      </div>
                      
                      {course.platform && (
                        <div className="text-xs text-gray-500 mb-2">
                          Platform: {course.platform}
                        </div>
                      )}
                      
                      {course.ai_recommendation_reason && (
                        <p className="text-xs text-blue-600 mb-3 italic">
                          💡 {course.ai_recommendation_reason}
                        </p>
                      )}
                      
                      <button
                        onClick={() => {
                          if (course.source === 'SkillNova') {
                            navigate(course.url || `/courses/${course.id}`);
                          } else {
                            window.open(course.url, '_blank');
                          }
                        }}
                        className={`w-full text-xs py-2 px-3 rounded transition-colors ${
                          course.source === 'SkillNova'
                            ? 'bg-blue-600 text-white hover:bg-blue-700'
                            : 'bg-purple-600 text-white hover:bg-purple-700'
                        }`}
                      >
                        {course.source === 'SkillNova' ? 'Start Learning' : 'View Course'}
                      </button>
                    </div>
                  ))}
                </div>
                
                {results.course_recommendations.total_recommendations > 9 && (
                  <div className="text-center mt-4">
                    <p className="text-sm text-gray-600">
                      Showing top 9 of {results.course_recommendations.total_recommendations} recommendations
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate('/courses')}
                className="btn-primary flex items-center justify-center space-x-2"
              >
                <BookOpen className="w-4 h-4" />
                <span>Browse Courses</span>
              </button>
              
              <button
                onClick={() => navigate('/tests')}
                className="btn-secondary flex items-center justify-center space-x-2"
              >
                <Award className="w-4 h-4" />
                <span>View Test History</span>
              </button>
              
              {!results.passed && (
                <button
                  onClick={() => window.location.reload()}
                  className="btn-outline flex items-center justify-center space-x-2"
                >
                  <ArrowRight className="w-4 h-4" />
                  <span>Retake Assessment</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (questions.length === 0 && !loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <AlertCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">No Questions Available</h2>
            <p className="text-gray-600 mb-6">Unable to load assessment questions</p>
            <div className="space-y-3">
              <button 
                onClick={fetchAssessmentQuestions} 
                className="btn-primary"
              >
                Retry Loading Questions
              </button>
              <button 
                onClick={() => navigate('/tests')} 
                className="btn-secondary"
              >
                Back to Tests
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const question = questions[currentQuestion];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-gray-900">
              {type === 'initial' ? 'Initial' : 'Final'} Assessment
            </h1>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-gray-600">
                <Clock className="w-5 h-5" />
                <span className={`font-mono ${timeLeft < 300 ? 'text-red-600' : ''}`}>
                  {formatTime(timeLeft)}
                </span>
              </div>
              
              <div className="text-sm text-gray-600">
                {getAnsweredCount()}/{questions.length} answered
              </div>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${getProgressPercentage()}%` }}
            ></div>
          </div>
          
          <div className="flex justify-between text-sm text-gray-600 mt-2">
            <span>Question {currentQuestion + 1} of {questions.length}</span>
            <div className="flex items-center space-x-2">
              <span>{Math.round(getProgressPercentage())}% complete</span>
              {answers[questions[currentQuestion]?.id] ? (
                <CheckCircle className="w-4 h-4 text-green-600" />
              ) : (
                <AlertCircle className="w-4 h-4 text-red-500" />
              )}
            </div>
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-lg shadow-sm p-8 mb-6">
          <div className="mb-6">
            <div className="flex items-center space-x-2 mb-4">
              <span className={`px-3 py-1 text-sm font-medium rounded-full ${
                question?.difficulty_level === 'easy' ? 'bg-green-100 text-green-700' :
                question?.difficulty_level === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                'bg-red-100 text-red-700'
              }`}>
                {question?.difficulty_level || 'Medium'}
              </span>
              
              <span className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-full">
                {question?.category || 'General'}
              </span>
            </div>
            
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {question?.question_text}
            </h2>
          </div>

          {/* Answer Options */}
          {question?.question_type === 'multiple_choice' && question?.options && Array.isArray(question.options) && (
            <div className="space-y-3">
              {question.options.map((option, index) => (
                <label
                  key={index}
                  className={`flex items-center p-4 border rounded-lg cursor-pointer transition-colors ${
                    answers[question.id] === option
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name={`question_${question.id}`}
                    value={option}
                    checked={answers[question.id] === option}
                    onChange={() => handleAnswerSelect(question.id, option)}
                    className="sr-only"
                  />
                  <div className={`w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center ${
                    answers[question.id] === option
                      ? 'border-blue-500 bg-blue-500'
                      : 'border-gray-300'
                  }`}>
                    {answers[question.id] === option && (
                      <div className="w-2 h-2 rounded-full bg-white"></div>
                    )}
                  </div>
                  <span className="text-gray-900">{option}</span>
                </label>
              ))}
            </div>
          )}
          
          {question?.question_type === 'multiple_choice' && (!question?.options || !Array.isArray(question.options)) && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">Error: Question options not properly loaded</p>
              <p className="text-red-600 text-sm mt-1">Options data: {JSON.stringify(question?.options)}</p>
            </div>
          )}
        </div>

        {/* Answer requirement notice */}
        {!answers[questions[currentQuestion]?.id] && (
          <div className="mb-4 p-4 bg-red-50 border-2 border-red-300 rounded-lg animate-pulse">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
              <p className="text-sm font-medium text-red-800">
                You must select an answer before proceeding to the next question
              </p>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={handlePreviousQuestion}
            disabled={currentQuestion === 0}
            className="btn-secondary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>

          <div className="flex space-x-4">
            {currentQuestion === questions.length - 1 ? (
              <button
                onClick={() => {
                  const unansweredQuestions = questions.filter(q => !answers[q.id]);
                  if (unansweredQuestions.length > 0) {
                    toast.error(`Please answer all questions before submitting. ${unansweredQuestions.length} questions remaining.`);
                    return;
                  }
                  handleSubmitAssessment();
                }}
                disabled={submitting}
                className={`flex items-center space-x-2 px-4 py-2 rounded transition-colors ${
                  submitting
                    ? 'bg-gray-400 text-white cursor-not-allowed'
                    : questions.filter(q => !answers[q.id]).length > 0
                    ? 'bg-red-600 text-white hover:bg-red-700'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {submitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Submitting...</span>
                  </>
                ) : questions.filter(q => !answers[q.id]).length > 0 ? (
                  <>
                    <AlertCircle className="w-4 h-4" />
                    <span>Answer {questions.filter(q => !answers[q.id]).length} More</span>
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    <span>Submit Assessment</span>
                  </>
                )}
              </button>
            ) : (
              <button
                onClick={handleNextQuestion}
                disabled={!answers[questions[currentQuestion]?.id]}
                title={!answers[questions[currentQuestion]?.id] ? "Please select an answer first" : "Proceed to next question"}
                className={`flex items-center space-x-2 px-4 py-2 rounded transition-colors ${
                  !answers[questions[currentQuestion]?.id]
                    ? 'bg-gray-400 text-white cursor-not-allowed opacity-50'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                <span>{!answers[questions[currentQuestion]?.id] ? 'Select Answer First' : 'Next'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Assessment Info */}
        {userProfile && (
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">Assessment Personalized for You</h3>
            <p className="text-blue-800 text-sm">
              Based on your profile, this assessment focuses on: {userProfile.interests?.join(', ')} 
              at {userProfile.skill_level} level
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AssessmentTaking;