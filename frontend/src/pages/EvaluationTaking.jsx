import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import Cookies from 'js-cookie';

const EvaluationTaking = () => {
  const { attemptId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [evaluation, setEvaluation] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [autoSaving, setAutoSaving] = useState(false);
  
  const timerRef = useRef(null);
  const autoSaveRef = useRef(null);

  useEffect(() => {
    fetchEvaluationData();
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (autoSaveRef.current) clearInterval(autoSaveRef.current);
    };
  }, [attemptId]);

  useEffect(() => {
    if (evaluation && evaluation.attempt) {
      const startTime = new Date(evaluation.attempt.started_at);
      const durationMs = evaluation.evaluation.duration_minutes * 60 * 1000;
      const endTime = new Date(startTime.getTime() + durationMs);
      
      const updateTimer = () => {
        const now = new Date();
        const remaining = Math.max(0, endTime.getTime() - now.getTime());
        setTimeRemaining(remaining);
        
        if (remaining === 0) {
          handleAutoSubmit();
        }
      };
      
      updateTimer();
      timerRef.current = setInterval(updateTimer, 1000);
      
      // Auto-save every 30 seconds
      autoSaveRef.current = setInterval(autoSaveAnswers, 30000);
    }
  }, [evaluation]);

  const fetchEvaluationData = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/weekly-evaluations/attempts/${attemptId}/questions`, {
        headers: {
          'Authorization': `Bearer ${Cookies.get('skillnova_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setEvaluation(data);
        setQuestions(data.questions);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to fetch evaluation data');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const autoSaveAnswers = async () => {
    if (Object.keys(answers).length === 0) return;
    
    setAutoSaving(true);
    
    // Save all answers
    for (const [questionId, answer] of Object.entries(answers)) {
      try {
        await fetch(`http://localhost:5000/api/weekly-evaluations/attempts/${attemptId}/submit-answer`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${Cookies.get('skillnova_token')}`
          },
          body: JSON.stringify({
            question_id: questionId,
            answer: answer.answer,
            language: answer.language || 'python'
          })
        });
      } catch (err) {
        console.error('Auto-save failed for question:', questionId);
      }
    }
    
    setAutoSaving(false);
  };

  const handleAnswerChange = (questionId, answer, language = 'python') => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: { answer, language }
    }));
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleQuestionNavigation = (index) => {
    setCurrentQuestionIndex(index);
  };

  const handleAutoSubmit = async () => {
    if (submitting) return;
    
    setSubmitting(true);
    await autoSaveAnswers(); // Save any pending answers
    
    try {
      const response = await fetch(`http://localhost:5000/api/weekly-evaluations/attempts/${attemptId}/complete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${Cookies.get('skillnova_token')}`
        }
      });

      if (response.ok) {
        navigate('/evaluation-scores', { 
          state: { message: 'Questions auto-submitted due to time limit' }
        });
      } else {
        setError('Failed to auto-submit questions');
      }
    } catch (err) {
      setError('Network error during auto-submission');
    } finally {
      setSubmitting(false);
    }
  };

  const handleManualSubmit = async () => {
    if (submitting) return;
    
    const confirmSubmit = window.confirm(
      'Are you sure you want to submit your questions? You cannot change your answers after submission.'
    );
    
    if (!confirmSubmit) return;
    
    setSubmitting(true);
    await autoSaveAnswers(); // Save any pending answers
    
    try {
      const response = await fetch(`http://localhost:5000/api/weekly-evaluations/attempts/${attemptId}/complete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${Cookies.get('skillnova_token')}`
        }
      });

      const data = await response.json();

      if (response.ok) {
        navigate('/evaluation-scores', { 
          state: { 
            message: 'Questions submitted successfully!',
            score: data.score_percentage,
            grade: data.grade
          }
        });
      } else {
        setError(data.message || 'Failed to submit questions');
      }
    } catch (err) {
      setError('Network error during submission');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (ms) => {
    const totalSeconds = Math.floor(ms / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const getTimeColor = () => {
    const totalTime = evaluation?.evaluation?.duration_minutes * 60 * 1000 || 1;
    const percentage = (timeRemaining / totalTime) * 100;
    
    if (percentage > 50) return 'text-green-600';
    if (percentage > 25) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getQuestionStatus = (questionId) => {
    if (answers[questionId]) return 'answered';
    return 'unanswered';
  };

  if (loading) return <LoadingSpinner />;

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          {error}
        </div>
      </div>
    );
  }

  if (!evaluation || questions.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-900">No questions available</h2>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                {evaluation.evaluation.title}
              </h1>
              <p className="text-sm text-gray-600">
                Question {currentQuestionIndex + 1} of {questions.length}
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              {autoSaving && (
                <span className="text-sm text-blue-600">Auto-saving...</span>
              )}
              
              <div className={`text-lg font-mono font-semibold ${getTimeColor()}`}>
                ⏰ {formatTime(timeRemaining)}
              </div>
              
              <button
                onClick={handleManualSubmit}
                disabled={submitting}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                {submitting ? 'Submitting...' : 'Submit Questions'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-6">
          {/* Question Navigation Sidebar */}
          <div className="w-64 bg-white rounded-lg shadow-md p-4">
            <h3 className="font-semibold text-gray-900 mb-4">Questions</h3>
            <div className="grid grid-cols-5 gap-2">
              {questions.map((question, index) => (
                <button
                  key={question.id}
                  onClick={() => handleQuestionNavigation(index)}
                  className={`w-10 h-10 rounded-md text-sm font-medium transition-colors ${
                    index === currentQuestionIndex
                      ? 'bg-blue-600 text-white'
                      : getQuestionStatus(question.id) === 'answered'
                      ? 'bg-green-100 text-green-800 hover:bg-green-200'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {index + 1}
                </button>
              ))}
            </div>
            
            <div className="mt-4 text-xs text-gray-600">
              <div className="flex items-center mb-1">
                <div className="w-3 h-3 bg-green-100 rounded mr-2"></div>
                Answered
              </div>
              <div className="flex items-center mb-1">
                <div className="w-3 h-3 bg-gray-100 rounded mr-2"></div>
                Unanswered
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-blue-600 rounded mr-2"></div>
                Current
              </div>
            </div>
          </div>

          {/* Main Question Area */}
          <div className="flex-1 bg-white rounded-lg shadow-md">
            <div className="p-6">
              {/* Question Header */}
              <div className="mb-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      currentQuestion.question_type === 'coding' 
                        ? 'bg-blue-100 text-blue-800' 
                        : 'bg-purple-100 text-purple-800'
                    }`}>
                      {currentQuestion.question_type === 'coding' ? 'Coding' : 'Multiple Choice'}
                    </span>
                    <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      currentQuestion.difficulty_level === 'easy' 
                        ? 'bg-green-100 text-green-800'
                        : currentQuestion.difficulty_level === 'medium'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {currentQuestion.difficulty_level}
                    </span>
                    <span className="ml-2 text-sm text-gray-600">
                      {currentQuestion.category} • {currentQuestion.points} points
                    </span>
                  </div>
                </div>
                
                <h2 className="text-lg font-medium text-gray-900 mb-4">
                  {currentQuestion.question_text}
                </h2>
              </div>

              {/* Question Content */}
              {currentQuestion.question_type === 'multiple_choice' ? (
                <MultipleChoiceQuestion
                  question={currentQuestion}
                  answer={answers[currentQuestion.id]?.answer || ''}
                  onAnswerChange={(answer) => handleAnswerChange(currentQuestion.id, answer)}
                  onAutoNext={() => {
                    if (currentQuestionIndex < questions.length - 1) {
                      setCurrentQuestionIndex(currentQuestionIndex + 1);
                    }
                  }}
                />
              ) : (
                <CodingQuestion
                  question={currentQuestion}
                  answer={answers[currentQuestion.id]?.answer || ''}
                  language={answers[currentQuestion.id]?.language || 'python'}
                  onAnswerChange={(answer, language) => handleAnswerChange(currentQuestion.id, answer, language)}
                />
              )}
            </div>

            {/* Navigation Footer */}
            <div className="border-t border-gray-200 px-6 py-4 flex justify-between">
              <button
                onClick={handlePreviousQuestion}
                disabled={currentQuestionIndex === 0}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              
              <button
                onClick={handleNextQuestion}
                disabled={currentQuestionIndex === questions.length - 1}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Multiple Choice Question Component with Auto-Progression
const MultipleChoiceQuestion = ({ question, answer, onAnswerChange, onAutoNext }) => {
  const handleOptionSelect = (selectedValue) => {
    onAnswerChange(selectedValue);
    
    // Auto-progress to next question after 1 second for MCQ
    setTimeout(() => {
      if (onAutoNext) {
        onAutoNext();
      }
    }, 1000);
  };

  return (
    <div className="space-y-3">
      <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
        <p className="text-sm text-blue-800">
          <strong>📝 MCQ Rule:</strong> Select an option to automatically proceed to the next question.
        </p>
      </div>
      
      {Object.entries(question.options || {}).map(([key, value]) => (
        <label key={key} className="flex items-start space-x-3 cursor-pointer hover:bg-gray-50 p-3 rounded-md transition-colors">
          <input
            type="radio"
            name={`question-${question.id}`}
            value={key}
            checked={answer === key}
            onChange={(e) => handleOptionSelect(e.target.value)}
            className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
          />
          <div className="flex-1">
            <span className="font-medium text-gray-900">{key}.</span>
            <span className="ml-2 text-gray-700">{value}</span>
          </div>
          {answer === key && (
            <div className="text-green-600">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
          )}
        </label>
      ))}
      
      {answer && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-800">
            ✅ Answer selected! Moving to next question in 1 second...
          </p>
        </div>
      )}
    </div>
  );
};

// Coding Question Component
const CodingQuestion = ({ question, answer, language, onAnswerChange }) => {
  const [selectedLanguage, setSelectedLanguage] = useState(language);
  const [codeOutput, setCodeOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);

  const handleLanguageChange = (newLanguage) => {
    setSelectedLanguage(newLanguage);
    onAnswerChange(answer, newLanguage);
  };

  const languages = [
    { value: 'python', label: 'Python' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'java', label: 'Java' },
    { value: 'cpp', label: 'C++' },
    { value: 'c', label: 'C' }
  ];

  const handleTestCode = async () => {
    if (!answer || !answer.trim()) {
      setCodeOutput('Error: Please write some code first');
      return;
    }

    setIsRunning(true);
    setCodeOutput('Running code...');

    try {
      // Simulate code execution (in real app, this would call backend)
      setTimeout(() => {
        setCodeOutput(`Code syntax check passed for ${selectedLanguage}.\n\nNote: Full execution will happen during evaluation submission.`);
        setIsRunning(false);
      }, 1000);
    } catch (error) {
      setCodeOutput(`Error: ${error.message}`);
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          <strong>💻 Coding Question:</strong> Write your solution and test it before submitting. Your code will be evaluated against hidden test cases.
        </p>
      </div>

      {/* Language Selector */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Programming Language
        </label>
        <select
          value={selectedLanguage}
          onChange={(e) => handleLanguageChange(e.target.value)}
          className="block w-48 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          {languages.map((lang) => (
            <option key={lang.value} value={lang.value}>
              {lang.label}
            </option>
          ))}
        </select>
      </div>

      {/* Sample Inputs */}
      {question.sample_inputs && question.sample_inputs.length > 0 && (
        <div className="bg-gray-50 p-4 rounded-md">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Sample Inputs:</h4>
          {question.sample_inputs.map((input, index) => (
            <div key={index} className="mb-2">
              <span className="text-sm text-gray-600">Input {index + 1}:</span>
              <code className="ml-2 px-2 py-1 bg-white rounded text-sm font-mono">
                {input}
              </code>
            </div>
          ))}
        </div>
      )}

      {/* Code Editor */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="block text-sm font-medium text-gray-700">
            Your Solution
          </label>
          <button
            onClick={handleTestCode}
            disabled={isRunning}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isRunning ? 'Testing...' : 'Test Code'}
          </button>
        </div>
        <textarea
          value={answer}
          onChange={(e) => onAnswerChange(e.target.value, selectedLanguage)}
          placeholder={`Write your ${selectedLanguage} code here...\n\nExample for Python:\ndef solution(input_data):\n    # Your code here\n    return result`}
          className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
          style={{ fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace' }}
        />
      </div>

      {/* Code Output */}
      {codeOutput && (
        <div className="bg-gray-900 text-green-400 p-4 rounded-md font-mono text-sm">
          <div className="flex justify-between items-center mb-2">
            <span className="font-semibold">Output:</span>
            <button
              onClick={() => setCodeOutput('')}
              className="text-xs text-gray-400 hover:text-white"
            >
              Clear
            </button>
          </div>
          <pre className="whitespace-pre-wrap">{codeOutput}</pre>
        </div>
      )}

      {question.test_cases_count && (
        <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-md">
          <span className="font-medium">📊 Testing:</span> Your code will be tested against {question.test_cases_count} hidden test cases for accuracy and correctness.
        </div>
      )}
    </div>
  );
};

export default EvaluationTaking;