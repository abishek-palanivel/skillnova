import { useState } from 'react';
import api from '../utils/api';
import { Video, X, Search } from 'lucide-react';
import toast from 'react-hot-toast';

const InitiateVideoCall = ({ isOpen, onClose, onCallInitiated }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);


  const searchUsers = async (term) => {
    if (!term.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      setLoading(true);
      const response = await api.get(`/user/search?q=${encodeURIComponent(term)}`);
      if (response.data.success) {
        setSearchResults(response.data.users);
      }
    } catch (error) {
      console.error('Failed to search users:', error);
      toast.error('Failed to search users');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    
    // Debounce search
    clearTimeout(window.searchTimeout);
    window.searchTimeout = setTimeout(() => {
      searchUsers(value);
    }, 300);
  };

  const initiateCall = async (user) => {
    try {
      const response = await api.post('/video-calls/initiate', {
        participant_id: user.id,
        participant_email: user.email
      });

      if (response.data.success) {
        toast.success(`Video call initiated with ${user.name}`);
        onCallInitiated && onCallInitiated(response.data.call);
        onClose();
      }
    } catch (error) {
      console.error('Failed to initiate call:', error);
      toast.error(error.response?.data?.message || 'Failed to initiate call');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">Start Video Call</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Search Input */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            value={searchTerm}
            onChange={handleSearchChange}
            placeholder="Search users by name or email..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Search Results */}
        <div className="max-h-64 overflow-y-auto">
          {loading ? (
            <div className="text-center py-4 text-gray-500">Searching...</div>
          ) : searchResults.length === 0 && searchTerm ? (
            <div className="text-center py-4 text-gray-500">No users found</div>
          ) : (
            searchResults.map((user) => (
              <div
                key={user.id}
                className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-md"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-medium">
                      {user.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{user.name}</p>
                    <p className="text-sm text-gray-500">{user.email}</p>
                  </div>
                </div>
                <button
                  onClick={() => initiateCall(user)}
                  className="flex items-center px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  <Video className="w-4 h-4 mr-1" />
                  Call
                </button>
              </div>
            ))
          )}
        </div>

        {/* Quick Actions */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600 mb-2">Quick actions:</p>
          <div className="flex space-x-2">
            <button
              onClick={() => setSearchTerm('student')}
              className="px-3 py-1 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 text-sm"
            >
              Find Students
            </button>
            <button
              onClick={() => setSearchTerm('@')}
              className="px-3 py-1 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 text-sm"
            >
              Search by Email
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InitiateVideoCall;