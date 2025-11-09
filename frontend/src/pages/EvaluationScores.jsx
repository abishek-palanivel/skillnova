import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import Cookies from 'js-cookie';

const EvaluationScores = () => {
  const { user } = useAuth();
  const location = useLocation();
  const [scores, setScores] = useState([]);
  const [selectedScore, setSelectedScore] = useState(null);
  const [scoreDetails, setScoreDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchScores();
    
    // Show success message if redirected from evaluation submission
    if (location.state?.message) {
      setSuccess(location.state.message);
    }
    
    // Show instant score if just completed evaluation
    if (location.state?.instantScore) {
      setSelectedScore(location.state.instantScore);
    }
  }, []);

  const fetchScores = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/weekly-evaluations/my-scores', {
        headers: {
          'Authorization': `Bearer ${Cookies.get('skillnova_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setScores(data.scores);
      } else {
        setError('Failed to fetch scores');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchScoreDetails = async (scoreId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/weekly-evaluations/scores/${scoreId}/details`, {
        headers: {
          'Authorization': `Bearer ${Cookies.get('skillnova_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setScoreDetails(data);
        setSelectedScore(scoreId);
      } else {
        setError('Failed to fetch score details');
      }
    } catch (err) {
      setError('Network error occurred');
    }
  };

  const getGradeColor = (grade) => {
    if (['A+', 'A', 'A-'].includes(grade)) return 'text-green-600 bg-green-100';
    if (['B+', 'B', 'B-'].includes(grade)) return 'text-blue-600 bg-blue-100';
    if (['C+', 'C', 'C-'].includes(grade)) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getDecisionColor = (decision) => {
    switch (decision) {
      case 'selected': return 'text-green-600 bg-green-100';
      case 'rejected': return 'text-red-600 bg-red-100';
      case 'internship_offered': return 'text-blue-600 bg-blue-100';
      case 'scholarship_offered': return 'text-purple-600 bg-purple-100';
      default: return 'text-yellow-600 bg-yellow-100';
    }
  };

  const getDecisionIcon = (decision) => {
    switch (decision) {
      case 'selected': return '🎉';
      case 'rejected': return '📝';
      case 'internship_offered': return '🚀';
      case 'scholarship_offered': return '🎓';
      default: return '⏳';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Instant Score Display Component
  const InstantScoreDisplay = ({ score }) => (
    <div className="mb-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow-lg text-white p-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">🎉 Evaluation Completed!</h2>
        <p className="text-blue-100 mb-4">Your score is available instantly</p>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div className="bg-white bg-opacity-20 rounded-lg p-4">
            <div className="text-3xl font-bold">{score.score_percentage}%</div>
            <div className="text-sm text-blue-100">Overall Score</div>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-4">
            <div className="text-2xl font-bold">{score.grade}</div>
            <div className="text-sm text-blue-100">Grade</div>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-4">
            <div className="text-2xl font-bold">{score.coding_score}%</div>
            <div className="text-sm text-blue-100">Coding Score</div>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-4">
            <div className="text-2xl font-bold">{score.mcq_score}%</div>
            <div className="text-sm text-blue-100">MCQ Score</div>
          </div>
        </div>
        
        <div className="text-center">
          <p className="text-blue-100 mb-2">Points: {score.earned_points}/{score.total_points}</p>
          <p className="text-sm text-blue-200">Completed at: {new Date(score.completion_time).toLocaleString()}</p>
        </div>
      </div>
    </div>
  );

  if (loading) return <LoadingSpinner />;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Evaluation Scores</h1>
        <p className="mt-2 text-gray-600">
          View your weekly evaluation results and feedback
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
          {success}
        </div>
      )}

      {/* Instant Score Display */}
      {location.state?.instantScore && (
        <InstantScoreDisplay score={location.state.instantScore} />
      )}

      {scores.length === 0 ? (
        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          <div className="px-6 py-12 text-center">
            <div className="text-6xl mb-4">📊</div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              No Evaluation Scores Yet
            </h2>
            <p className="text-gray-600 mb-6">
              You haven't completed any weekly evaluations yet. Take your first evaluation to see your scores here.
            </p>
            <button
              onClick={() => window.location.href = '/weekly-evaluation'}
              className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors font-medium"
            >
              Take Evaluation
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Scores List */}
          <div className="lg:col-span-1">
            <div className="bg-white shadow-md rounded-lg overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Your Evaluations</h2>
              </div>
              <div className="divide-y divide-gray-200">
                {scores.map((score) => (
                  <div
                    key={score.id}
                    onClick={() => fetchScoreDetails(score.id)}
                    className={`px-6 py-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                      selectedScore === score.id ? 'bg-blue-50 border-r-4 border-blue-500' : ''
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-sm font-medium text-gray-900 truncate">
                        {score.evaluation.title}
                      </h3>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getGradeColor(score.grade)}`}>
                        {score.grade}
                      </span>
                    </div>
                    
                    <div className="text-sm text-gray-600 mb-2">
                      {formatDate(score.evaluation.scheduled_date)}
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-lg font-semibold text-gray-900">
                        {score.score_percentage}%
                      </span>
                      
                      {score.admin_decision && (
                        <span className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${getDecisionColor(score.admin_decision)}`}>
                          <span className="mr-1">{getDecisionIcon(score.admin_decision)}</span>
                          {score.admin_decision.replace('_', ' ').toUpperCase()}
                        </span>
                      )}
                    </div>
                    
                    <div className="mt-2 flex justify-between text-xs text-gray-500">
                      <span>Coding: {score.coding_score}%</span>
                      <span>MCQ: {score.mcq_score}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Score Details */}
          <div className="lg:col-span-2">
            {scoreDetails ? (
              <ScoreDetailsView scoreDetails={scoreDetails} />
            ) : (
              <div className="bg-white shadow-md rounded-lg overflow-hidden">
                <div className="px-6 py-12 text-center">
                  <div className="text-4xl mb-4">👈</div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Select an Evaluation
                  </h3>
                  <p className="text-gray-600">
                    Click on an evaluation from the list to view detailed results and feedback.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Score Details Component
const ScoreDetailsView = ({ scoreDetails }) => {
  const { score, evaluation, attempt, detailed_results } = scoreDetails;

  const getQuestionTypeIcon = (type) => {
    return type === 'coding' ? '💻' : '📝';
  };

  const getResultColor = (result) => {
    if (result.question_type === 'multiple_choice') {
      return result.correct ? 'text-green-600' : 'text-red-600';
    } else {
      const percentage = (result.points_earned / result.max_points) * 100;
      if (percentage >= 80) return 'text-green-600';
      if (percentage >= 60) return 'text-yellow-600';
      return 'text-red-600';
    }
  };

  return (
    <div className="bg-white shadow-md rounded-lg overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          {evaluation.title}
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{score.score_percentage}%</div>
            <div className="text-sm text-gray-600">Overall Score</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{score.grade}</div>
            <div className="text-sm text-gray-600">Grade</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{score.coding_score}%</div>
            <div className="text-sm text-gray-600">Coding</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{score.mcq_score}%</div>
            <div className="text-sm text-gray-600">MCQ</div>
          </div>
        </div>
      </div>

      {/* Admin Decision & Feedback */}
      {(score.admin_decision || score.admin_feedback) && (
        <div className="px-6 py-4 border-b border-gray-200">
          {score.admin_decision && (
            <div className="mb-3">
              <h3 className="text-sm font-medium text-gray-900 mb-2">Admin Decision</h3>
              <span className={`inline-flex items-center px-3 py-1 text-sm font-semibold rounded-full ${
                score.admin_decision === 'selected' ? 'bg-green-100 text-green-800' :
                score.admin_decision === 'rejected' ? 'bg-red-100 text-red-800' :
                score.admin_decision === 'internship_offered' ? 'bg-blue-100 text-blue-800' :
                score.admin_decision === 'scholarship_offered' ? 'bg-purple-100 text-purple-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {score.admin_decision === 'selected' && '🎉 Selected'}
                {score.admin_decision === 'rejected' && '📝 Not Selected'}
                {score.admin_decision === 'internship_offered' && '🚀 Internship Offered'}
                {score.admin_decision === 'scholarship_offered' && '🎓 Scholarship Offered'}
                {score.admin_decision === 'pending' && '⏳ Under Review'}
              </span>
            </div>
          )}
          
          {score.admin_feedback && (
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-2">Admin Feedback</h3>
              <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded">
                <p className="text-sm text-blue-800">{score.admin_feedback}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Attempt Info */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-900">Time Taken:</span>
            <span className="ml-2 text-gray-600">{attempt.time_taken_minutes} minutes</span>
          </div>
          <div>
            <span className="font-medium text-gray-900">Completed:</span>
            <span className="ml-2 text-gray-600">
              {new Date(attempt.completed_at).toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {/* Question Results */}
      <div className="px-6 py-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Question-by-Question Results</h3>
        <div className="space-y-4">
          {detailed_results.map((result, index) => (
            <QuestionResult key={index} result={result} index={index} />
          ))}
        </div>
      </div>
    </div>
  );
};

// Question Result Component
const QuestionResult = ({ result, index }) => {
  const [expanded, setExpanded] = useState(false);
  const { question, result: questionResult } = result;

  const getResultColor = () => {
    if (question.type === 'multiple_choice') {
      return questionResult.correct ? 'text-green-600' : 'text-red-600';
    } else {
      const percentage = (questionResult.points_earned / questionResult.max_points) * 100;
      if (percentage >= 80) return 'text-green-600';
      if (percentage >= 60) return 'text-yellow-600';
      return 'text-red-600';
    }
  };

  const getResultIcon = () => {
    if (question.type === 'multiple_choice') {
      return questionResult.correct ? '✅' : '❌';
    } else {
      const percentage = (questionResult.points_earned / questionResult.max_points) * 100;
      if (percentage >= 80) return '✅';
      if (percentage >= 60) return '⚠️';
      return '❌';
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div
        onClick={() => setExpanded(!expanded)}
        className="px-4 py-3 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
      >
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <span className="text-lg">{question.type === 'coding' ? '💻' : '📝'}</span>
            <div>
              <h4 className="font-medium text-gray-900">
                Question {index + 1} - {question.category}
              </h4>
              <p className="text-sm text-gray-600">
                {question.difficulty} • {question.points} points
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <div className={`text-lg font-semibold ${getResultColor()}`}>
                {getResultIcon()} {questionResult.points_earned}/{questionResult.max_points}
              </div>
              <div className="text-sm text-gray-600">
                {Math.round((questionResult.points_earned / questionResult.max_points) * 100)}%
              </div>
            </div>
            <span className="text-gray-400">
              {expanded ? '▼' : '▶'}
            </span>
          </div>
        </div>
      </div>

      {expanded && (
        <div className="px-4 py-3 border-t border-gray-200">
          <div className="mb-3">
            <h5 className="font-medium text-gray-900 mb-2">Question:</h5>
            <p className="text-gray-700">{question.text}</p>
          </div>

          {question.type === 'multiple_choice' ? (
            <div>
              {question.options && (
                <div className="mb-3">
                  <h5 className="font-medium text-gray-900 mb-2">Options:</h5>
                  <div className="space-y-1">
                    {Object.entries(question.options).map(([key, value]) => (
                      <div key={key} className={`p-2 rounded ${
                        key === question.correct_answer ? 'bg-green-100' :
                        key === questionResult.user_answer ? 'bg-red-100' : 'bg-gray-50'
                      }`}>
                        <span className="font-medium">{key}.</span> {value}
                        {key === question.correct_answer && <span className="ml-2 text-green-600">✓ Correct</span>}
                        {key === questionResult.user_answer && key !== question.correct_answer && (
                          <span className="ml-2 text-red-600">✗ Your Answer</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {question.explanation && (
                <div className="bg-blue-50 p-3 rounded">
                  <h5 className="font-medium text-blue-900 mb-1">Explanation:</h5>
                  <p className="text-blue-800 text-sm">{question.explanation}</p>
                </div>
              )}
            </div>
          ) : (
            <div>
              {questionResult.test_results && (
                <div className="mb-3">
                  <h5 className="font-medium text-gray-900 mb-2">Test Results:</h5>
                  <div className="space-y-2">
                    {questionResult.test_results.map((test, testIndex) => (
                      <div key={testIndex} className={`p-2 rounded text-sm ${
                        test.passed ? 'bg-green-100' : 'bg-red-100'
                      }`}>
                        <div className="flex justify-between items-center">
                          <span>Test Case {testIndex + 1}</span>
                          <span className={test.passed ? 'text-green-600' : 'text-red-600'}>
                            {test.passed ? '✅ Passed' : '❌ Failed'}
                          </span>
                        </div>
                        {!test.passed && (
                          <div className="mt-1 text-xs">
                            <div>Expected: {test.expected_output}</div>
                            <div>Got: {test.actual_output || 'No output'}</div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {questionResult.code_quality && (
                <div className="bg-blue-50 p-3 rounded">
                  <h5 className="font-medium text-blue-900 mb-2">Code Quality Analysis:</h5>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-blue-800">Readability:</span>
                      <span className="ml-1 font-medium">{questionResult.code_quality.readability_score}/100</span>
                    </div>
                    <div>
                      <span className="text-blue-800">Efficiency:</span>
                      <span className="ml-1 font-medium">{questionResult.code_quality.efficiency_score}/100</span>
                    </div>
                    <div>
                      <span className="text-blue-800">Best Practices:</span>
                      <span className="ml-1 font-medium">{questionResult.code_quality.best_practices_score}/100</span>
                    </div>
                  </div>
                  {questionResult.code_quality.comments && questionResult.code_quality.comments.length > 0 && (
                    <div className="mt-2">
                      <ul className="text-sm text-blue-800 space-y-1">
                        {questionResult.code_quality.comments.map((comment, i) => (
                          <li key={i}>• {comment}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EvaluationScores;