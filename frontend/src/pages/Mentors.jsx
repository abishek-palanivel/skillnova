import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  Users, 
  Clock, 
  MessageCircle,
  Calendar,
  Filter,
  Search,
  Award
} from 'lucide-react';
import toast from 'react-hot-toast';

const Mentors = () => {
  const { user } = useAuth();
  const [mentors, setMentors] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedExpertise, setSelectedExpertise] = useState('all');
  const [showRecommendations, setShowRecommendations] = useState(true);

  useEffect(() => {
    fetchMentors();
    fetchRecommendations();
  }, []);

  const fetchMentors = async () => {
    try {
      const response = await api.get('/mentors');
      if (response.data.success) {
        setMentors(response.data.mentors || []);
      }
    } catch (error) {
      console.error('Failed to fetch mentors:', error);
      toast.error('Failed to load mentors');
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await api.get('/user/recommendations/mentors');
      if (response.data.success) {
        setRecommendations(response.data.recommendations || []);
      }
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBookSession = async (mentorId, mentorName) => {
    try {
      const response = await api.post(`/mentors/${mentorId}/book-session`, {
        duration_minutes: 60
      });
      if (response.data.success) {
        toast.success(`Session request sent to ${mentorName}! They will contact you soon.`);
        // Don't navigate anywhere - stay on mentors page
      }
    } catch (error) {
      console.error('Book session error:', error);
      toast.error(error.response?.data?.message || 'Failed to book session. Please try again.');
    }
  };

  const handleMessage = async (mentorId, mentorName) => {
    try {
      // Create a chat room with the mentor
      const response = await api.post('/chat/rooms', {
        target_user_id: mentorId,
        title: `Chat with ${mentorName}`
      });
      
      if (response.data.success) {
        toast.success(`Chat opened with ${mentorName}! Check the chat widget.`, { icon: '💬' });
        // The chat widget will automatically show the new room
      } else {
        toast.error(response.data.message || 'Failed to open chat');
      }
    } catch (error) {
      console.error('Message error:', error);
      // If room already exists, that's fine
      if (error.response?.status === 409) {
        toast.success(`Chat with ${mentorName} is ready! Check the chat widget.`, { icon: '💬' });
      } else {
        toast.error(error.response?.data?.message || 'Failed to open chat. Please try again.');
      }
    }
  };

  const filteredMentors = mentors.filter(mentor => {
    const matchesSearch = mentor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         mentor.expertise?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesExpertise = selectedExpertise === 'all' || mentor.expertise?.includes(selectedExpertise);
    return matchesSearch && matchesExpertise;
  });

  const expertiseAreas = ['all', ...new Set(mentors.flatMap(mentor => 
    mentor.expertise ? mentor.expertise.split(',').map(e => e.trim()) : []
  ))];

  if (loading) {
    return <LoadingSpinner text="Loading mentors..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Find Your Mentor
          </h1>
          <p className="text-gray-600">
            Connect with expert mentors to accelerate your learning journey
          </p>
        </div>



        {/* Search and Filter */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search mentors..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-white border border-gray-300 text-gray-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={selectedExpertise}
              onChange={(e) => setSelectedExpertise(e.target.value)}
              className="px-4 py-2 bg-white border border-gray-300 text-gray-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {expertiseAreas.map(area => (
                <option key={area} value={area}>
                  {area === 'all' ? 'All Expertise' : area}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Mentors Grid */}
        {filteredMentors.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredMentors.map((mentor) => (
              <div key={mentor.id} className="bg-white border border-gray-200 shadow-lg rounded-xl hover:shadow-xl transition-all duration-300 hover:scale-105 overflow-hidden">
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-1">
                  <div className="bg-white rounded-lg p-6">
                    <div className="flex items-center space-x-4 mb-4">
                      <div className="w-16 h-16 bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
                        <Users className="w-8 h-8 text-white" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-gray-900 mb-1">{mentor.name}</h3>
                        <div className="bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 rounded-full">
                          <p className="text-sm font-medium text-blue-800">{mentor.expertise}</p>
                        </div>
                      </div>
                    </div>
                  
                  <div className="space-y-3 mb-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Award className="w-4 h-4 text-blue-500" />
                        <span className="text-sm text-gray-700 font-medium">
                          {mentor.experience_years} years experience
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <MessageCircle className="w-4 h-4 text-green-500" />
                        <span className="text-sm text-gray-700">
                          {mentor.sessions_completed > 0 ? `${mentor.sessions_completed} sessions completed` : 'New mentor'}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Clock className="w-4 h-4 text-emerald-500" />
                        <span className={`text-sm font-medium ${mentor.is_available ? 'text-emerald-600' : 'text-orange-600'}`}>
                          {mentor.is_available ? '🟢 Available now' : '🟡 Busy'}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                    <div className="flex space-x-3 mt-6">
                      <button
                        onClick={() => handleBookSession(mentor.id, mentor.name)}
                        className="flex-1 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700 text-white flex items-center justify-center space-x-2 px-4 py-3 rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                      >
                        <Calendar className="w-4 h-4" />
                        <span className="font-semibold">Book Session</span>
                      </button>
                      <button 
                        onClick={() => handleMessage(mentor.user_id || mentor.id, mentor.name)}
                        className="px-4 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                        title="Send Message"
                      >
                        <MessageCircle className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No mentors found</h3>
            <p className="text-gray-600">
              {searchTerm || selectedExpertise !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : 'Mentors will be available soon'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Mentors;