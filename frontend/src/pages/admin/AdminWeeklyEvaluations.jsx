import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../../components/LoadingSpinner';
import Cookies from 'js-cookie';

const AdminWeeklyEvaluations = () => {
  const { user } = useAuth();
  const [evaluations, setEvaluations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedEvaluation, setSelectedEvaluation] = useState(null);
  const [scores, setScores] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    scheduled_date: '',
    total_questions: 10,
    coding_questions_count: 3,
    mcq_questions_count: 7,
    duration_minutes: 60
  });

  // Set default date when modal opens
  const handleCreateModalOpen = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(9, 0, 0, 0); // Set to 9 AM
    const defaultDate = tomorrow.toISOString().slice(0, 16); // Format for datetime-local
    
    setCreateForm({
      scheduled_date: defaultDate,
      total_questions: 10,
      coding_questions_count: 3,
      mcq_questions_count: 7,
      duration_minutes: 60
    });
    setShowCreateModal(true);
  };

  useEffect(() => {
    fetchEvaluations();
  }, []);

  const fetchEvaluations = async () => {
    try {
      const token = Cookies.get('skillnova_token');
      if (!token) {
        setError('Authentication token not found. Please login again.');
        setLoading(false);
        return;
      }

      const response = await fetch('http://localhost:5000/api/admin/weekly-evaluations', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setEvaluations(data.evaluations);
        setError(''); // Clear any previous errors
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to fetch evaluations');
      }
    } catch (err) {
      setError('Network error occurred. Please check if the backend server is running.');
      console.error('Fetch evaluations error:', err);
    } finally {
      setLoading(false);
    }
  };

  const createEvaluation = async (e) => {
    e.preventDefault();
    
    // Clear previous errors
    setError('');
    setSuccess('');
    
    // Validate form
    if (!createForm.scheduled_date) {
      setError('Please select a scheduled date and time');
      return;
    }
    
    // Validate that the date is in the future
    const selectedDate = new Date(createForm.scheduled_date);
    const now = new Date();
    if (selectedDate <= now) {
      setError('Scheduled date must be in the future');
      return;
    }
    
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/admin/weekly-evaluations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${Cookies.get('skillnova_token')}`
        },
        body: JSON.stringify(createForm)
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('Weekly evaluation created successfully!');
        setShowCreateModal(false);
        fetchEvaluations();
        setCreateForm({
          scheduled_date: '',
          total_questions: 10,
          coding_questions_count: 3,
          mcq_questions_count: 7,
          duration_minutes: 60
        });
      } else {
        setError(data.message || 'Failed to create evaluation');
      }
    } catch (err) {
      setError('Network error occurred. Please check if the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  const autoGenerateEvaluations = async () => {
    // Clear previous messages
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const token = Cookies.get('skillnova_token');
      if (!token) {
        setError('Authentication token not found. Please login again.');
        setLoading(false);
        return;
      }

      const response = await fetch('http://localhost:5000/api/admin/weekly-evaluations/auto-generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ weeks_ahead: 4 })
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(`Auto-generated ${data.created_evaluations.length} evaluations for the next 4 weeks!`);
        fetchEvaluations();
      } else {
        setError(data.message || 'Failed to auto-generate evaluations');
      }
    } catch (err) {
      setError('Network error occurred. Please check if the backend server is running.');
      console.error('Auto-generate error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchEvaluationScores = async (evaluationId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/admin/weekly-evaluations/${evaluationId}/scores`, {
        headers: {
          'Authorization': `Bearer ${Cookies.get('skillnova_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setScores(data.scores);
        setSelectedEvaluation(data.evaluation);
      } else {
        setError('Failed to fetch scores');
      }
    } catch (err) {
      setError('Network error occurred');
    }
  };

  const updateDecision = async (scoreId, decision, feedback) => {
    try {
      const response = await fetch(`http://localhost:5000/api/admin/weekly-evaluations/scores/${scoreId}/decision`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${Cookies.get('skillnova_token')}`
        },
        body: JSON.stringify({
          admin_decision: decision,
          admin_feedback: feedback
        })
      });

      if (response.ok) {
        setSuccess('Decision updated successfully!');
        if (selectedEvaluation) {
          fetchEvaluationScores(selectedEvaluation.id);
        }
      } else {
        setError('Failed to update decision');
      }
    } catch (err) {
      setError('Network error occurred');
    }
  };

  const sendEmail = async (scoreId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/admin/weekly-evaluations/scores/${scoreId}/send-email`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${Cookies.get('skillnova_token')}`
        }
      });

      if (response.ok) {
        setSuccess('📧 Evaluation result email sent successfully!');
        if (selectedEvaluation) {
          fetchEvaluationScores(selectedEvaluation.id);
        }
      } else {
        setError('Failed to send email');
      }
    } catch (err) {
      setError('Network error occurred');
    }
  };

  const sendScholarshipEmail = async (userId, userName, userEmail) => {
    try {
      const response = await fetch(`http://localhost:5000/api/admin/users/${userId}/send-scholarship`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${Cookies.get('skillnova_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          amount: 'Full Coverage',
          duration: '6 months',
          coverage: 'All courses and mentorship',
          start_date: 'Immediate'
        })
      });

      if (response.ok) {
        setSuccess(`🎓 Scholarship offer sent to ${userName} (${userEmail})`);
      } else {
        setError('Failed to send scholarship email');
      }
    } catch (err) {
      setError('Network error occurred');
    }
  };

  const sendInternshipEmail = async (userId, userName, userEmail) => {
    try {
      const response = await fetch(`http://localhost:5000/api/admin/users/${userId}/send-internship`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${Cookies.get('skillnova_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          position: 'Software Development Intern',
          duration: '3-6 months',
          stipend: 'Competitive',
          location: 'Remote/Hybrid',
          start_date: 'Flexible'
        })
      });

      if (response.ok) {
        setSuccess(`💼 Internship offer sent to ${userName} (${userEmail})`);
      } else {
        setError('Failed to send internship email');
      }
    } catch (err) {
      setError('Network error occurred');
    }
  };

  const deleteEvaluation = async (evaluationId, evaluationTitle) => {
    if (!window.confirm(`Are you sure you want to delete the evaluation "${evaluationTitle}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:5000/api/admin/weekly-evaluations/${evaluationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${Cookies.get('skillnova_token')}`
        }
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(data.message);
        fetchEvaluations(); // Refresh the list
      } else {
        setError(data.message || 'Failed to delete evaluation');
      }
    } catch (err) {
      setError('Network error occurred');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'selected': return 'text-green-600 bg-green-100';
      case 'rejected': return 'text-red-600 bg-red-100';
      case 'internship_offered': return 'text-blue-600 bg-blue-100';
      case 'scholarship_offered': return 'text-purple-600 bg-purple-100';
      default: return 'text-yellow-600 bg-yellow-100';
    }
  };

  const getGradeColor = (grade) => {
    if (['A+', 'A', 'A-'].includes(grade)) return 'text-green-600';
    if (['B+', 'B', 'B-'].includes(grade)) return 'text-blue-600';
    if (['C+', 'C', 'C-'].includes(grade)) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Weekly Evaluations Management</h1>
        <p className="mt-2 text-gray-600">Manage automated weekly evaluations and review student performance</p>
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

      {/* Action Buttons */}
      <div className="mb-6 flex flex-wrap gap-4">
        <button
          onClick={handleCreateModalOpen}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          Create Evaluation
        </button>
        <button
          onClick={autoGenerateEvaluations}
          className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
        >
          Auto-Generate Next 4 Weeks
        </button>
      </div>

      {/* Evaluations List */}
      <div className="bg-white shadow-md rounded-lg overflow-hidden mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">All Evaluations</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Scheduled Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Questions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Participation
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Score
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
              {evaluations.map((evaluation) => (
                <tr key={evaluation.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{evaluation.title}</div>
                    <div className="text-sm text-gray-500">{evaluation.duration_minutes} minutes</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div>{new Date(evaluation.scheduled_date).toLocaleDateString()}</div>
                    <div className="text-xs text-gray-500 font-mono">
                      {new Date(evaluation.scheduled_date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div>{evaluation.total_questions} total</div>
                    <div className="text-xs text-gray-500">
                      {evaluation.coding_questions_count} coding, {evaluation.mcq_questions_count} MCQ
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div>{evaluation.statistics.completed_attempts}/{evaluation.statistics.total_attempts}</div>
                    <div className="text-xs text-gray-500">
                      {evaluation.statistics.completion_rate}% completion
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {evaluation.statistics.average_score}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      evaluation.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {evaluation.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => fetchEvaluationScores(evaluation.id)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      View Scores
                    </button>
                    <button
                      onClick={() => deleteEvaluation(evaluation.id, evaluation.title)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Scores Modal */}
      {selectedEvaluation && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-6xl shadow-lg rounded-md bg-white">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">
                Scores for {selectedEvaluation.title}
              </h3>
              <button
                onClick={() => setSelectedEvaluation(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Student
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Grade
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Decision
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {scores.map((score) => (
                    <ScoreRow
                      key={score.id}
                      score={score}
                      onUpdateDecision={updateDecision}
                      onSendEmail={sendEmail}
                      getStatusColor={getStatusColor}
                      getGradeColor={getGradeColor}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Create Evaluation Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Create Weekly Evaluation</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <form onSubmit={createEvaluation}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Scheduled Date & Time
                </label>
                <input
                  type="datetime-local"
                  value={createForm.scheduled_date}
                  onChange={(e) => setCreateForm({...createForm, scheduled_date: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Total Questions
                </label>
                <input
                  type="number"
                  min="5"
                  max="20"
                  value={createForm.total_questions}
                  onChange={(e) => setCreateForm({...createForm, total_questions: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Coding Questions
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={createForm.coding_questions_count}
                  onChange={(e) => setCreateForm({...createForm, coding_questions_count: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  MCQ Questions
                </label>
                <input
                  type="number"
                  min="1"
                  max="15"
                  value={createForm.mcq_questions_count}
                  onChange={(e) => setCreateForm({...createForm, mcq_questions_count: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Duration (minutes)
                </label>
                <input
                  type="number"
                  min="30"
                  max="180"
                  value={createForm.duration_minutes}
                  onChange={(e) => setCreateForm({...createForm, duration_minutes: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Create Evaluation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// Score Row Component
const ScoreRow = ({ score, onUpdateDecision, onSendEmail, getStatusColor, getGradeColor }) => {
  const [showDecisionModal, setShowDecisionModal] = useState(false);
  const [decision, setDecision] = useState(score.admin_decision || 'pending');
  const [feedback, setFeedback] = useState(score.admin_feedback || '');

  const handleUpdateDecision = () => {
    onUpdateDecision(score.id, decision, feedback);
    setShowDecisionModal(false);
  };

  return (
    <>
      <tr>
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="text-sm font-medium text-gray-900">{score.user.name}</div>
          <div className="text-sm text-blue-600 font-medium hover:text-blue-800 cursor-pointer" 
               onClick={() => navigator.clipboard.writeText(score.user.email)}
               title="Click to copy email">
            📧 {score.user.email}
          </div>
          <div className="text-xs text-gray-400 mt-1">Click email to copy</div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <div className="text-sm font-medium text-gray-900">{score.score_percentage}%</div>
          <div className="text-xs text-gray-500">
            Coding: {score.coding_score}% | MCQ: {score.mcq_score}%
          </div>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <span className={`text-sm font-semibold ${getGradeColor(score.grade)}`}>
            {score.grade}
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap">
          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(score.admin_decision)}`}>
            {score.admin_decision || 'Pending'}
          </span>
        </td>
        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
          <div className="flex flex-col space-y-1">
            <button
              onClick={() => setShowDecisionModal(true)}
              className="text-blue-600 hover:text-blue-900 text-xs"
            >
              📝 Update Decision
            </button>
            
            <div className="flex space-x-2">
              {!score.email_sent && (
                <button
                  onClick={() => onSendEmail(score.id)}
                  className="text-green-600 hover:text-green-900 text-xs"
                >
                  📧 Send Result
                </button>
              )}
              
              <button
                onClick={() => toast.info('Scholarship feature coming soon!')}
                className="text-purple-600 hover:text-purple-900 text-xs"
                title="Send Scholarship Offer"
              >
                🎓 Scholarship
              </button>
              
              <button
                onClick={() => toast.info('Internship feature coming soon!')}
                className="text-orange-600 hover:text-orange-900 text-xs"
                title="Send Internship Offer"
              >
                💼 Internship
              </button>
            </div>
            
            {score.email_sent && (
              <span className="text-gray-500 text-xs">
                ✅ Email sent {score.email_sent_at ? new Date(score.email_sent_at).toLocaleDateString() : ''}
              </span>
            )}
          </div>
        </td>
      </tr>

      {/* Decision Modal */}
      {showDecisionModal && (
        <tr>
          <td colSpan="5" className="px-6 py-4">
            <div className="bg-gray-50 p-4 rounded-md">
              <h4 className="font-medium mb-3">Update Decision for {score.user.name}</h4>
              
              <div className="mb-3">
                <label className="block text-sm font-medium text-gray-700 mb-1">Decision</label>
                <select
                  value={decision}
                  onChange={(e) => setDecision(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="pending">Pending</option>
                  <option value="selected">Selected</option>
                  <option value="rejected">Rejected</option>
                  <option value="internship_offered">Internship Offered</option>
                  <option value="scholarship_offered">Scholarship Offered</option>
                </select>
              </div>

              <div className="mb-3">
                <label className="block text-sm font-medium text-gray-700 mb-1">Feedback</label>
                <textarea
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  rows="3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Provide feedback to the student..."
                />
              </div>

              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setShowDecisionModal(false)}
                  className="px-3 py-1 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpdateDecision}
                  className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Update
                </button>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
};

export default AdminWeeklyEvaluations;