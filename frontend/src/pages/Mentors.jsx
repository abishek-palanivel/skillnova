import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  Users, 
  Star, 
  Clock, 
  DollarSign,
  MessageCircle,
  Calendar,
  Filter,
  Search,
  Sparkles,
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

  const handleBookSession = async (mentorId) => {
    try {
      const response = await api.post(`/mentors/${mentorId}/book-session`);
      if (response.data.success) {
        toast.success('Session booking request sent!');
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to book session');
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

        {/* AI Recommendations Section */}
        {recommendations.length > 0 && showRecommendations && (
          <div className="mb-8">
            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 border border-green-200">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-6 h-6 text-green-600" />
                  <h2 className="text-xl font-semibold text-gray-900">
                    Perfect Mentors for You
                  </h2>
                </div>
                <button
                  onClick={() => setShowRecommendations(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {recommendations.slice(0, 6).map((mentor, index) => (
                  <div key={index} className="bg-white rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                        <Users className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{mentor.name}</h3>
                        <p className="text-sm text-gray-600">{mentor.expertise}</p>
                      </div>
                    </div>
                    
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-1">
                          <Award className="w-4 h-4 text-gray-500" />
                          <span>{mentor.experience_years} years exp</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Star className="w-4 h-4 text-yellow-400 fill-current" />
                          <span>{mentor.rating}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-1">
                          <MessageCircle className="w-4 h-4 text-gray-500" />
                          <span>{mentor.sessions_completed} sessions</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <DollarSign className="w-4 h-4 text-gray-500" />
                          <span>${mentor.hourly_rate}/hr</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full">
                        {mentor.match_score}% match
                      </span>
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4 text-green-500" />
                        <span className="text-sm text-green-600">{mentor.availability}</span>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => handleBookSession(mentor.id)}
                      className="w-full mt-3 px-3 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 transition-colors"
                    >
                      Book Session
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Search and Filter */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search mentors..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={selectedExpertise}
              onChange={(e) => setSelectedExpertise(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
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
              <div key={mentor.id} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                <div className="p-6">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-primary-400 to-accent-500 rounded-full flex items-center justify-center">
                      <Users className="w-8 h-8 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{mentor.name}</h3>
                      <p className="text-gray-600">{mentor.expertise}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-3 mb-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Award className="w-4 h-4 text-gray-500" />
                        <span className="text-sm text-gray-600">
                          {mentor.experience_years} years experience
                        </span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Star className="w-4 h-4 text-yellow-400 fill-current" />
                        <span className="text-sm font-medium">{mentor.rating > 0 ? mentor.rating.toFixed(1) : 'New'}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <MessageCircle className="w-4 h-4 text-gray-500" />
                        <span className="text-sm text-gray-600">
                          {mentor.sessions_completed > 0 ? `${mentor.sessions_completed} sessions completed` : 'New mentor'}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <DollarSign className="w-4 h-4 text-gray-500" />
                        <span className="text-sm text-gray-600">
                          {mentor.hourly_rate > 0 ? `$${mentor.hourly_rate}/hour` : 'Rate not set'}
                        </span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4 text-green-500" />
                        <span className="text-sm text-green-600">
                          {mentor.is_available ? 'Available' : 'Busy'}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleBookSession(mentor.id)}
                      className="flex-1 btn-primary flex items-center justify-center space-x-2"
                    >
                      <Calendar className="w-4 h-4" />
                      <span>Book Session</span>
                    </button>
                    <button className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors">
                      <MessageCircle className="w-4 h-4 text-gray-600" />
                    </button>
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