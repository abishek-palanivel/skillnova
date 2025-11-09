import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  Award, 
  Download, 
  Share2, 
  CheckCircle,
  Calendar,
  User,
  BookOpen,
  Star,
  ArrowLeft,
  ExternalLink
} from 'lucide-react';
import toast from 'react-hot-toast';

const Certificate = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [certificates, setCertificates] = useState([]);
  const [selectedCertificate, setSelectedCertificate] = useState(null);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchCertificates();
  }, [user]);

  const fetchCertificates = async () => {
    try {
      const response = await api.get('/tests/certificates');
      if (response.data.success) {
        setCertificates(response.data.certificates);
        
        // If courseId is provided, find the specific certificate
        if (courseId) {
          const courseCert = response.data.certificates.find(
            cert => cert.id === courseId || cert.course_title.toLowerCase().includes(courseId.toLowerCase())
          );
          if (courseCert) {
            setSelectedCertificate(courseCert);
          }
        } else if (response.data.certificates.length > 0) {
          setSelectedCertificate(response.data.certificates[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch certificates:', error);
      toast.error('Failed to load certificates');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (certificateNumber) => {
    try {
      const response = await fetch(`/api/tests/certificates/download/${certificateNumber}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `certificate_${certificateNumber}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        toast.success('Certificate downloaded successfully!');
      } else {
        throw new Error('Download failed');
      }
    } catch (error) {
      toast.error('Failed to download certificate');
    }
  };

  const handleShare = async (certificate) => {
    const shareData = {
      title: `${user.name}'s Certificate - ${certificate.course_title}`,
      text: `I've successfully completed ${certificate.course_title} with a score of ${certificate.final_score}%!`,
      url: `${window.location.origin}/verify/${certificate.certificate_number}`
    };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
      } catch (error) {
        console.log('Share cancelled');
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(
        `${shareData.text} Verify at: ${shareData.url}`
      );
      toast.success('Certificate details copied to clipboard!');
    }
  };

  const getGradeColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const getGradeBadge = (score) => {
    if (score >= 90) return { text: 'Distinction', color: 'bg-green-100 text-green-800' };
    if (score >= 80) return { text: 'Merit', color: 'bg-blue-100 text-blue-800' };
    if (score >= 70) return { text: 'Credit', color: 'bg-yellow-100 text-yellow-800' };
    return { text: 'Pass', color: 'bg-gray-100 text-gray-800' };
  };

  if (loading) {
    return <LoadingSpinner text="Loading certificates..." />;
  }

  if (certificates.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back</span>
          </button>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <Award className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">No Certificates Yet</h1>
            <p className="text-gray-600 mb-6">
              Complete courses and pass final tests to earn certificates.
            </p>
            <button
              onClick={() => navigate('/courses')}
              className="btn-primary"
            >
              Browse Courses
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back</span>
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Certificate List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                My Certificates ({certificates.length})
              </h2>
              
              <div className="space-y-3">
                {certificates.map((cert) => {
                  const grade = getGradeBadge(cert.final_score);
                  return (
                    <div
                      key={cert.certificate_id}
                      onClick={() => setSelectedCertificate(cert)}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        selectedCertificate?.certificate_id === cert.certificate_id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-medium text-gray-900 text-sm">
                          {cert.course_title}
                        </h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded ${grade.color}`}>
                          {grade.text}
                        </span>
                      </div>
                      
                      <div className="space-y-1 text-xs text-gray-600">
                        <div className="flex items-center space-x-1">
                          <Star className="w-3 h-3" />
                          <span>Score: {cert.final_score}%</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>{new Date(cert.issued_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Certificate Details */}
          <div className="lg:col-span-2">
            {selectedCertificate ? (
              <div className="space-y-6">
                {/* Certificate Preview */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                  {/* Certificate Header */}
                  <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8 text-center">
                    <Award className="w-16 h-16 mx-auto mb-4 opacity-90" />
                    <h1 className="text-2xl font-bold mb-2">Certificate of Completion</h1>
                    <p className="text-blue-100">SkillNova Learning Platform</p>
                  </div>

                  {/* Certificate Body */}
                  <div className="p-8">
                    <div className="text-center mb-8">
                      <p className="text-gray-600 mb-4">This is to certify that</p>
                      <h2 className="text-3xl font-bold text-gray-900 mb-4 border-b-2 border-gray-200 pb-2 inline-block">
                        {user.name}
                      </h2>
                      <p className="text-gray-600 mb-2">has successfully completed the course</p>
                      <h3 className="text-xl font-semibold text-blue-600 mb-6">
                        {selectedCertificate.course_title}
                      </h3>
                    </div>

                    {/* Achievement Details */}
                    <div className="grid grid-cols-2 gap-6 mb-8">
                      <div className="text-center p-4 bg-gray-50 rounded-lg">
                        <div className={`text-2xl font-bold ${getGradeColor(selectedCertificate.final_score)}`}>
                          {selectedCertificate.final_score}%
                        </div>
                        <p className="text-gray-600 text-sm">Final Score</p>
                      </div>
                      <div className="text-center p-4 bg-gray-50 rounded-lg">
                        <div className="text-2xl font-bold text-gray-900">
                          {getGradeBadge(selectedCertificate.final_score).text}
                        </div>
                        <p className="text-gray-600 text-sm">Achievement Level</p>
                      </div>
                    </div>

                    {/* Certificate Footer */}
                    <div className="border-t border-gray-200 pt-6">
                      <div className="grid grid-cols-2 gap-6 text-sm text-gray-600">
                        <div>
                          <p><strong>Certificate Number:</strong></p>
                          <p className="font-mono">{selectedCertificate.certificate_number}</p>
                        </div>
                        <div>
                          <p><strong>Issue Date:</strong></p>
                          <p>{new Date(selectedCertificate.issued_at).toLocaleDateString()}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Certificate Actions</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button
                      onClick={() => handleDownload(selectedCertificate.certificate_number)}
                      className="flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download PDF</span>
                    </button>
                    
                    <button
                      onClick={() => handleShare(selectedCertificate)}
                      className="flex items-center justify-center space-x-2 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <Share2 className="w-4 h-4" />
                      <span>Share</span>
                    </button>
                    
                    <button
                      onClick={() => window.open(`/verify/${selectedCertificate.certificate_number}`, '_blank')}
                      className="flex items-center justify-center space-x-2 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                      <span>Verify</span>
                    </button>
                  </div>
                </div>

                {/* Certificate Info */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">About This Certificate</h3>
                  
                  <div className="space-y-4">
                    <div className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                      <div>
                        <p className="font-medium text-gray-900">Verified Achievement</p>
                        <p className="text-gray-600 text-sm">
                          This certificate represents successful completion of all course requirements
                          with a passing score of 60% or higher.
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-start space-x-3">
                      <User className="w-5 h-5 text-blue-600 mt-0.5" />
                      <div>
                        <p className="font-medium text-gray-900">Personal Achievement</p>
                        <p className="text-gray-600 text-sm">
                          This certificate is issued specifically to {user.name} and cannot be transferred.
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-start space-x-3">
                      <BookOpen className="w-5 h-5 text-purple-600 mt-0.5" />
                      <div>
                        <p className="font-medium text-gray-900">Skills Validated</p>
                        <p className="text-gray-600 text-sm">
                          Completion demonstrates proficiency in Java programming concepts,
                          object-oriented programming, and software development practices.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
                <Award className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-600">Select a certificate to view details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Certificate;