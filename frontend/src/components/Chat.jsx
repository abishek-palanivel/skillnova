import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import ChatRating from './ChatRating';
import { 
  MessageCircle, 
  Send, 
  Users, 
  UserPlus,
  X,
  Minimize2,
  Maximize2,
  Star,
  Trash2,
  MoreVertical
} from 'lucide-react';
import toast from 'react-hot-toast';

const Chat = () => {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [chatRooms, setChatRooms] = useState([]);
  const [activeRoom, setActiveRoom] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [availableMentors, setAvailableMentors] = useState([]);
  const [availableAdmins, setAvailableAdmins] = useState([]);
  const [availableUsers, setAvailableUsers] = useState([]);
  const [showNewChatModal, setShowNewChatModal] = useState(false);
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);
  const messageIntervalRef = useRef(null);
  const roomIntervalRef = useRef(null);
  const lastMessageCount = useRef(0);
  const [debugMode] = useState(process.env.NODE_ENV === 'development');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);
  const [deletingMessage, setDeletingMessage] = useState(null);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      fetchChatRooms();
      fetchAvailableMentors();
      fetchAvailableAdmins();
      if (user && (user.is_admin || user.is_mentor)) {
        fetchAvailableUsers();
      }
      
      // Clear existing interval
      if (roomIntervalRef.current) {
        clearInterval(roomIntervalRef.current);
      }
      
      // Set up polling for chat room updates
      roomIntervalRef.current = setInterval(() => {
        fetchChatRooms();
      }, 3000); // Check for new rooms/messages every 3 seconds
      
      return () => {
        if (roomIntervalRef.current) {
          clearInterval(roomIntervalRef.current);
        }
      };
    } else {
      // Clear interval when chat is closed
      if (roomIntervalRef.current) {
        clearInterval(roomIntervalRef.current);
      }
    }
  }, [isOpen, isMinimized]);

  useEffect(() => {
    if (activeRoom) {
      fetchMessages(activeRoom.id);
      lastMessageCount.current = 0;
      
      // Clear existing message interval
      if (messageIntervalRef.current) {
        clearInterval(messageIntervalRef.current);
      }
      
      // Set up polling for new messages
      messageIntervalRef.current = setInterval(() => {
        fetchMessages(activeRoom.id, true); // Silent fetch to avoid loading indicators
      }, 2000); // Check for new messages every 2 seconds
      
      return () => {
        if (messageIntervalRef.current) {
          clearInterval(messageIntervalRef.current);
        }
      };
    } else {
      // Clear interval when no active room
      if (messageIntervalRef.current) {
        clearInterval(messageIntervalRef.current);
      }
    }
  }, [activeRoom]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchChatRooms = async () => {
    try {
      const response = await api.get('/chat/rooms');
      if (response.data.success) {
        setChatRooms(response.data.rooms);
      }
    } catch (error) {
      console.error('Failed to fetch chat rooms:', error);
    }
  };

  const fetchMessages = async (roomId, silent = false) => {
    try {
      if (!silent) setLoading(true);
      const response = await api.get(`/chat/rooms/${roomId}/messages`);
      if (response.data.success) {
        const newMessages = response.data.messages || [];
        
        // Check if we have new messages
        if (newMessages.length > lastMessageCount.current) {
          // Show notification for new messages (except first load)
          if (lastMessageCount.current > 0 && newMessages.length > messages.length) {
            const newMessageCount = newMessages.length - lastMessageCount.current;
            if (debugMode) {
              console.log(`${newMessageCount} new message(s) received!`);
            }
            
            // Show a subtle notification for new messages
            if (newMessageCount > 0) {
              toast.success(`${newMessageCount} new message${newMessageCount > 1 ? 's' : ''} received`, {
                duration: 2000,
                position: 'bottom-left'
              });
            }
          }
          lastMessageCount.current = newMessages.length;
        }
        
        setMessages(newMessages);
      } else {
        if (!silent) {
          console.error('Failed to fetch messages:', response.data.message);
          toast.error(response.data.message || 'Failed to load messages');
        }
      }
    } catch (error) {
      if (!silent) {
        console.error('Failed to fetch messages:', error);
        const errorMessage = error.response?.data?.message || 'Failed to load messages';
        toast.error(errorMessage);
      }
    } finally {
      if (!silent) setLoading(false);
    }
  };

  const fetchAvailableMentors = async () => {
    try {
      const response = await api.get('/chat/mentors');
      if (response.data.success) {
        setAvailableMentors(response.data.mentors);
      }
    } catch (error) {
      console.error('Failed to fetch mentors:', error);
    }
  };

  const fetchAvailableAdmins = async () => {
    try {
      const response = await api.get('/chat/admins');
      if (response.data.success) {
        setAvailableAdmins(response.data.admins);
      }
    } catch (error) {
      console.error('Failed to fetch admins:', error);
    }
  };

  const fetchAvailableUsers = async () => {
    try {
      const response = await api.get('/chat/users');
      if (response.data.success) {
        setAvailableUsers(response.data.users);
      }
    } catch (error) {
      console.error('Failed to fetch users:', error);
    }
  };

  const createChatRoom = async (targetUserId, targetUserName) => {
    try {
      const response = await api.post('/chat/rooms', {
        target_user_id: targetUserId,
        title: `Chat with ${targetUserName}`
      });
      
      if (response.data.success) {
        toast.success('Chat room created successfully');
        setShowNewChatModal(false);
        fetchChatRooms();
        
        // Find and select the new room after refresh
        setTimeout(() => {
          fetchChatRooms().then(() => {
            const newRoom = chatRooms.find(room => room.id === response.data.room.id);
            if (newRoom) {
              setActiveRoom(newRoom);
            }
          });
        }, 500);
      } else {
        toast.error(response.data.message || 'Failed to create chat room');
      }
    } catch (error) {
      console.error('Failed to create chat room:', error);
      toast.error(error.response?.data?.message || 'Failed to create chat room');
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !activeRoom || sending) return;

    try {
      setSending(true);
      const response = await api.post(`/chat/rooms/${activeRoom.id}/messages`, {
        message_text: newMessage.trim()
      });
      
      if (response.data.success) {
        // Add message to local state immediately
        setMessages(prev => [...prev, response.data.message]);
        setNewMessage('');
        lastMessageCount.current += 1;
        
        // Refresh chat rooms to update last message
        fetchChatRooms();
        
        // Force refresh messages after a short delay to ensure sync
        setTimeout(() => {
          fetchMessages(activeRoom.id, true);
        }, 500);
        
        toast.success('Message sent!');
      } else {
        console.error('Failed to send message:', response.data.message);
        toast.error(response.data.message || 'Failed to send message');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage = error.response?.data?.message || 'Failed to send message';
      toast.error(errorMessage);
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const deleteMessage = async (messageId) => {
    try {
      setDeletingMessage(messageId);
      const response = await api.delete(`/chat/messages/${messageId}`);
      
      if (response.data.success) {
        // Remove message from local state
        setMessages(prev => prev.filter(msg => msg.id !== messageId));
        toast.success('Message deleted');
        // Refresh messages to ensure sync
        if (activeRoom) {
          fetchMessages(activeRoom.id, true);
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
        // Remove room from local state
        setChatRooms(prev => prev.filter(room => room.id !== roomId));
        // Clear active room if it was deleted
        if (activeRoom && activeRoom.id === roomId) {
          setActiveRoom(null);
          setMessages([]);
        }
        toast.success('Chat deleted');
        fetchChatRooms(); // Refresh rooms
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

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsOpen(true)}
          className="bg-blue-600 text-white p-4 rounded-full shadow-xl hover:bg-blue-700 transition-all duration-200 hover:scale-105 border-2 border-white relative"
          title="Chat Support"
        >
          <MessageCircle className="w-7 h-7" />
          {chatRooms.some(room => room.unread_count > 0) && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {chatRooms.reduce((total, room) => total + room.unread_count, 0)}
            </span>
          )}
        </button>
      </div>
    );
  }

  return (
    <div className={`fixed bottom-6 right-6 z-50 bg-white rounded-lg shadow-xl border border-gray-200 ${
      isMinimized ? 'w-80 h-12' : 'w-96 h-[500px]'
    } transition-all duration-300`}>
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200 bg-blue-600 text-white rounded-t-lg">
        <div className="flex items-center space-x-2">
          <MessageCircle className="w-5 h-5" />
          <span className="font-medium">
            {activeRoom ? activeRoom.title : 'Chat Support'}
          </span>
          {debugMode && activeRoom && (
            <span className="text-xs bg-blue-500 px-2 py-1 rounded">
              {messages.length} msgs
            </span>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {activeRoom && (
            <button
              onClick={() => fetchMessages(activeRoom.id)}
              className="p-1 hover:bg-blue-700 rounded"
              title="Refresh messages"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          )}
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-1 hover:bg-blue-700 rounded"
          >
            {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="p-1 hover:bg-blue-700 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <div className="flex h-[420px]">
          {/* Chat Rooms Sidebar */}
          <div className="w-1/3 border-r border-gray-200 bg-gray-50">
            <div className="p-3 border-b border-gray-200">
              <button
                onClick={() => setShowNewChatModal(true)}
                className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              >
                <UserPlus className="w-4 h-4" />
                <span>New Chat</span>
              </button>
            </div>
            
            <div className="overflow-y-auto h-80">
              {chatRooms.length > 0 ? (
                chatRooms.map((room, index) => (
                  <div
                    key={`${room.id}-${index}`}
                    className={`p-3 border-b border-gray-100 hover:bg-gray-100 group ${
                      activeRoom?.id === room.id ? 'bg-blue-50 border-l-4 border-l-blue-600' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div 
                        onClick={() => setActiveRoom(room)}
                        className="flex-1 cursor-pointer"
                      >
                        <div className="flex items-center justify-between">
                          <p className="font-medium text-sm text-gray-900 truncate">
                            {room.other_participant?.name || 'Unknown'}
                          </p>
                          {room.unread_count > 0 && (
                            <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1">
                              {room.unread_count}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-600 truncate mt-1">
                          {room.last_message?.text || 'No messages yet'}
                        </p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setShowDeleteConfirm(`room-${room.id}`);
                        }}
                        className="opacity-0 group-hover:opacity-100 p-1 text-red-500 hover:text-red-700 transition-opacity ml-2"
                        title="Delete chat"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-4 text-center text-gray-500 text-sm">
                  No chats yet. Start a new conversation!
                </div>
              )}
            </div>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 flex flex-col">
            {activeRoom ? (
              <>
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-3 space-y-3">
                  {loading ? (
                    <div className="text-center text-gray-500 text-sm">Loading messages...</div>
                  ) : messages.length > 0 ? (
                    messages.map((message, index) => (
                      <div
                        key={`${message.id}-${index}`}
                        className={`flex ${message.is_own ? 'justify-end' : 'justify-start'} group`}
                      >
                        <div className="flex items-end space-x-2 max-w-xs">
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
                            className={`px-3 py-2 rounded-lg text-sm ${
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
                            <p>{message.message_text}</p>
                            <p className={`text-xs mt-1 ${
                              message.is_own ? 'text-blue-100' : 'text-gray-500'
                            }`}>
                              {new Date(message.created_at).toLocaleTimeString()}
                            </p>
                          </div>
                          {!message.is_own && user?.is_admin && (
                            <button
                              onClick={() => setShowDeleteConfirm(message.id)}
                              className="opacity-0 group-hover:opacity-100 p-1 text-red-500 hover:text-red-700 transition-opacity"
                              title="Delete message (Admin)"
                            >
                              <Trash2 className="w-3 h-3" />
                            </button>
                          )}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center text-gray-500 text-sm">
                      No messages yet. Start the conversation!
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Message Input */}
                <div className="p-3 border-t border-gray-200">
                  <div className="flex space-x-2 mb-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Type a message..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <button
                      onClick={sendMessage}
                      disabled={!newMessage.trim() || sending}
                      className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                    >
                      {sending ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                  {activeRoom && activeRoom.room_type === 'user_mentor' && (
                    <button
                      onClick={() => setShowRatingModal(true)}
                      className="w-full flex items-center justify-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg transition-colors"
                    >
                      <Star className="w-4 h-4" />
                      <span>Rate this conversation</span>
                    </button>
                  )}
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
                Select a chat to start messaging
              </div>
            )}
          </div>
        </div>
      )}

      {/* New Chat Modal */}
      {showNewChatModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 max-h-96 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Start New Chat</h3>
              <button
                onClick={() => setShowNewChatModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Show different options based on user role */}
            {user && (user.is_admin || user.is_mentor) ? (
              /* Admins and Mentors can chat with anyone */
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Start Chat With</h4>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {availableUsers.length > 0 ? availableUsers.map((targetUser) => (
                    <div
                      key={targetUser.id}
                      onClick={() => createChatRoom(targetUser.id, targetUser.name)}
                      className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                    >
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        targetUser.is_admin ? 'bg-red-100' : 
                        targetUser.is_mentor ? 'bg-blue-100' : 'bg-green-100'
                      }`}>
                        <span className={`text-sm font-medium ${
                          targetUser.is_admin ? 'text-red-600' : 
                          targetUser.is_mentor ? 'text-blue-600' : 'text-green-600'
                        }`}>
                          {targetUser.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{targetUser.name}</p>
                        <p className="text-sm text-gray-600">{targetUser.role}</p>
                      </div>
                    </div>
                  )) : (
                    <p className="text-sm text-gray-500 text-center py-4">No users available</p>
                  )}
                </div>
              </div>
            ) : (
              /* Regular users see mentors and admins separately */
              <>
                {/* Mentors */}
                <div className="mb-6">
                  <h4 className="font-medium text-gray-900 mb-3">Chat with Mentors</h4>
                  <div className="space-y-2">
                    {availableMentors.length > 0 ? availableMentors.map((mentor) => (
                      <div
                        key={mentor.id}
                        onClick={() => createChatRoom(mentor.id, mentor.name)}
                        className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                      >
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-sm font-medium text-blue-600">
                            {mentor.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{mentor.name}</p>
                          <p className="text-sm text-gray-600">{mentor.expertise_areas || 'Mentor'}</p>
                        </div>
                      </div>
                    )) : (
                      <p className="text-sm text-gray-500 text-center py-4">No mentors available</p>
                    )}
                  </div>
                </div>

                {/* Admins */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Chat with Support</h4>
                  <div className="space-y-2">
                    {availableAdmins.length > 0 ? availableAdmins.map((admin) => (
                      <div
                        key={admin.id}
                        onClick={() => createChatRoom(admin.id, admin.name)}
                        className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                      >
                        <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                          <span className="text-sm font-medium text-red-600">
                            {admin.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{admin.name}</p>
                          <p className="text-sm text-gray-600">{admin.role || 'Administrator'}</p>
                        </div>
                      </div>
                    )) : (
                      <p className="text-sm text-gray-500 text-center py-4">No support staff available</p>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Rating Modal */}
      {showRatingModal && activeRoom && (
        <ChatRating
          roomId={activeRoom.id}
          onClose={() => setShowRatingModal(false)}
          onRatingSubmitted={(rating, feedback) => {
            // Update the active room with rating info
            setActiveRoom(prev => ({
              ...prev,
              rating,
              feedback
            }));
          }}
        />
      )}

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

export default Chat;