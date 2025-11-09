import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import { formatSharpDateTime, formatSharpTime } from '../utils/dateUtils';
import Cookies from 'js-cookie';

const WeeklyEvaluation = () => {
  const { user } = useAuth();
  const [nextEvaluation, setNextEvaluation] = useState(null);
  const [currentEvaluation, setCurrentEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchEvaluationInfo();
  }, []);

  const fetchEvaluationInfo = async () => {
    try {
      // Fetch both next and current evaluations
      const [nextResponse, currentResponse] = await Promise.all([
        fetch('http://localhost:5000/api/weekly-evaluations/next', {
          headers: {
            'Authorization': `Bearer ${Cookies.get('skillnova_token')}`
          }
        }),
        fetch('http://localhost:5000/api/weekly-evaluations/current', {
          headers: {
            'Authorization': `Bearer ${Cookies.get('skillnova_token')}`
          }
        })
      ]);

      if (nextResponse.ok) {
        const nextData = await nextResponse.json();
        setNextEvaluation(nextData.next_evaluation);
      }

      if (currentResponse.ok) {
        const currentData = await currentResponse.json();
        setCurrentEvaluation(currentData.current_evaluation);
      }
    } catch (err) {
      setError('Failed to fetch evaluation information');
    } finally {
      setLoading(false);
    }
  };

  const startEvaluation = async (evaluationId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/weekly-evaluations/${evaluationId}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${Cookies.get('skillnova_token')}`
        }
      });

      const data = await response.json();

      if (response.ok) {
        // Redirect to evaluation taking page
        window.location.href = `/evaluation/${data.attempt_id}`;
      } else {
        setError(data.message || 'Failed to start evaluation');
      }
    } catch (err) {
      setError('Network error occurred');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'in_progress': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      }),
      time: formatSharpTime(date),
      fullDateTime: formatSharpDateTime(date)
    };
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Weekly Evaluation</h1>
        <p className="mt-2 text-gray-600">
          Test your skills with our comprehensive weekly evaluations
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      {/* Time Window Information */}
      <div className="mb-8 bg-gradient-to-r from-purple-500 to-blue-600 rounded-lg shadow-lg text-white p-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">📅 Weekly Evaluation Schedule</h2>
          <p className="text-purple-100 mb-4">Every Sunday • 5:00 PM - 7:00 PM</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <div className="text-lg font-bold">⏰ Start Time</div>
              <div className="text-sm text-purple-100">Sunday 5:00 PM</div>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <div className="text-lg font-bold">⏱️ Duration</div>
              <div className="text-sm text-purple-100">60 Minutes Strict</div>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <div className="text-lg font-bold">🔒 End Time</div>
              <div className="text-sm text-purple-100">Sunday 7:00 PM</div>
            </div>
          </div>
          
          <div className="text-center">
            <p className="text-purple-100 text-sm">
              ⚠️ Start button will only be available during the 2-hour window (5:00 PM - 7:00 PM Sunday)
            </p>
          </div>
        </div>
      </div>

      {/* Current Evaluation */}
      {currentEvaluation && (
        <div className="mb-8 bg-white shadow-lg rounded-lg overflow-hidden border-l-4 border-green-500">
          <div className="px-6 py-4 bg-green-50">
            <h2 className="text-xl font-semibold text-green-900 flex items-center">
              <span className="mr-2">🔥</span>
              Evaluation Available Now!
            </h2>
            <p className="text-green-700 text-sm mt-1">
              Window: {formatDateTime(currentEvaluation.scheduled_date).time} - {formatDateTime(new Date(new Date(currentEvaluation.scheduled_date).getTime() + 2*60*60*1000)).time}
            </p>
          </div>
          <div className="px-6 py-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {currentEvaluation.title}
                </h3>
                <p className="text-gray-600 mb-4">{currentEvaluation.description}</p>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {currentEvaluation.total_questions}
                    </div>
                    <div className="text-sm text-gray-500">Total Questions</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {currentEvaluation.coding_questions_count}
                    </div>
                    <div className="text-sm text-gray-500">Coding</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {currentEvaluation.mcq_questions_count}
                    </div>
                    <div className="text-sm text-gray-500">Multiple Choice</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {currentEvaluation.duration_minutes}
                    </div>
                    <div className="text-sm text-gray-500">Minutes</div>
                  </div>
                </div>

                {currentEvaluation.user_status && (
                  <div className="mb-4">
                    <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(currentEvaluation.user_status)}`}>
                      Status: {currentEvaluation.user_status.replace('_', ' ').toUpperCase()}
                    </span>
                    {currentEvaluation.score && (
                      <span className="ml-3 text-sm text-gray-600">
                        Score: {currentEvaluation.score}%
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-500">
                <div>Scheduled: {formatDateTime(currentEvaluation.scheduled_date).date}</div>
                <div>Time: {formatDateTime(currentEvaluation.scheduled_date).time}</div>
              </div>
              
              {currentEvaluation.user_status === 'not_started' && (
                <div className="text-right">
                  <div className="mb-2 text-sm text-green-600 font-medium">
                    ✅ Evaluation window is OPEN
                  </div>
                  <button
                    onClick={() => startEvaluation(currentEvaluation.id)}
                    className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 transition-colors font-medium shadow-lg"
                  >
                    🚀 Start Evaluation Now
                  </button>
                  <div className="mt-2 text-xs text-gray-500">
                    60 minutes • Auto-submit after time limit
                  </div>
                </div>
              )}
              
              {currentEvaluation.user_status === 'in_progress' && (
                <button
                  onClick={() => window.location.href = `/evaluation/${currentEvaluation.attempt_id}`}
                  className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 transition-colors font-medium"
                >
                  Continue Evaluation
                </button>
              )}
              
              {currentEvaluation.user_status === 'completed' && (
                <button
                  onClick={() => window.location.href = '/evaluation-scores'}
                  className="bg-gray-600 text-white px-6 py-3 rounded-md hover:bg-gray-700 transition-colors font-medium"
                >
                  View Results
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Next Evaluation */}
      {nextEvaluation && !currentEvaluation && (
        <div className="mb-8 bg-white shadow-lg rounded-lg overflow-hidden">
          <div className="px-6 py-4 bg-yellow-50">
            <h2 className="text-xl font-semibold text-yellow-900 flex items-center">
              <span className="mr-2">📅</span>
              Next Scheduled Evaluation
            </h2>
            <p className="text-yellow-700 text-sm mt-1">
              Start button will unlock on {formatDateTime(nextEvaluation.scheduled_date).date} at {formatDateTime(nextEvaluation.scheduled_date).time}
            </p>
          </div>
          <div className="px-6 py-6">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {nextEvaluation.title}
                </h3>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {nextEvaluation.total_questions}
                    </div>
                    <div className="text-sm text-gray-500">Questions</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {nextEvaluation.duration_minutes}
                    </div>
                    <div className="text-sm text-gray-500">Minutes</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-medium text-gray-700">
                      {formatDateTime(nextEvaluation.scheduled_date).date}
                    </div>
                    <div className="text-sm text-gray-500">Date</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-medium text-gray-700">
                      {formatDateTime(nextEvaluation.scheduled_date).time}
                    </div>
                    <div className="text-sm text-gray-500">Time</div>
                  </div>
                </div>

                {nextEvaluation.user_status && nextEvaluation.user_status !== 'not_started' && (
                  <div className="mb-4">
                    <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(nextEvaluation.user_status)}`}>
                      Status: {nextEvaluation.user_status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mt-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <span className="text-blue-500 text-xl">ℹ️</span>
                </div>
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-blue-900">Evaluation Information</h4>
                  <div className="mt-1 text-sm text-blue-700">
                    <p>• The evaluation will automatically start at the scheduled time</p>
                    <p>• You'll have a 24-hour window to complete it</p>
                    <p>• Make sure you have a stable internet connection</p>
                    <p>• Prepare your coding environment for programming questions</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* No Evaluations */}
      {!currentEvaluation && !nextEvaluation && (
        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          <div className="px-6 py-12 text-center">
            <div className="text-6xl mb-4">📝</div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              No Evaluations Scheduled
            </h2>
            <p className="text-gray-600 mb-6">
              There are currently no weekly evaluations scheduled. Check back later or contact your administrator.
            </p>
            <button
              onClick={() => window.location.href = '/practice'}
              className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors font-medium"
            >
              Practice Questions Instead
            </button>
          </div>
        </div>
      )}

      {/* No Evaluation Available */}
      {!currentEvaluation && !nextEvaluation && (
        <div className="mb-8 bg-white shadow-lg rounded-lg overflow-hidden">
          <div className="px-6 py-12 text-center">
            <div className="text-6xl mb-4">⏰</div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              No Evaluations Scheduled
            </h2>
            <p className="text-gray-600 mb-6">
              Weekly evaluations are scheduled every Sunday from 5:00 PM to 7:00 PM.
              Check back during the evaluation window to participate.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4 max-w-md mx-auto">
              <p className="text-blue-800 text-sm">
                <strong>Next evaluation window:</strong><br />
                Sunday 5:00 PM - 7:00 PM
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Quick Links */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">📊 View Scores</h3>
          <p className="text-gray-600 mb-4">Check your evaluation history and detailed results</p>
          <button
            onClick={() => window.location.href = '/evaluation-scores'}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            View All Scores →
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">💪 Practice</h3>
          <p className="text-gray-600 mb-4">Prepare for evaluations with practice questions</p>
          <button
            onClick={() => window.location.href = '/practice'}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            Start Practice →
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">📚 Courses</h3>
          <p className="text-gray-600 mb-4">Improve your skills with our comprehensive courses</p>
          <button
            onClick={() => window.location.href = '/courses'}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            Browse Courses →
          </button>
        </div>
      </div>
    </div>
  );
};

export default WeeklyEvaluation;