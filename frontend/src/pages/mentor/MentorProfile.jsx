import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Calendar,
  Award,
  Star,
  Edit,
  Save,
  X,
  ArrowLeft,
  Briefcase,
  DollarSign,
  Link,
  Github,
  Linkedin
} from 'lucide-react';
import toast from 'react-hot-toast';

const MentorProfile = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [profile, setProfile] = useState({
    bio: '',
    expertise_areas: '',
    experience_years: 0,
    hourly_rate: 0,
    linkedin_url: '',
    github_url: '',
    portfolio_url: '',
    is_verified: false,
    rating: 0,
    total_sessions: 0
  });
  const [editForm, setEditForm] = useState({});

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/mentor-portal/profile');
      if (response.data.success) {
        setProfile(response.data.profile);
        setEditForm(response.data.profile);
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      const response = await api.post('/mentor-portal/profile', editForm);
      if (response.data.success) {
        setProfile(editForm);
        setEditing(false);
        toast.success('Profile updated successfully');
      }
    } catch (error) {
      console.error('Failed to update profile:', error);
      toast.error('Failed to update profile');
    }
  };

  const handleCancel = () => {
    setEditForm(profile);
    setEditing(false);
  };

  if (loading) {
    return <LoadingSpinner text="Loading profile..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/mentor')}
            className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Mentor Profile</h1>
              <p className="text-gray-600">Manage your professional information</p>
            </div>
            {!editing ? (
              <button
                onClick={() => setEditing(true)}
                className="btn-primary flex items-center space-x-2"
              >
                <Edit className="w-4 h-4" />
                <span>Edit Profile</span>
              </button>
            ) : (
              <div className="flex space-x-2">
                <button
                  onClick={handleSave}
                  className="btn-primary flex items-center space-x-2"
                >
                  <Save className="w-4 h-4" />
                  <span>Save</span>
                </button>
                <button
                  onClick={handleCancel}
                  className="btn-outline flex items-center space-x-2"
                >
                  <X className="w-4 h-4" />
                  <span>Cancel</span>
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-center mb-6">
                <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <User className="w-12 h-12 text-blue-600" />
                </div>
                <div className="flex items-center justify-center space-x-2 mb-2">
                  <span className={`px-3 py-1 text-sm font-medium rounded-full ${
                    profile.is_verified 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {profile.is_verified ? 'Verified Mentor' : 'Pending Verification'}
                  </span>
                </div>
                {profile.rating > 0 && (
                  <div className="flex items-center justify-center space-x-1">
                    <Star className="w-5 h-5 text-yellow-400 fill-current" />
                    <span className="text-lg font-semibold">{profile.rating.toFixed(1)}</span>
                    <span className="text-gray-600">({profile.total_sessions} sessions)</span>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <Briefcase className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-700">Experience</p>
                    <p className="text-gray-600">{profile.experience_years} years</p>
                  </div>
                </div>

                {profile.hourly_rate > 0 && (
                  <div className="flex items-center space-x-3">
                    <DollarSign className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-700">Hourly Rate</p>
                      <p className="text-gray-600">${profile.hourly_rate}/hour</p>
                    </div>
                  </div>
                )}

                {profile.linkedin_url && (
                  <div className="flex items-center space-x-3">
                    <Linkedin className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-700">LinkedIn</p>
                      <a 
                        href={profile.linkedin_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700 text-sm"
                      >
                        View Profile
                      </a>
                    </div>
                  </div>
                )}

                {profile.github_url && (
                  <div className="flex items-center space-x-3">
                    <Github className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-700">GitHub</p>
                      <a 
                        href={profile.github_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700 text-sm"
                      >
                        View Profile
                      </a>
                    </div>
                  </div>
                )}

                {profile.portfolio_url && (
                  <div className="flex items-center space-x-3">
                    <Link className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-700">Portfolio</p>
                      <a 
                        href={profile.portfolio_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700 text-sm"
                      >
                        View Portfolio
                      </a>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Profile Details */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="space-y-6">
                {/* Bio */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Professional Bio
                  </label>
                  {editing ? (
                    <textarea
                      value={editForm.bio || ''}
                      onChange={(e) => setEditForm({...editForm, bio: e.target.value})}
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Tell students about your background, experience, and what you can help them with..."
                    />
                  ) : (
                    <div className="p-3 bg-gray-50 rounded-md">
                      <p className="text-gray-700">
                        {profile.bio || ''}
                      </p>
                    </div>
                  )}
                </div>

                {/* Expertise Areas */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Expertise Areas
                  </label>
                  {editing ? (
                    <input
                      type="text"
                      value={editForm.expertise_areas || ''}
                      onChange={(e) => setEditForm({...editForm, expertise_areas: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g., JavaScript, React, Node.js, Python, Data Science"
                    />
                  ) : (
                    <div className="p-3 bg-gray-50 rounded-md">
                      <p className="text-gray-700">
                        {profile.expertise_areas || ''}
                      </p>
                    </div>
                  )}
                </div>

                {/* Experience Years */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Years of Experience
                  </label>
                  {editing ? (
                    <input
                      type="number"
                      min="0"
                      max="50"
                      value={editForm.experience_years || 0}
                      onChange={(e) => setEditForm({...editForm, experience_years: parseInt(e.target.value) || 0})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  ) : (
                    <div className="p-3 bg-gray-50 rounded-md">
                      <p className="text-gray-700">{profile.experience_years} years</p>
                    </div>
                  )}
                </div>

                {/* Hourly Rate */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hourly Rate (USD)
                  </label>
                  {editing ? (
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={editForm.hourly_rate || 0}
                      onChange={(e) => setEditForm({...editForm, hourly_rate: parseFloat(e.target.value) || 0})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="0.00"
                    />
                  ) : (
                    <div className="p-3 bg-gray-50 rounded-md">
                      <p className="text-gray-700">
                        {profile.hourly_rate > 0 ? `$${profile.hourly_rate}/hour` : ''}
                      </p>
                    </div>
                  )}
                </div>

                {/* LinkedIn URL */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    LinkedIn Profile URL
                  </label>
                  {editing ? (
                    <input
                      type="url"
                      value={editForm.linkedin_url || ''}
                      onChange={(e) => setEditForm({...editForm, linkedin_url: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="https://linkedin.com/in/yourprofile"
                    />
                  ) : (
                    <div className="p-3 bg-gray-50 rounded-md">
                      <p className="text-gray-700">
                        {profile.linkedin_url || ''}
                      </p>
                    </div>
                  )}
                </div>

                {/* GitHub URL */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    GitHub Profile URL
                  </label>
                  {editing ? (
                    <input
                      type="url"
                      value={editForm.github_url || ''}
                      onChange={(e) => setEditForm({...editForm, github_url: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="https://github.com/yourusername"
                    />
                  ) : (
                    <div className="p-3 bg-gray-50 rounded-md">
                      <p className="text-gray-700">
                        {profile.github_url || ''}
                      </p>
                    </div>
                  )}
                </div>

                {/* Portfolio URL */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Portfolio Website URL
                  </label>
                  {editing ? (
                    <input
                      type="url"
                      value={editForm.portfolio_url || ''}
                      onChange={(e) => setEditForm({...editForm, portfolio_url: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="https://yourportfolio.com"
                    />
                  ) : (
                    <div className="p-3 bg-gray-50 rounded-md">
                      <p className="text-gray-700">
                        {profile.portfolio_url || ''}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MentorProfile;