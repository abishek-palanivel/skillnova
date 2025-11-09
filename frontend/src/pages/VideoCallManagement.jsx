import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  Video, 
  Phone, 
  PhoneOff, 
  Clock, 
  User,
  Calendar,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

const VideoCallManagement = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [incomingCalls, setIncomingCalls] = useState([]);
  const [scheduledCalls, setScheduledCalls] = useState([]);
  const [callHistory, setCallHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('incoming');

  useEffect(() => {
    fetchCalls();
    
    // Set up polling for incoming calls
    const interval = setInterval(fetchCalls, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchCalls = async () => {
    try {
      const [incomingRes, scheduledRes, historyRes] = await Promise.all([
        api.get('/video-calls/incoming'),
        api.get('/video-calls/scheduled'),
        api.get('/video-calls/history')
      ]);

      if (incomingRes.data.success) {
        setIncomingCalls(incomingRes.data.calls);
      }
      if (scheduledRes.data.success) {
        setScheduledCalls(scheduledRes.data.calls);
      }
      if (historyRes.data.success) {
        setCallHistory(historyRes.data.calls);
      }
    } catch (error) {
      console.error('Failed to fetch calls:', error);
    } finally {
      setLoading(false);
    }
  };

  const acceptCall = async (callId) => {
    try {
      const response = await api.post(`/video-calls/${callId}/accept`);
      if (response.data.success) {
        navigate(`/video-call/${callId}`);
      }
    } catch (error) {
      console.error('Failed to accept call:', error);
      toast.error('Failed to accept call');
    }
  };

  const rejectCall = async (callId) => {
    try {
      const response = await api.post(`/video-calls/${callId}/reject`);
      if (response.data.success) {
        toast.success('Call rejected');
        fetchCalls();
      }
    } catch (error) {
      console.error('Failed to reject call:', error);
      toast.error('Failed to reject call');
    }
  };

  const joinScheduledCall = async (callId) => {
    try {
      const response = await api.post(`/video-calls/${callId}/join`);
      if (response.data.success) {
        navigate(`/video-call/${callId}`);
      }
    } catch (error) {
      console.error('Failed to join call:', error);
      toast.error('Failed to join call');
    }
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
  };

  const getCallStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'missed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'rejected':
        return <PhoneOff className="w-4 h-4 text-red-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Video Calls</h1>
          <p className="text-gray-600">Manage your video call sessions with mentors</p>
        </div>

        {/* Tab Navigation */}
        <div className="mb-6">
          <nav className="flex space-x-8">
            {[
              { id: 'incoming', label: 'Incoming Calls', count: incomingCalls.length },
              { id: 'scheduled', label: 'Scheduled', count: scheduledCalls.length },
              { id: 'history', label: 'History', count: callHistory.length }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center px-3 py-2 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
                {tab.count > 0 && (
                  <span className="ml-2 bg-blue-100 text-blue-600 text-xs px-2 py-1 rounded-full">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Incoming Calls */}
        {activeTab === 'incoming' && (
          <div className="space-y-4">
            {incomingCalls.length === 0 ? (
              <div className="text-center py-12">
                <Video className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No incoming calls</h3>
                <p className="text-gray-600">You'll see incoming video calls from mentors here</p>
              </div>
            ) : (
              incomingCalls.map((call) => {
                const { date, time } = formatDateTime(call.created_at);
                return (
                  <div key={call.id} className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                            <User className="w-6 h-6 text-blue-600" />
                          </div>
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {call.mentor_name}
                          </h3>
                          <p className="text-gray-600">{call.title || 'Mentoring Session'}</p>
                          <div className="flex items-center text-sm text-gray-500 mt-1">
                            <Clock className="w-4 h-4 mr-1" />
                            <span>{date} at {time}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex space-x-3">
                        <button
                          onClick={() => rejectCall(call.id)}
                          className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 flex items-center"
                        >
                          <PhoneOff className="w-4 h-4 mr-2" />
                          Reject
                        </button>
                        <button
                          onClick={() => acceptCall(call.id)}
                          className="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 flex items-center animate-pulse"
                        >
                          <Phone className="w-4 h-4 mr-2" />
                          Accept
                        </button>
                      </div>
                    </div>
                    {call.description && (
                      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-700">{call.description}</p>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        )}

        {/* Scheduled Calls */}
        {activeTab === 'scheduled' && (
          <div className="space-y-4">
            {scheduledCalls.length === 0 ? (
              <div className="text-center py-12">
                <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No scheduled calls</h3>
                <p className="text-gray-600">Your scheduled video calls will appear here</p>
              </div>
            ) : (
              scheduledCalls.map((call) => {
                const { date, time } = formatDateTime(call.scheduled_at);
                const isUpcoming = new Date(call.scheduled_at) > new Date();
                
                return (
                  <div key={call.id} className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                            <User className="w-6 h-6 text-purple-600" />
                          </div>
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {call.mentor_name}
                          </h3>
                          <p className="text-gray-600">{call.title || 'Mentoring Session'}</p>
                          <div className="flex items-center text-sm text-gray-500 mt-1">
                            <Calendar className="w-4 h-4 mr-1" />
                            <span>{date} at {time}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        {isUpcoming ? (
                          <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm rounded-full">
                            Upcoming
                          </span>
                        ) : (
                          <button
                            onClick={() => joinScheduledCall(call.id)}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
                          >
                            <Video className="w-4 h-4 mr-2" />
                            Join Call
                          </button>
                        )}
                      </div>
                    </div>
                    {call.description && (
                      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-700">{call.description}</p>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        )}

        {/* Call History */}
        {activeTab === 'history' && (
          <div className="space-y-4">
            {callHistory.length === 0 ? (
              <div className="text-center py-12">
                <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No call history</h3>
                <p className="text-gray-600">Your completed video calls will appear here</p>
              </div>
            ) : (
              callHistory.map((call) => {
                const { date, time } = formatDateTime(call.created_at);
                
                return (
                  <div key={call.id} className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                            <User className="w-6 h-6 text-gray-600" />
                          </div>
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {call.mentor_name}
                          </h3>
                          <p className="text-gray-600">{call.title || 'Mentoring Session'}</p>
                          <div className="flex items-center text-sm text-gray-500 mt-1">
                            <Clock className="w-4 h-4 mr-1" />
                            <span>{date} at {time}</span>
                            {call.duration && (
                              <>
                                <span className="mx-2">•</span>
                                <span>{call.duration} minutes</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        {getCallStatusIcon(call.status)}
                        <span className={`px-3 py-1 text-sm rounded-full capitalize ${
                          call.status === 'completed' 
                            ? 'bg-green-100 text-green-800'
                            : call.status === 'missed' || call.status === 'rejected'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {call.status}
                        </span>
                      </div>
                    </div>
                    {call.notes && (
                      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-700">{call.notes}</p>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoCallManagement;