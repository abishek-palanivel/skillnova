import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import InitiateVideoCall from '../../components/InitiateVideoCall';
import { 
  Users, 
  MessageCircle, 
  Calendar, 
  Star,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Video
} from 'lucide-react';
import toast from 'react-hot-toast';

const MentorDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [showVideoCallModal, setShowVideoCallModal] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/mentor-portal/dashboard');
      if (response.data.success) {
        setDashboardData(response.data.dashboard);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading mentor dashboard..." />;
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Dashboard Not Available</h2>
            <p className="text-gray-600">Unable to load dashboard data.</p>
          </div>
        </div>
      </div>
    );
  }

  const { statistics, mentor_profile, recent_messages } = dashboardData;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Mentor Dashboard</h1>
          <p className="text-gray-600">Manage your mentoring activities and connect with students</p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Calendar className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Sessions</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.total_sessions}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.completed_sessions}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Scheduled</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.pending_sessions}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Star className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Rating</p>
                <p className="text-2xl font-bold text-gray-900">
                  {statistics.rating > 0 ? statistics.rating.toFixed(1) : 'N/A'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-8 w-8 text-indigo-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Reviews</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.total_reviews || 0}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Summary */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Profile Summary</h2>
                <button
                  onClick={() => navigate('/mentor/profile')}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  Edit Profile
                </button>
              </div>
              
              <div className="space-y-4">
                {mentor_profile.bio && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-1">Bio</h3>
                    <p className="text-gray-600">{mentor_profile.bio}</p>
                  </div>
                )}
                
                {mentor_profile.expertise_areas && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-1">Expertise Areas</h3>
                    <p className="text-gray-600">{mentor_profile.expertise_areas}</p>
                  </div>
                )}
                
                {!mentor_profile.bio && !mentor_profile.expertise_areas && mentor_profile.experience_years === 0 && (
                  <div className="text-center py-6">
                    <p className="text-gray-500 text-sm">Complete your profile to help students learn more about you.</p>
                  </div>
                )}
                
                <div className="flex items-center space-x-4">
                  {mentor_profile.experience_years > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-700">Experience: </span>
                      <span className="text-gray-600">{mentor_profile.experience_years} years</span>
                    </div>
                  )}
                  <div>
                    <span className="text-sm font-medium text-gray-700">Status: </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      mentor_profile.is_verified 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {mentor_profile.is_verified ? 'Verified' : 'Pending Verification'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <button
                  onClick={() => navigate('/mentor/chats')}
                  className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <MessageCircle className="w-6 h-6 text-blue-600" />
                  <div className="text-left">
                    <p className="font-medium text-gray-900">View Chats</p>
                    <p className="text-sm text-gray-600">{statistics.active_chats} active</p>
                  </div>
                </button>
                
                <button
                  onClick={() => setShowVideoCallModal(true)}
                  className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <Video className="w-6 h-6 text-red-600" />
                  <div className="text-left">
                    <p className="font-medium text-gray-900">Start Video Call</p>
                    <p className="text-sm text-gray-600">Call students</p>
                  </div>
                </button>
                
                <button
                  onClick={() => navigate('/mentor/sessions')}
                  className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <Calendar className="w-6 h-6 text-green-600" />
                  <div className="text-left">
                    <p className="font-medium text-gray-900">Sessions</p>
                    <p className="text-sm text-gray-600">Manage schedule</p>
                  </div>
                </button>
                
                <button
                  onClick={() => navigate('/mentor/students')}
                  className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <Users className="w-6 h-6 text-purple-600" />
                  <div className="text-left">
                    <p className="font-medium text-gray-900">Students</p>
                    <p className="text-sm text-gray-600">View all</p>
                  </div>
                </button>
              </div>
              

            </div>
          </div>

          {/* Recent Messages */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Recent Messages</h2>
                <button
                  onClick={() => navigate('/mentor/chats')}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  View All
                </button>
              </div>
              
              {recent_messages.length > 0 ? (
                <div className="space-y-4">
                  {recent_messages.map((message) => (
                    <div key={message.id} className="border-b border-gray-100 pb-3 last:border-b-0">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                            <span className="text-xs font-medium text-blue-600">
                              {message.sender_name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900">{message.sender_name}</p>
                          <p className="text-sm text-gray-600 truncate">{message.message_text}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(message.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Video Call Modal */}
      <InitiateVideoCall
        isOpen={showVideoCallModal}
        onClose={() => setShowVideoCallModal(false)}
        onCallInitiated={(call) => {
          toast.success('Video call initiated successfully!');
          // Optionally navigate to the call or update UI
        }}
      />
    </div>
  );
};

export default MentorDashboard;