import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import { 
  Users, 
  Search, 
  User,
  MessageCircle,
  Calendar,
  Mail,
  ArrowLeft,
  Filter,
  BookOpen,
  Trash2
} from 'lucide-react';
import toast from 'react-hot-toast';

const MentorStudents = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [students, setStudents] = useState([]);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [interactionFilter, setInteractionFilter] = useState('all');

  useEffect(() => {
    fetchStudents();
  }, []);

  useEffect(() => {
    let filtered = students;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(student =>
        student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.email.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by interaction type
    if (interactionFilter !== 'all') {
      filtered = filtered.filter(student => {
        switch (interactionFilter) {
          case 'active':
            return student.last_interaction && new Date(student.last_interaction) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
          case 'inactive':
            return !student.last_interaction || new Date(student.last_interaction) <= new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
          case 'new':
            return new Date(student.created_at) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
          default:
            return true;
        }
      });
    }

    setFilteredStudents(filtered);
  }, [students, searchTerm, interactionFilter]);

  const fetchStudents = async () => {
    try {
      const response = await api.get('/mentor-portal/students');
      if (response.data.success) {
        setStudents(response.data.students);
      }
    } catch (error) {
      console.error('Failed to fetch students:', error);
      toast.error('Failed to load students');
    } finally {
      setLoading(false);
    }
  };



  const startChat = async (studentId) => {
    try {
      const response = await api.post('/chat/rooms', {
        target_user_id: studentId,
        room_type: 'user_mentor',
        title: 'Mentoring Chat'
      });
      
      if (response.data.success) {
        navigate('/mentor/chats');
        toast.success('Chat started successfully');
      }
    } catch (error) {
      console.error('Failed to start chat:', error);
      toast.error('Failed to start chat');
    }
  };

  const scheduleSession = async (studentId) => {
    try {
      const student = students.find(s => s.id === studentId);
      if (student) {
        navigate('/mentor/sessions', { 
          state: { 
            scheduleFor: {
              email: student.email,
              name: student.name
            }
          }
        });
      }
    } catch (error) {
      console.error('Failed to navigate to schedule:', error);
      toast.error('Failed to open schedule');
    }
  };

  const sendEmail = async (studentId) => {
    try {
      const student = students.find(s => s.id === studentId);
      if (student) {
        const response = await api.post('/mentor-portal/send-email', {
          recipient_email: student.email,
          recipient_name: student.name,
          subject: 'Mentoring Session Follow-up',
          message: `Hello ${student.name},\n\nI hope you're doing well. I wanted to follow up on our mentoring sessions and see if you have any questions or need additional support.\n\nBest regards,\nYour Mentor`
        });
        
        if (response.data.success) {
          toast.success('Email sent successfully');
        }
      }
    } catch (error) {
      console.error('Failed to send email:', error);
      toast.error('Failed to send email');
    }
  };

  const deleteStudent = async (studentId) => {
    if (!window.confirm('Are you sure you want to remove this student from your list? This will not delete their account, but will remove your mentoring relationship.')) {
      return;
    }

    try {
      const response = await api.delete(`/mentor-portal/students/${studentId}`);
      
      if (response.data.success) {
        setStudents(prev => prev.filter(student => student.id !== studentId));
        toast.success('Student removed successfully');
      }
    } catch (error) {
      console.error('Failed to delete student:', error);
      toast.error('Failed to remove student');
    }
  };

  const getInteractionBadge = (type) => {
    switch (type) {
      case 'session':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            <Calendar className="w-3 h-3 mr-1" />
            Sessions
          </span>
        );
      case 'chat':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <MessageCircle className="w-3 h-3 mr-1" />
            Chats
          </span>
        );
      case 'both':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
            <BookOpen className="w-3 h-3 mr-1" />
            Both
          </span>
        );
      default:
        return null;
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading students..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/mentor')}
            className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Students</h1>
          <p className="text-gray-600">Students you've interacted with through sessions and chats</p>
        </div>

        {/* Search and Filters */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search students by name or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select
              value={interactionFilter}
              onChange={(e) => setInteractionFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Interactions</option>
              <option value="session">Sessions Only</option>
              <option value="chat">Chats Only</option>
            </select>
          </div>
        </div>

        {/* Students Grid */}
        {filteredStudents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredStudents.map((student) => (
              <div key={student.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                        <User className="w-6 h-6 text-blue-600" />
                      </div>
                    </div>
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{student.name}</h3>
                      <p className="text-sm text-gray-600">{student.email}</p>
                    </div>
                  </div>
                  {getInteractionBadge(student.interaction_type)}
                </div>

                <div className="space-y-3">
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Joined:</span> {' '}
                    {new Date(student.created_at).toLocaleDateString()}
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={() => startChat(student.id)}
                      className="flex-1 flex items-center justify-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                    >
                      <MessageCircle className="w-4 h-4 mr-2" />
                      Chat
                    </button>
                    
                    <button 
                      onClick={() => scheduleSession(student.id)}
                      className="flex-1 flex items-center justify-center px-3 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
                    >
                      <Calendar className="w-4 h-4 mr-2" />
                      Schedule
                    </button>
                  </div>

                  <div className="flex space-x-2">
                    <button 
                      onClick={() => sendEmail(student.id)}
                      className="flex-1 flex items-center justify-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                    >
                      <Mail className="w-4 h-4 mr-2" />
                      Email
                    </button>
                    <button
                      onClick={() => deleteStudent(student.id)}
                      className="flex items-center justify-center px-3 py-2 border border-red-300 rounded-md text-sm font-medium text-red-700 bg-white hover:bg-red-50"
                      title="Remove student"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No students found</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || interactionFilter !== 'all'
                ? "No students match your current filters."
                : "You haven't interacted with any students yet."
              }
            </p>
            {searchTerm || interactionFilter !== 'all' ? (
              <button
                onClick={() => {
                  setSearchTerm('');
                  setInteractionFilter('all');
                }}
                className="btn-outline"
              >
                Clear Filters
              </button>
            ) : (
              <p className="text-sm text-gray-500">
                Students will appear here after you have sessions or chats with them.
              </p>
            )}
          </div>
        )}

        {/* Statistics */}
        {students.length > 0 && (
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <Users className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Students</p>
                  <p className="text-2xl font-bold text-gray-900">{students.length}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <Calendar className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Session Students</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {students.filter(s => s.interaction_type === 'session' || s.interaction_type === 'both').length}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <MessageCircle className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Chat Students</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {students.filter(s => s.interaction_type === 'chat' || s.interaction_type === 'both').length}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MentorStudents;