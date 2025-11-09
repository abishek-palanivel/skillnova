import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  Video, 
  VideoOff, 
  Mic, 
  MicOff, 
  Phone, 
  PhoneOff, 
  MessageSquare,
  Settings,
  Users,
  Monitor,
  Camera
} from 'lucide-react';
import toast from 'react-hot-toast';

const VideoCall = () => {
  const { callId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [callData, setCallData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [participants, setParticipants] = useState([]);
  
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const localStreamRef = useRef(null);
  const peerConnectionRef = useRef(null);
  const socketRef = useRef(null);

  useEffect(() => {
    if (callId) {
      initializeCall();
    }
    
    return () => {
      cleanup();
    };
  }, [callId]);

  const initializeCall = async () => {
    try {
      // Fetch call details
      const response = await api.get(`/video-calls/${callId}`);
      if (response.data.success) {
        setCallData(response.data.call);
        await setupWebRTC();
        connectToSignalingServer();
      }
    } catch (error) {
      console.error('Failed to initialize call:', error);
      toast.error('Failed to join video call');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const setupWebRTC = async () => {
    try {
      console.log('Setting up WebRTC...');
      
      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });
      
      console.log('Got user media stream:', stream);
      
      localStreamRef.current = stream;
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
      }

      // Initialize video/audio state based on actual tracks
      const videoTrack = stream.getVideoTracks()[0];
      const audioTrack = stream.getAudioTracks()[0];
      
      if (videoTrack) {
        setIsVideoEnabled(videoTrack.enabled);
        console.log('Video track enabled:', videoTrack.enabled);
      }
      
      if (audioTrack) {
        setIsAudioEnabled(audioTrack.enabled);
        console.log('Audio track enabled:', audioTrack.enabled);
      }

      // Create peer connection
      const configuration = {
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' }
        ]
      };
      
      peerConnectionRef.current = new RTCPeerConnection(configuration);
      
      // Add local stream to peer connection
      stream.getTracks().forEach(track => {
        peerConnectionRef.current.addTrack(track, stream);
      });

      // Handle remote stream
      peerConnectionRef.current.ontrack = (event) => {
        console.log('Received remote stream');
        if (remoteVideoRef.current) {
          remoteVideoRef.current.srcObject = event.streams[0];
        }
      };

      // Handle ICE candidates
      peerConnectionRef.current.onicecandidate = (event) => {
        if (event.candidate && socketRef.current) {
          socketRef.current.emit('ice-candidate', {
            callId,
            candidate: event.candidate
          });
        }
      };

      setIsConnected(true);
      console.log('WebRTC setup completed successfully');
    } catch (error) {
      console.error('Failed to setup WebRTC:', error);
      
      // Provide specific error messages
      if (error.name === 'NotAllowedError') {
        toast.error('Camera/microphone access denied. Please allow permissions and refresh.');
      } else if (error.name === 'NotFoundError') {
        toast.error('No camera or microphone found. Please check your devices.');
      } else if (error.name === 'NotReadableError') {
        toast.error('Camera/microphone is being used by another application.');
      } else {
        toast.error('Failed to access camera/microphone. Please check your devices.');
      }
    }
  };

  const connectToSignalingServer = () => {
    // Using Socket.IO for signaling (you'll need to implement this)
    // For now, we'll simulate the connection
    console.log('Connecting to signaling server...');
    
    // Simulate WebSocket connection
    setTimeout(() => {
      setParticipants([
        { id: 1, name: 'You', isLocal: true },
        { id: 2, name: callData?.mentor_name || 'Mentor', isLocal: false }
      ]);
    }, 1000);
  };

  const toggleVideo = () => {
    if (localStreamRef.current) {
      const videoTrack = localStreamRef.current.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsVideoEnabled(videoTrack.enabled);
        
        // Also update the video element visibility
        if (localVideoRef.current) {
          localVideoRef.current.style.display = videoTrack.enabled ? 'block' : 'none';
        }
        
        console.log('Video toggled:', videoTrack.enabled ? 'ON' : 'OFF');
      } else {
        console.error('No video track found');
        toast.error('No video track available');
      }
    } else {
      console.error('No local stream found');
      toast.error('No video stream available');
    }
  };

  const toggleAudio = () => {
    if (localStreamRef.current) {
      const audioTrack = localStreamRef.current.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsAudioEnabled(audioTrack.enabled);
        console.log('Audio toggled:', audioTrack.enabled ? 'ON' : 'OFF');
      } else {
        console.error('No audio track found');
        toast.error('No audio track available');
      }
    } else {
      console.error('No local stream found');
      toast.error('No audio stream available');
    }
  };

  const toggleScreenShare = async () => {
    try {
      if (!isScreenSharing) {
        const screenStream = await navigator.mediaDevices.getDisplayMedia({
          video: true,
          audio: true
        });
        
        // Replace video track with screen share
        const videoTrack = screenStream.getVideoTracks()[0];
        const sender = peerConnectionRef.current.getSenders().find(s => 
          s.track && s.track.kind === 'video'
        );
        
        if (sender) {
          await sender.replaceTrack(videoTrack);
        }
        
        videoTrack.onended = () => {
          stopScreenShare();
        };
        
        setIsScreenSharing(true);
      } else {
        stopScreenShare();
      }
    } catch (error) {
      console.error('Screen share error:', error);
      toast.error('Failed to share screen');
    }
  };

  const stopScreenShare = async () => {
    try {
      // Get camera stream back
      const cameraStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });
      
      const videoTrack = cameraStream.getVideoTracks()[0];
      const sender = peerConnectionRef.current.getSenders().find(s => 
        s.track && s.track.kind === 'video'
      );
      
      if (sender) {
        await sender.replaceTrack(videoTrack);
      }
      
      localStreamRef.current = cameraStream;
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = cameraStream;
      }
      
      setIsScreenSharing(false);
    } catch (error) {
      console.error('Failed to stop screen share:', error);
    }
  };

  const endCall = async () => {
    try {
      await api.post(`/video-calls/${callId}/end`);
      cleanup();
      navigate('/dashboard');
      toast.success('Call ended');
    } catch (error) {
      console.error('Failed to end call:', error);
      cleanup();
      navigate('/dashboard');
    }
  };

  const cleanup = () => {
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop());
    }
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
    }
    if (socketRef.current) {
      socketRef.current.disconnect();
    }
  };

  const sendMessage = () => {
    if (newMessage.trim()) {
      const message = {
        id: Date.now(),
        text: newMessage,
        sender: 'You',
        timestamp: new Date().toLocaleTimeString()
      };
      setChatMessages(prev => [...prev, message]);
      setNewMessage('');
      
      // Send to other participants via WebSocket
      if (socketRef.current) {
        socketRef.current.emit('chat-message', {
          callId,
          message
        });
      }
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 p-4 flex justify-between items-center">
        <div className="text-white">
          <h1 className="text-lg font-semibold">Video Call</h1>
          <p className="text-sm text-gray-300">
            {callData?.title || 'Mentoring Session'}
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center text-white">
            <Users className="w-4 h-4 mr-2" />
            <span>{participants.length} participants</span>
          </div>
          <div className="flex items-center text-green-400">
            <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
            <span className="text-sm">Connected</span>
          </div>
        </div>
      </div>

      {/* Video Area */}
      <div className="flex-1 flex">
        {/* Main Video Area */}
        <div className="flex-1 relative">
          {/* Remote Video */}
          <video
            ref={remoteVideoRef}
            autoPlay
            playsInline
            className="w-full h-full object-cover bg-gray-800"
          />
          
          {/* Local Video (Picture-in-Picture) */}
          <div className="absolute top-4 right-4 w-48 h-36 bg-gray-700 rounded-lg overflow-hidden relative">
            <video
              ref={localVideoRef}
              autoPlay
              playsInline
              muted
              className={`w-full h-full object-cover transition-opacity duration-300 ${
                isVideoEnabled ? 'opacity-100' : 'opacity-0'
              }`}
            />
            {!isVideoEnabled && (
              <div className="absolute inset-0 bg-gray-800 flex flex-col items-center justify-center">
                <VideoOff className="w-8 h-8 text-gray-400 mb-2" />
                <span className="text-xs text-gray-400">Camera Off</span>
              </div>
            )}
          </div>

          {/* Participant Info */}
          <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 text-white px-3 py-2 rounded-lg">
            <p className="text-sm">{callData?.mentor_name || 'Mentor'}</p>
          </div>
        </div>

        {/* Chat Sidebar */}
        {showChat && (
          <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <h3 className="font-semibold">Chat</h3>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {chatMessages.map((message) => (
                <div key={message.id} className="flex flex-col">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">{message.sender}</span>
                    <span className="text-xs text-gray-500">{message.timestamp}</span>
                  </div>
                  <p className="text-sm text-gray-700 mt-1">{message.text}</p>
                </div>
              ))}
            </div>
            
            <div className="p-4 border-t border-gray-200">
              <div className="flex">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Type a message..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={sendMessage}
                  className="px-4 py-2 bg-blue-600 text-white rounded-r-md hover:bg-blue-700"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="bg-gray-800 p-4">
        <div className="flex justify-center items-center space-x-4">
          {/* Audio Toggle */}
          <button
            onClick={toggleAudio}
            className={`p-3 rounded-full ${
              isAudioEnabled 
                ? 'bg-gray-600 hover:bg-gray-500' 
                : 'bg-red-600 hover:bg-red-500'
            } text-white transition-colors`}
          >
            {isAudioEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
          </button>

          {/* Video Toggle */}
          <button
            onClick={toggleVideo}
            className={`p-3 rounded-full ${
              isVideoEnabled 
                ? 'bg-gray-600 hover:bg-gray-500' 
                : 'bg-red-600 hover:bg-red-500'
            } text-white transition-colors`}
          >
            {isVideoEnabled ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
          </button>

          {/* Screen Share */}
          <button
            onClick={toggleScreenShare}
            className={`p-3 rounded-full ${
              isScreenSharing 
                ? 'bg-blue-600 hover:bg-blue-500' 
                : 'bg-gray-600 hover:bg-gray-500'
            } text-white transition-colors`}
          >
            <Monitor className="w-5 h-5" />
          </button>

          {/* Chat Toggle */}
          <button
            onClick={() => setShowChat(!showChat)}
            className={`p-3 rounded-full ${
              showChat 
                ? 'bg-blue-600 hover:bg-blue-500' 
                : 'bg-gray-600 hover:bg-gray-500'
            } text-white transition-colors`}
          >
            <MessageSquare className="w-5 h-5" />
          </button>

          {/* End Call */}
          <button
            onClick={endCall}
            className="p-3 rounded-full bg-red-600 hover:bg-red-500 text-white transition-colors"
          >
            <PhoneOff className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default VideoCall;