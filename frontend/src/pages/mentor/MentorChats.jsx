import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import LoadingSpinner from '../../components/LoadingSpinner';
import { 
  MessageCircle, 
  Search, 
  Clock, 
  User,
  Send,
  ArrowLeft,
  Trash2,
  MoreVertical
} from 'lucide-react';
import toast from 'react-hot-toast';

const MentorChats = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [chats, setChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const chatIntervalRef = useRef(null);
  const messageIntervalRef = useRef(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);
  const [deletingMessage, setDeletingMessage] = useState(null);

  useEffect(() => {
    fetchChats();
    
    // Clear existing intervals
    if (chatIntervalRef.current) {
      clearInterval(chatIntervalRef.current);
    }
    if (messageIntervalRef.current) {
      clearInterval(messageIntervalRef.current);
    }
    
    // Set up polling for chat updates
    chatIntervalRef.current = setInterval(() => {
      fetchChats();
    }, 3000); // Check for chat updates every 3 seconds
    
    // Set up message polling if chat is selected
    if (selectedChat) {
      messageIntervalRef.current = setInterval(() => {
        fetchMessages(selectedChat.id);
      }, 2000); // Check for new messages every 2 seconds
    }
    
    return () => {
      if (chatIntervalRef.current) {
        clearInterval(chatIntervalRef.current);
      }
      if (messageIntervalRef.current) {
        clearInterval(messageIntervalRef.current);
      }
    };
  }, [selectedChat]);

  const fetchChats = async () => {
    try {
      const response = await api.get('/chat/rooms');
      if (response.data.success) {
        setChats(response.data.rooms.map(room => ({
          id: room.id,
          title: room.title,
          user_name: room.other_participant?.name || 'Unknown',
          user_email: room.other_participant?.email || '',
          user_role: room.other_participant?.role || 'User',
          last_message: room.last_message || { text: '', created_at: '' },
          unread_count: room.unread_count || 0,
          created_at: room.created_at,
          updated_at: room.updated_at
        })));
      } else {
        console.error('Failed to fetch chats:', response.data.message);
        toast.error(response.data.message || 'Failed to load chats');
      }
    } catch (error) {
      console.error('Failed to fetch chats:', error);
      toast.error('Failed to load chats');
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (chatId) => {
    try {
      const response = await api.get(`/chat/rooms/${chatId}/messages`);
      if (response.data.success) {
        setMessages(response.data.messages || []);
      } else {
        console.error('Failed to fetch messages:', response.data.message);
        toast.error(response.data.message || 'Failed to load messages');
      }
    } catch (error) {
      console.error('Failed to fetch messages:', error);
      const errorMessage = error.response?.data?.message || 'Failed to load messages';
      toast.error(errorMessage);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedChat) return;

    try {
      const response = await api.post(`/chat/rooms/${selectedChat.id}/messages`, {
        message_text: newMessage.trim()
      });
      
      if (response.data.success) {
        setMessages(prev => [...prev, response.data.message]);
        setNewMessage('');
        // Update chat list with new message
        fetchChats();
      } else {
        console.error('Failed to send message:', response.data.message);
        toast.error(response.data.message || 'Failed to send message');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage = error.response?.data?.message || 'Failed to send message';
      toast.error(errorMessage);
    }
  };

  const handleChatSelect = (chat) => {
    setSelectedChat(chat);
    fetchMessages(chat.id);
  };

  const deleteMessage = async (messageId) => {
    try {
      setDeletingMessage(messageId);
      const response = await api.delete(`/chat/messages/${messageId}`);
      
      if (response.data.success) {
        setMessages(prev => prev.filter(msg => msg.id !== messageId));
        toast.success('Message deleted');
        if (selectedChat) {
          fetchMessages(selectedChat.id);
        }
      } else {
        toast.error(response.data.message || 'Failed to delete message');
      }
    } catch (error) {
      console.error('Failed to delete message:', error);
      toast.error(error.response?.data?.message || 'Failed to delete message');
    } finally {
      setDeletingMessage(null);
      setShowDeleteConfirm(null);
    }
  };

  const deleteChatRoom = async (roomId) => {
    try {
      const response = await api.delete(`/chat/rooms/${roomId}`);
      
      if (response.data.success) {
        setChats(prev => prev.filter(chat => chat.id !== roomId));
        if (selectedChat && selectedChat.id === roomId) {
          setSelectedChat(null);
          setMessages([]);
        }
        toast.success('Chat deleted');
        fetchChats();
      } else {
        toast.error(response.data.message || 'Failed to delete chat');
      }
    } catch (error) {
      console.error('Failed to delete chat room:', error);
      toast.error(error.response?.data?.message || 'Failed to delete chat');
    } finally {
      setShowDeleteConfirm(null);
    }
  };

  const filteredChats = chats.filter(chat =>
    chat.user_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    chat.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <LoadingSpinner text="Loading chats..." />;
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Student Chats</h1>
          <p className="text-gray-600">Communicate with your students</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="flex h-96">
            {/* Chat List */}
            <div className="w-1/3 border-r border-gray-200">
              <div className="p-4 border-b border-gray-200">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search chats..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              
              <div className="overflow-y-auto h-80">
                {filteredChats.length > 0 ? (
                  filteredChats.map((chat) => (
                    <div
                      key={chat.id}
                      className={`p-4 border-b border-gray-100 hover:bg-gray-50 group ${
                        selectedChat?.id === chat.id ? 'bg-blue-50 border-blue-200' : ''
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <User className="w-5 h-5 text-blue-600" />
                          </div>
                        </div>
                        <div 
                          onClick={() => handleChatSelect(chat)}
                          className="flex-1 min-w-0 cursor-pointer"
                        >
                          <div className="flex items-center space-x-2">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {chat.user_name}
                            </p>
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              chat.user_role === 'Administrator' ? 'bg-red-100 text-red-600' :
                              chat.user_role === 'Mentor' ? 'bg-blue-100 text-blue-600' :
                              'bg-green-100 text-green-600'
                            }`}>
                              {chat.user_role}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 truncate">
                            {chat.last_message.text || 'No messages yet'}
                          </p>
                          <div className="flex items-center justify-between mt-1">
                            <p className="text-xs text-gray-500">
                              {chat.last_message.created_at ? 
                                new Date(chat.last_message.created_at).toLocaleDateString() : 
                                new Date(chat.created_at).toLocaleDateString()
                              }
                            </p>
                            {chat.unread_count > 0 && (
                              <span className="bg-blue-600 text-white text-xs rounded-full px-2 py-1">
                                {chat.unread_count}
                              </span>
                            )}
                          </div>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setShowDeleteConfirm(`room-${chat.id}`);
                          }}
                          className="opacity-0 group-hover:opacity-100 p-1 text-red-500 hover:text-red-700 transition-opacity"
                          title="Delete chat"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-8 text-center">
                    <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-600">No chats found</p>
                  </div>
                )}
              </div>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 flex flex-col">
              {selectedChat ? (
                <>
                  {/* Chat Header */}
                  <div className="p-4 border-b border-gray-200 bg-gray-50">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <User className="w-4 h-4 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900">{selectedChat.user_name}</h3>
                        <p className="text-sm text-gray-600">{selectedChat.user_email}</p>
                      </div>
                    </div>
                  </div>

                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.length > 0 ? (
                      messages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex ${message.is_own ? 'justify-end' : 'justify-start'} group`}
                        >
                          <div className="flex items-end space-x-2 max-w-xs lg:max-w-md">
                            {message.is_own && (
                              <button
                                onClick={() => setShowDeleteConfirm(message.id)}
                                className="opacity-0 group-hover:opacity-100 p-1 text-red-500 hover:text-red-700 transition-opacity"
                                title="Delete message"
                              >
                                <Trash2 className="w-3 h-3" />
                              </button>
                            )}
                            <div
                              className={`px-4 py-2 rounded-lg ${
                                message.is_own
                                  ? 'bg-blue-600 text-white'
                                  : 'bg-gray-200 text-gray-900'
                              }`}
                            >
                              {!message.is_own && (
                                <p className="text-xs font-medium mb-1 opacity-75">
                                  {message.sender.name}
                                </p>
                              )}
                              <p className="text-sm">{message.message_text}</p>
                              <p className={`text-xs mt-1 ${
                                message.is_own ? 'text-blue-100' : 'text-gray-500'
                              }`}>
                                {new Date(message.created_at).toLocaleTimeString()}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                        <p className="text-gray-600">No messages yet. Start the conversation!</p>
                      </div>
                    )}
                  </div>

                  {/* Message Input */}
                  <div className="p-4 border-t border-gray-200">
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                        placeholder="Type your message..."
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <button
                        onClick={sendMessage}
                        disabled={!newMessage.trim()}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Send className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Select a chat</h3>
                    <p className="text-gray-600">Choose a conversation from the list to start messaging</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-80">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-red-100 rounded-full">
                <Trash2 className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {showDeleteConfirm.startsWith('room-') ? 'Delete Chat' : 'Delete Message'}
                </h3>
                <p className="text-sm text-gray-600">
                  {showDeleteConfirm.startsWith('room-') 
                    ? 'This will delete the entire conversation and all messages.'
                    : 'This message will be permanently deleted.'
                  }
                </p>
              </div>
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (showDeleteConfirm.startsWith('room-')) {
                    const roomId = showDeleteConfirm.replace('room-', '');
                    deleteChatRoom(roomId);
                  } else {
                    deleteMessage(showDeleteConfirm);
                  }
                }}
                disabled={deletingMessage === showDeleteConfirm}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {deletingMessage === showDeleteConfirm ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MentorChats;