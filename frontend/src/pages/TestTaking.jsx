import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  Clock, 
  CheckCircle, 
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  Flag,
  Award,
  Download
} from 'lucide-react';
import toast from 'react-hot-toast';

const TestTaking = () => {
  const { courseId, moduleId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [test, setTest] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [testStarted, setTestStarted] = useState(false);
  const [testCompleted, setTestCompleted] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [attemptId, setAttemptId] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const isModuleTest = !!moduleId;
  const isFinalTest = location.pathname.includes('/final-test');

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    if (testStarted && timeRemaining > 0) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            handleSubmitTest();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      
      return () => clearInterval(timer);
    }
  }, [testStarted, timeRemaining]);

  // Load test data on component mount
  useEffect(() => {
    if (user && !testStarted && !testCompleted) {
      loadTestData();
    }
  }, [user]);

  const loadTestData = async () => {
    try {
      setLoading(true);
      let response;
      let testType = 'general';
      
      console.log('Loading test data...');
      console.log('isModuleTest:', isModuleTest, 'isFinalTest:', isFinalTest);
      console.log('moduleId:', moduleId, 'courseId:', courseId);
      
      // Try to load the appropriate test type with fallbacks
      if (isModuleTest && moduleId) {
        console.log('Loading module test for module:', moduleId);
        testType = 'module';
        try {
          response = await api.get(`/tests/module-test/${moduleId}`);
          console.log('Module test loaded successfully');
        } catch (moduleError) {
          console.log('Module test failed, falling back to simple test:', moduleError.message);
          response = await api.get('/tests/simple-test');
          testType = 'simple';
        }
      } else if (isFinalTest && courseId) {
        console.log('Loading final test for course:', courseId);
        testType = 'course_final';
        try {
          response = await api.get(`/tests/course/${courseId}/final-test`);
          console.log('Course final test loaded successfully');
        } catch (finalError) {
          console.log('Course final test failed, trying general final test:', finalError.message);
          try {
            response = await api.get('/tests/final-assessment');
            testType = 'final';
            console.log('General final test loaded successfully');
          } catch (generalFinalError) {
            console.log('All final tests failed, falling back to simple test:', generalFinalError.message);
            response = await api.get('/tests/simple-test');
            testType = 'simple';
          }
        }
      } else {
        console.log('Loading general assessment...');
        testType = 'assessment';
        try {
          response = await api.get('/tests/initial-assessment');
          console.log('Initial assessment loaded successfully');
        } catch (assessmentError) {
          console.log('Initial assessment failed, trying simple test:', assessmentError.message);
          response = await api.get('/tests/simple-test');
          testType = 'simple';
        }
      }
      
      console.log('API Response:', response?.data);
      
      if (response && response.data && response.data.success) {
        const testData = response.data.test || response.data.assessment;
        console.log('Test data received:', testData);
        
        if (!testData) {
          throw new Error('No test data received from server');
        }
        
        if (!testData.questions || !Array.isArray(testData.questions) || testData.questions.length === 0) {
          throw new Error('No questions available for this test');
        }
        
        // Normalize test data structure
        const normalizedTest = {
          test_title: testData.test_title || testData.title || `${testType.charAt(0).toUpperCase() + testType.slice(1)} Test`,
          duration_minutes: testData.time_limit_minutes || testData.duration_minutes || 30,
          questions: testData.questions,
          attempt_id: testData.attempt_id || `${testType}_${Date.now()}`,
          test_type: testType
        };
        
        setTest(normalizedTest);
        setAttemptId(normalizedTest.attempt_id);
        console.log('Test loaded successfully:', {
          title: normalizedTest.test_title,
          questions: normalizedTest.questions.length,
          duration: normalizedTest.duration_minutes,
          type: testType
        });
      } else {
        console.error('Invalid response structure:', response?.data);
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Failed to load test data:', error);
      const errorMessage = error.response?.data?.message || error.message || 'Failed to load test';
      toast.error(errorMessage);
      
      // Don't navigate away immediately, show error state instead
      setTest(null);
    } finally {
      setLoading(false);
    }
  };

  const startTest = async () => {
    if (!test || !test.questions || test.questions.length === 0) {
      toast.error('No test data available');
      return;
    }
    
    try {
      // Start the test timer and mark as started
      setTimeRemaining(test.duration_minutes * 60);
      setTestStarted(true);
      toast.success('Test started! Good luck!');
      
      // If this is a formal test (module or final), notify the backend
      if (isModuleTest || isFinalTest) {
        const endpoint = isModuleTest ? '/tests/module/start' : '/tests/final/start';
        const payload = isModuleTest ? { module_id: moduleId } : { course_id: courseId };
        
        try {
          await api.post(endpoint, payload);
        } catch (error) {
          console.warn('Failed to notify backend of test start:', error);
          // Don't fail the test start if backend notification fails
        }
      }
    } catch (error) {
      console.error('Test start error:', error);
      toast.error('Failed to start test');
    }
  };

  const handleAnswerChange = (questionId, answer, autoAdvance = false) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
    
    // Auto-save answer locally (no API call during test)
    console.log(`Answer saved for question ${questionId}: ${answer}`);
    
    // Auto-advance to next question for MCQ if enabled
    if (autoAdvance && currentQuestionIndex < test.questions.length - 1) {
      setTimeout(() => {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
        toast.success('Answer saved! Moving to next question...');
      }, 800);
    }
  };

  const handleSubmitTest = async () => {
    if (submitting) return;
    
    // Final validation - ensure all questions are answered
    const unansweredQuestions = test.questions.filter(q => !answers[q.id]);
    if (unansweredQuestions.length > 0) {
      toast.error(`Cannot submit test. Please answer all ${unansweredQuestions.length} remaining questions.`);
      return;
    }
    
    setSubmitting(true);
    try {
      // Submit all answers at once
      const submitData = {
        attempt_id: attemptId,
        answers: answers,
        test_type: isModuleTest ? 'module' : isFinalTest ? 'course_final' : 'final',
        time_taken_minutes: Math.round((test.duration_minutes * 60 - timeRemaining) / 60)
      };
      
      // Add module_id for module tests
      if (isModuleTest && moduleId) {
        submitData.module_id = moduleId;
      }
      
      // Add course_id for final tests
      if (isFinalTest && courseId) {
        submitData.course_id = courseId;
      }
      
      const response = await api.post('/tests/complete', submitData);
      
      if (response.data.success) {
        setTestResults(response.data.results);
        setTestCompleted(true);
        
        const score = response.data.results.score_percentage;
        const passed = response.data.results.passed; // Use backend determination
        
        // Show appropriate message based on score and pass requirement
        if (passed && score === 100 && isFinalTest) {
          if (response.data.results.certificate_generated) {
            toast.success('🏆 Perfect score! AI Certificate generated!');
          } else {
            toast.success('🏆 Perfect score achieved!');
          }
        } else if (passed && score >= 90) {
          toast.success(`🎉 Excellent! You scored ${score}% and passed!`);
        } else if (passed && score >= 80) {
          toast.success(`✅ Great job! You scored ${score}% and passed!`);
        } else if (passed) {
          toast.success(`✅ You passed with ${score}%!`);
        } else {
          toast.error(`❌ Test not passed. You scored ${score}% but need 60% to pass. Please try again.`);
        }
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to submit test');
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

  const getTimeColor = () => {
    if (timeRemaining < 300) return 'text-red-600'; // Less than 5 minutes
    if (timeRemaining < 600) return 'text-yellow-600'; // Less than 10 minutes
    return 'text-green-600';
  };

  if (loading) {
    return <LoadingSpinner text="Loading test..." />;
  }

  if (!test) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Test Not Available</h2>
            <p className="text-gray-600 mb-6">Unable to load test data. Please try again later.</p>
            <button
              onClick={() => navigate(-1)}
              className="btn-primary"
            >
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!testStarted) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back</span>
          </button>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <div className="mb-6">
              <Flag className="w-16 h-16 text-blue-600 mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                {isModuleTest ? 'Module Test' : 'Final Examination'}
              </h1>
              <p className="text-gray-600">
                {isModuleTest 
                  ? 'Test your knowledge of this module'
                  : 'Comprehensive final test covering all course material'
                }
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
              <h3 className="font-semibold text-blue-900 mb-4">⚠️ Important Test Rules</h3>
              <div className="text-left space-y-2 text-blue-800">
                <p>• <strong>Answer ALL questions:</strong> You must answer every question to submit</p>
                <p>• <strong>No skipping:</strong> Select an answer before going to next question</p>
                <p>• <strong>60% minimum:</strong> You need at least 60% to pass the test</p>
                <p>• <strong>No answers shown:</strong> Correct answers are not revealed during test</p>
                <p>• <strong>Submit once:</strong> Review all answers before final submission</p>
                <p>• <strong>Time limit:</strong> {isModuleTest ? '30' : '90'} minutes - auto-submit when time expires</p>
                <p>• {isModuleTest ? 'Unlimited attempts for module tests' : '🏆 Achieve 100% on final test for AI certificate'}</p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-6 text-sm">
              <div className="bg-gray-50 p-4 rounded-lg">
                <Clock className="w-6 h-6 text-gray-600 mx-auto mb-2" />
                <p className="font-medium text-gray-900">Duration</p>
                <p className="text-gray-600">{isModuleTest ? '30' : '90'} minutes</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <CheckCircle className="w-6 h-6 text-gray-600 mx-auto mb-2" />
                <p className="font-medium text-gray-900">Questions</p>
                <p className="text-gray-600">{isModuleTest ? '5' : '15'} questions</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <CheckCircle className="w-6 h-6 text-gray-600 mx-auto mb-2" />
                <p className="font-medium text-gray-900">Passing Score</p>
                <p className="text-gray-600">60%</p>
              </div>
            </div>

            <div className="space-y-4">
              <button
                onClick={startTest}
                className="btn-primary text-lg px-8 py-3"
              >
                Start Test
              </button>
              
              <button
                onClick={async () => {
                  try {
                    const response = await api.get('/tests/debug/questions');
                    console.log('Debug response:', response.data);
                    toast.success(`Found ${response.data.total_questions} questions in database`);
                  } catch (error) {
                    console.error('Debug error:', error);
                    toast.error('Debug failed');
                  }
                }}
                className="block mx-auto text-sm text-gray-600 hover:text-gray-900"
              >
                Debug: Check Questions
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (testCompleted && testResults) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <div className="mb-6">
              {testResults.passed ? (
                <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
              ) : (
                <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
              )}
              
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Test {testResults.passed ? 'Passed!' : 'Not Passed'}
              </h1>
              
              <p className="text-gray-600 mb-6">
                {testResults.passed 
                  ? 'Congratulations! You have successfully completed the test.'
                  : 'You need 60% to pass. Please review the material and try again.'
                }
              </p>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-8">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-2xl font-bold text-gray-900">
                  {testResults.score_percentage.toFixed(1)}%
                </p>
                <p className="text-gray-600">Your Score</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-2xl font-bold text-gray-900">
                  {testResults.correct_answers}
                </p>
                <p className="text-gray-600">Correct Answers</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-2xl font-bold text-gray-900">
                  {testResults.total_questions}
                </p>
                <p className="text-gray-600">Total Questions</p>
              </div>
            </div>

            {/* Certificate Generation - Only for 100% score on final test */}
            {testResults.passed && isFinalTest && testResults.score_percentage === 100 && testResults.certificate_generated && (
              <div className="bg-gradient-to-r from-yellow-50 to-green-50 border-2 border-yellow-300 rounded-lg p-6 mb-6">
                <div className="text-center">
                  <Award className="w-16 h-16 text-yellow-600 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-yellow-900 mb-2">
                    🏆 Perfect Score Certificate Generated! 🏆
                  </h3>
                  <p className="text-yellow-800 mb-2">
                    Congratulations on achieving a perfect 100% score!
                  </p>
                  <p className="text-green-800 mb-4">
                    Your AI-generated certificate with perfect alignment is ready for download.
                  </p>
                  <div className="bg-white rounded-lg p-3 mb-4">
                    <p className="text-sm text-gray-600">Certificate Number:</p>
                    <p className="font-mono text-sm font-bold text-gray-900">
                      {testResults.certificate_data?.certificate_number}
                    </p>
                  </div>
                  <button
                    onClick={() => window.open(testResults.certificate_data?.download_url, '_blank')}
                    className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-yellow-600 to-green-600 text-white rounded-lg hover:from-yellow-700 hover:to-green-700 font-semibold"
                  >
                    <Download className="w-5 h-5" />
                    <span>Download Perfect Score Certificate</span>
                  </button>
                </div>
              </div>
            )}
            
            {/* Show message for passed but not perfect score */}
            {testResults.passed && isFinalTest && testResults.score_percentage < 100 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                <Award className="w-12 h-12 text-blue-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-blue-900 mb-2">
                  Test Passed! 🎉
                </h3>
                <p className="text-blue-800 mb-4">
                  Great job! You passed the final test with {testResults.score_percentage}%.
                </p>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-yellow-800 font-medium mb-2">
                    🏆 Want the AI-Generated Certificate?
                  </p>
                  <p className="text-yellow-700 text-sm">
                    Achieve a perfect 100% score to unlock the special AI-generated certificate with premium design and proper alignment!
                  </p>
                </div>
              </div>
            )}
            


            <div className="space-y-3">
              {/* Show different options based on test result and type */}
              {testResults.passed && isModuleTest && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                  <h3 className="font-semibold text-green-900 mb-2">🎉 Module Test Passed!</h3>
                  <p className="text-green-800 text-sm mb-3">
                    Great job! You scored {testResults.score_percentage}% and passed this module.
                  </p>
                  <div className="space-y-3">
                    <div className="bg-white border border-green-300 rounded-lg p-3">
                      <h4 className="font-medium text-green-900 mb-2">Choose your next step:</h4>
                      <div className="space-y-2">
                        <button
                          onClick={() => navigate(`/courses/${courseId}`, { 
                            state: { 
                              testResult: {
                                moduleId: moduleId,
                                passed: testResults.passed,
                                score: testResults.score_percentage,
                                completedAt: new Date().toISOString(),
                                action: 'continue_next_module'
                              }
                            }
                          })}
                          className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 font-medium"
                        >
                          📚 Continue to Next Module
                        </button>
                        <button
                          onClick={() => navigate(`/courses/${courseId}`, { 
                            state: { 
                              testResult: {
                                moduleId: moduleId,
                                passed: testResults.passed,
                                score: testResults.score_percentage,
                                completedAt: new Date().toISOString(),
                                action: 'take_final_test'
                              }
                            }
                          })}
                          className="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 font-medium"
                        >
                          🎯 Take Final Test & Get Certificate
                        </button>
                      </div>
                      <p className="text-xs text-green-700 text-center mt-2">
                        You can continue learning or test your overall knowledge
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              {testResults.passed && isFinalTest && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                  <h3 className="font-semibold text-blue-900 mb-2">🎓 Final Test Passed!</h3>
                  <p className="text-blue-800 text-sm mb-3">
                    Congratulations! You scored {testResults.score_percentage}% and completed the course.
                  </p>
                  {testResults.score_percentage >= 60 && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-3">
                      <p className="text-green-800 text-sm font-medium mb-2">
                        🏆 You've earned your AI-generated certificate!
                      </p>
                      {testResults.certificate_data && (
                        <div className="space-y-2">
                          <p className="text-xs text-green-700">
                            Certificate #{testResults.certificate_data.certificate_number}
                          </p>
                          <button
                            onClick={() => window.open(`/api${testResults.certificate_data.download_url}`, '_blank')}
                            className="w-full px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm font-medium"
                          >
                            📄 Download Certificate
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
              
              <button
                onClick={() => navigate(`/courses/${courseId}`, { 
                  state: { 
                    testResult: {
                      moduleId: moduleId,
                      passed: testResults.passed,
                      score: testResults.score_percentage,
                      completedAt: new Date().toISOString(),
                      testType: isModuleTest ? 'module' : 'final'
                    }
                  }
                })}
                className="w-full btn-primary"
              >
                {testResults.passed 
                  ? (isModuleTest ? 'Continue to Next Module' : 'View Certificate') 
                  : 'Back to Course'
                }
              </button>
              
              {!testResults.passed && (
                <div className="space-y-2">
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="text-red-800 text-sm">
                      You need 60% to pass. Review the material and try again.
                    </p>
                  </div>
                  <button
                    onClick={() => window.location.reload()}
                    className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
                  >
                    Try Again
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!test || !test.questions || test.questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <LoadingSpinner text="Loading questions..." />
            <div className="mt-4">
              <button
                onClick={startTest}
                className="btn-secondary"
              >
                Retry Loading Test
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const currentQuestion = test.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / test.questions.length) * 100;

  return (
    <div className="min-h-screen bg-gray-50 py-4">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-lg font-semibold text-gray-900">
                {test.test_title}
              </h1>
              <p className="text-sm text-gray-600">
                Question {currentQuestionIndex + 1} of {test.questions.length}
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 ${getTimeColor()}`}>
                <Clock className="w-4 h-4" />
                <span className="font-mono font-semibold">
                  {formatTime(timeRemaining)}
                </span>
              </div>
              
              <button
                onClick={() => {
                  const unansweredQuestions = test.questions.filter(q => !answers[q.id]);
                  if (unansweredQuestions.length > 0) {
                    toast.error(`Please answer all questions before submitting. ${unansweredQuestions.length} questions remaining.`);
                    return;
                  }
                  handleSubmitTest();
                }}
                disabled={submitting}
                className={`px-4 py-2 rounded transition-colors ${
                  submitting
                    ? 'bg-gray-400 text-white cursor-not-allowed'
                    : test.questions.filter(q => !answers[q.id]).length > 0
                    ? 'bg-red-600 text-white hover:bg-red-700'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {submitting 
                  ? 'Submitting...' 
                  : test.questions.filter(q => !answers[q.id]).length > 0
                  ? `Answer ${test.questions.filter(q => !answers[q.id]).length} More`
                  : 'Submit Test'
                }
              </button>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Question */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="mb-6">
            <h2 className="text-xl font-medium text-gray-900 mb-4">
              {currentQuestion.question_text}
            </h2>
            
            {currentQuestion.question_type === 'multiple_choice' && currentQuestion.options && Array.isArray(currentQuestion.options) && (
              <div className="space-y-3">
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>📝 MCQ Rule:</strong> Select an option to automatically proceed to the next question.
                  </p>
                </div>
                {currentQuestion.options.map((option, index) => (
                  <label 
                    key={index} 
                    className={`flex items-center space-x-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                      answers[currentQuestion.id] === option
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <input
                      type="radio"
                      name={`question-${currentQuestion.id}`}
                      value={option}
                      checked={answers[currentQuestion.id] === option}
                      onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value, true)}
                      className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-gray-900 flex-1">{option}</span>
                    {answers[currentQuestion.id] === option && (
                      <div className="text-green-600">
                        <CheckCircle className="w-5 h-5" />
                      </div>
                    )}
                  </label>
                ))}
                {answers[currentQuestion.id] && (
                  <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm text-green-800">
                      ✅ Answer selected! Moving to next question...
                    </p>
                  </div>
                )}
              </div>
            )}
            
            {currentQuestion.question_type === 'multiple_choice' && (!currentQuestion.options || !Array.isArray(currentQuestion.options)) && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800">Error: Question options not properly loaded</p>
                <p className="text-red-600 text-sm mt-1">Options data: {JSON.stringify(currentQuestion.options)}</p>
              </div>
            )}
            
            {currentQuestion.question_type === 'coding' && (
              <div className="space-y-4">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-sm text-yellow-800">
                    <strong>💻 Coding Question:</strong> Write your solution in the code editor below. Make sure to test your code logic before submitting.
                  </p>
                </div>
                
                {/* Language Selector */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Programming Language
                  </label>
                  <select
                    value={answers[currentQuestion.id]?.language || 'python'}
                    onChange={(e) => {
                      const currentAnswer = answers[currentQuestion.id];
                      setAnswers(prev => ({
                        ...prev,
                        [currentQuestion.id]: {
                          code: currentAnswer?.code || '',
                          language: e.target.value
                        }
                      }));
                    }}
                    className="block w-48 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="java">Java</option>
                    <option value="cpp">C++</option>
                    <option value="c">C</option>
                  </select>
                </div>
                
                {/* Code Editor */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your Solution
                  </label>
                  <textarea
                    value={answers[currentQuestion.id]?.code || answers[currentQuestion.id] || ''}
                    onChange={(e) => {
                      const currentAnswer = answers[currentQuestion.id];
                      if (typeof currentAnswer === 'object') {
                        setAnswers(prev => ({
                          ...prev,
                          [currentQuestion.id]: {
                            ...currentAnswer,
                            code: e.target.value
                          }
                        }));
                      } else {
                        setAnswers(prev => ({
                          ...prev,
                          [currentQuestion.id]: {
                            code: e.target.value,
                            language: 'python'
                          }
                        }));
                      }
                    }}
                    placeholder={`Write your ${answers[currentQuestion.id]?.language || 'python'} code here...`}
                    className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                    style={{ fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace' }}
                  />
                </div>
                
                {/* Sample Inputs if available */}
                {currentQuestion.sample_inputs && currentQuestion.sample_inputs.length > 0 && (
                  <div className="bg-gray-50 p-4 rounded-md">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Sample Inputs:</h4>
                    {currentQuestion.sample_inputs.map((input, index) => (
                      <div key={index} className="mb-2">
                        <span className="text-sm text-gray-600">Input {index + 1}:</span>
                        <code className="ml-2 px-2 py-1 bg-white rounded text-sm font-mono">
                          {input}
                        </code>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            {currentQuestion.question_type === 'essay' && (
              <div>
                <textarea
                  value={answers[currentQuestion.id] || ''}
                  onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                  placeholder="Write your answer here..."
                  className="w-full h-32 p-4 border border-gray-300 rounded-lg"
                />
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
            disabled={currentQuestionIndex === 0}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>
          
          <div className="flex items-center space-x-2">
            {test.questions.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentQuestionIndex(index)}
                className={`w-8 h-8 rounded text-sm font-medium ${
                  index === currentQuestionIndex
                    ? 'bg-blue-600 text-white'
                    : answers[test.questions[index].id]
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>
          
          {/* Next button - disabled if current question not answered */}
          <button
            onClick={() => {
              const currentQuestionId = test.questions[currentQuestionIndex].id;
              if (!answers[currentQuestionId]) {
                toast.error('Please select an answer before proceeding to the next question');
                return;
              }
              setCurrentQuestionIndex(Math.min(test.questions.length - 1, currentQuestionIndex + 1));
            }}
            disabled={currentQuestionIndex === test.questions.length - 1}
            className={`flex items-center space-x-2 px-4 py-2 border rounded transition-colors ${
              currentQuestionIndex === test.questions.length - 1
                ? 'border-gray-300 text-gray-400 cursor-not-allowed opacity-50'
                : !answers[test.questions[currentQuestionIndex].id]
                ? 'border-red-300 text-red-600 bg-red-50'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <span>Next</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
        
        {/* Answer requirement notice */}
        {!answers[test.questions[currentQuestionIndex].id] && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              ⚠️ Please select an answer to proceed to the next question
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TestTaking;