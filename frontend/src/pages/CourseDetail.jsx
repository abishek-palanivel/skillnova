import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  BookOpen, 
  Clock, 
  Users, 
  Star, 
  Play,
  CheckCircle,
  Lock,
  ArrowLeft,
  Award,
  Target,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

const CourseDetail = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [course, setCourse] = useState(null);
  const [modules, setModules] = useState([]);
  const [enrollment, setEnrollment] = useState(null);
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [certificate, setCertificate] = useState(null);
  const [completedModules, setCompletedModules] = useState(new Set());
  const [expandedModules, setExpandedModules] = useState(new Set());
  const [moduleTestResults, setModuleTestResults] = useState({});
  const [learningPath, setLearningPath] = useState(null);
  const [showLearningPath, setShowLearningPath] = useState(false);
  const [finalTestCompleted, setFinalTestCompleted] = useState(false);
  const [finalTestScore, setFinalTestScore] = useState(null);
  const [finalProject, setFinalProject] = useState(null);
  const [finalProjectSubmission, setFinalProjectSubmission] = useState(null);
  const [courseUnlocked, setCourseUnlocked] = useState(true);

  useEffect(() => {
    if (courseId) {
      fetchCourseDetails();
      if (user) {
        checkEnrollment();
        fetchFinalProject();
      }
    }
    
    // Handle test results from navigation state
    if (location.state?.testResult) {
      const { testResult } = location.state;
      handleTestCompletion(testResult.moduleId, testResult);
      // Clear the state to prevent re-processing
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [courseId, user, location.state]);

  const fetchCourseDetails = async () => {
    try {
      const response = await api.get(`/courses/${courseId}`);
      if (response.data.success) {
        setCourse(response.data.course);
      }
    } catch (error) {
      console.error('Failed to fetch course details:', error);
      toast.error('Failed to load course details');
      navigate('/courses');
    } finally {
      setLoading(false);
    }
  };

  const checkEnrollment = async () => {
    try {
      console.log('🔍 Checking enrollment for course:', courseId);
      const response = await api.get('/courses/my-courses');
      console.log('📝 My courses response:', response.data);
      if (response.data.success) {
        const enrolledCourse = response.data.my_courses.find(
          enrollment => enrollment.course.id === courseId
        );
        console.log('🎯 Found enrolled course:', enrolledCourse);
        if (enrolledCourse) {
          setIsEnrolled(true);
          setEnrollment(enrolledCourse);
          fetchModules();
          fetchLearningPath();
          checkCertificate();
        }
      }
    } catch (error) {
      console.error('❌ Failed to check enrollment:', error);
    }
  };

  const fetchModules = async () => {
    try {
      console.log('🔍 Fetching modules for course:', courseId);
      const response = await api.get(`/courses/${courseId}/modules`);
      console.log('📚 Modules response:', response.data);
      if (response.data.success) {
        setModules(response.data.modules);
        console.log('✅ Set modules:', response.data.modules.length);
      }
    } catch (error) {
      console.error('❌ Failed to fetch modules:', error);
      if (error.response?.status === 403) {
        toast.error('Please enroll in the course to view modules');
      }
    }
  };

  const fetchLearningPath = async () => {
    try {
      console.log('🗺️ Fetching learning path for course:', courseId);
      // Temporarily disabled - endpoint not implemented
      // const response = await api.get(`/courses/${courseId}/learning-path`);
      // console.log('📋 Learning path response:', response.data);
      const response = { data: { success: false } }; // Placeholder
      if (response.data.success) {
        setLearningPath(response.data.learning_path);
        console.log('✅ Set learning path:', response.data.learning_path);
      }
    } catch (error) {
      console.error('❌ Failed to fetch learning path:', error);
    }
  };

  const handleEnroll = async () => {
    if (!user) {
      toast.error('Please login to enroll in courses');
      navigate('/login');
      return;
    }

    try {
      console.log('🎯 Enrolling in course:', courseId);
      const response = await api.post(`/courses/${courseId}/enroll`);
      console.log('✅ Enrollment response:', response.data);
      if (response.data.success) {
        toast.success('Successfully enrolled in course!');
        setIsEnrolled(true);
        setEnrollment(response.data.enrollment);
        // Re-check enrollment to get full data
        await checkEnrollment();
        // Fetch learning path for newly enrolled user
        await fetchLearningPath();
      }
    } catch (error) {
      console.error('❌ Enrollment error:', error);
      toast.error(error.response?.data?.message || 'Failed to enroll in course');
    }
  };

  const updateProgress = async (newProgress) => {
    try {
      const response = await api.put(`/courses/${courseId}/progress`, {
        progress_percentage: newProgress
      });
      if (response.data.success) {
        setEnrollment(prev => ({
          ...prev,
          progress_percentage: newProgress,
          status: response.data.enrollment.status
        }));
        toast.success('Progress updated!');
      }
    } catch (error) {
      toast.error('Failed to update progress');
    }
  };

  const toggleModuleContent = (moduleId) => {
    setExpandedModules(prev => {
      const newSet = new Set(prev);
      if (newSet.has(moduleId)) {
        newSet.delete(moduleId);
      } else {
        newSet.add(moduleId);
      }
      return newSet;
    });
  };

  const handleTestCompletion = (moduleId, testResult) => {
    // This would be called when returning from test
    setModuleTestResults(prev => ({
      ...prev,
      [moduleId]: testResult
    }));
    
    // If test passed, handle based on user's choice
    if (testResult.passed) {
      toast.success('Test passed! Module completed successfully.');
      
      // Auto-complete the module
      completeModule(moduleId, modules.find(m => m.id === moduleId)?.title || 'Module');
      
      // Handle user's choice from test completion
      if (testResult.action === 'continue_next_module') {
        const currentModuleIndex = modules.findIndex(m => m.id === moduleId);
        const nextModule = modules[currentModuleIndex + 1];
        
        if (nextModule) {
          setTimeout(() => {
            toast.success(`🎯 Next: ${nextModule.title} is now unlocked!`, {
              duration: 4000,
              icon: '🚀'
            });
            // Auto-expand next module
            setExpandedModules(prev => new Set([...prev, nextModule.id]));
          }, 1500);
        } else {
          // All modules completed
          setTimeout(() => {
            toast.success('🎉 All modules completed! Take the final test to earn your certificate!', {
              duration: 5000,
              icon: '🏆'
            });
          }, 1500);
        }
      } else if (testResult.action === 'take_final_test') {
        // User chose to take final test
        setTimeout(() => {
          toast.success('🎯 Ready for final test! Click "Take Final Assessment" to earn your certificate!', {
            duration: 5000,
            icon: '🏆'
          });
        }, 1500);
      }
    } else {
      toast.error(`Test failed with ${testResult.score}%. You need 60% to pass and continue.`);
    }
  };

  const handleFinalTestCompletion = (testResult) => {
    setFinalTestCompleted(true);
    setFinalTestScore(testResult.score_percentage);
    
    if (testResult.certificate) {
      setCertificate(testResult.certificate);
      toast.success('🎉 Congratulations! You earned a certificate!');
    } else if (testResult.score_percentage >= 60) {
      toast.success(`Final test passed with ${testResult.score_percentage}%!`);
    } else {
      toast.error(`Final test failed. Score: ${testResult.score_percentage}%. You need 60% to pass.`);
    }
  };

  const takeFinalAssessment = () => {
    // Check if all modules are completed
    if (enrollment && enrollment.progress_percentage < 100) {
      toast.error('Please complete all modules before taking the final assessment');
      return;
    }
    
    // Navigate to final test
    navigate(`/courses/${courseId}/final-test`);
  };

  const completeModule = async (moduleId, moduleTitle) => {
    try {
      const response = await api.post(`/courses/${courseId}/modules/${moduleId}/complete`);
      if (response.data.success) {
        setCompletedModules(prev => new Set([...prev, moduleId]));
        setEnrollment(prev => ({
          ...prev,
          progress_percentage: response.data.progress.percentage,
          status: response.data.progress.percentage === 100 ? 'completed' : 'active'
        }));
        
        console.log(`✅ Module "${moduleTitle}" completed! Progress: ${response.data.progress.percentage}%`);
        
        // Check if all modules are completed
        if (response.data.progress.percentage >= 100) {
          toast.success('🎉 All modules completed! You can now take the final assessment!');
        }
        
        // Check if certificate is available
        if (response.data.certificate) {
          setCertificate(response.data.certificate);
          toast.success('🎉 Congratulations! You earned a certificate!');
        }
      }
    } catch (error) {
      console.error('Failed to complete module:', error);
      toast.error('Failed to complete module');
    }
  };

  const getModuleContent = (module) => {
    // Enhanced module content based on module title/content
    const moduleTitle = module.title.toLowerCase();
    
    if (moduleTitle.includes('introduction') || moduleTitle.includes('basics')) {
      return {
        subtopics: [
          'What is Java Programming?',
          'Java Development Environment Setup',
          'Understanding JVM, JRE, and JDK',
          'Writing Your First Java Program',
          'Java Syntax and Structure'
        ],
        definitions: [
          {
            term: 'JVM (Java Virtual Machine)',
            definition: 'The runtime environment that executes Java bytecode and provides platform independence'
          },
          {
            term: 'Class',
            definition: 'A blueprint or template for creating objects that defines attributes and methods'
          },
          {
            term: 'Method',
            definition: 'A block of code that performs a specific task and can be called from other parts of the program'
          }
        ],
        codeExamples: [
          {
            title: 'Hello World Program',
            code: `public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        System.out.println("Welcome to Java Programming!");
    }
}`
          },
          {
            title: 'Basic Variable Declaration',
            code: `public class Variables {
    public static void main(String[] args) {
        int age = 25;
        String name = "John";
        double salary = 50000.50;
        boolean isEmployed = true;
        
        System.out.println("Name: " + name);
        System.out.println("Age: " + age);
    }
}`
          }
        ],
        explanation: 'Java is a powerful, object-oriented programming language that runs on billions of devices worldwide. In this module, you\'ll learn the fundamentals of Java programming, including how to set up your development environment, understand the Java ecosystem (JVM, JRE, JDK), and write your first Java programs. You\'ll also learn about Java\'s syntax, data types, and basic program structure.'
      };
    } else if (moduleTitle.includes('variable') || moduleTitle.includes('data type')) {
      return {
        subtopics: [
          'Primitive Data Types',
          'Reference Data Types',
          'Variable Declaration and Initialization',
          'Type Casting and Conversion',
          'Constants and Final Variables'
        ],
        definitions: [
          {
            term: 'Primitive Data Types',
            definition: 'Basic data types built into Java: byte, short, int, long, float, double, boolean, char'
          },
          {
            term: 'Reference Data Types',
            definition: 'Data types that store references to objects, including String, Arrays, and custom classes'
          },
          {
            term: 'Type Casting',
            definition: 'Converting one data type to another, either implicitly (widening) or explicitly (narrowing)'
          }
        ],
        codeExamples: [
          {
            title: 'Primitive Data Types',
            code: `public class DataTypes {
    public static void main(String[] args) {
        // Integer types
        byte b = 127;
        short s = 32767;
        int i = 2147483647;
        long l = 9223372036854775807L;
        
        // Floating point types
        float f = 3.14f;
        double d = 3.14159265359;
        
        // Other types
        boolean bool = true;
        char c = 'A';
        
        System.out.println("Integer: " + i);
        System.out.println("Double: " + d);
        System.out.println("Boolean: " + bool);
        System.out.println("Character: " + c);
    }
}`
          },
          {
            title: 'Type Casting Example',
            code: `public class TypeCasting {
    public static void main(String[] args) {
        // Implicit casting (widening)
        int num = 100;
        double d = num;  // int to double
        
        // Explicit casting (narrowing)
        double pi = 3.14159;
        int intPi = (int) pi;  // double to int
        
        System.out.println("Original double: " + pi);
        System.out.println("Casted to int: " + intPi);
    }
}`
          }
        ],
        explanation: 'Variables are containers that store data values. Java has two categories of data types: primitive and reference types. Primitive types store actual values, while reference types store addresses of objects. Understanding data types is crucial for memory management and choosing the right type for your data. This module covers all primitive data types, variable declaration, initialization, and type conversion techniques.'
      };
    } else {
      // Default content for other modules
      return {
        subtopics: [
          'Core Concepts Overview',
          'Key Programming Principles',
          'Practical Implementation',
          'Code Examples and Patterns',
          'Best Practices and Tips'
        ],
        definitions: [
          {
            term: 'Object',
            definition: 'An instance of a class that contains data (attributes) and code (methods)'
          },
          {
            term: 'Encapsulation',
            definition: 'The bundling of data and methods that operate on that data within a single unit'
          }
        ],
        codeExamples: [
          {
            title: 'Example Implementation',
            code: `public class Example {
    private String data;
    
    public Example(String data) {
        this.data = data;
    }
    
    public void displayData() {
        System.out.println("Data: " + data);
    }
    
    public static void main(String[] args) {
        Example ex = new Example("Hello Java");
        ex.displayData();
    }
}`
          }
        ],
        explanation: module.content || 'This module covers important Java programming concepts with practical examples and hands-on exercises. You\'ll learn through detailed explanations, code examples, and real-world applications.'
      };
    }
  };

  const fetchFinalProject = async () => {
    try {
      // Temporarily disabled - endpoint not fully implemented
      // const response = await api.get(`/final-projects/courses/${courseId}/final-project`);
      const response = { data: { success: false } }; // Placeholder
      if (response.data.success) {
        setFinalProject(response.data.final_project);
        setFinalProjectSubmission(response.data.final_project.submission);
        setCourseUnlocked(response.data.enrollment_status.course_unlocked);
      }
    } catch (error) {
      console.log('No final project found or error:', error);
    }
  };

  const submitFinalProject = async (completionPercentage, submissionData = {}) => {
    try {
      const response = await api.post(`/final-projects/courses/${courseId}/final-project/submit`, {
        completion_percentage: completionPercentage,
        submission_data: submissionData
      });
      
      if (response.data.success) {
        setFinalProjectSubmission(response.data.submission);
        setCourseUnlocked(response.data.submission.course_unlocked);
        
        if (completionPercentage >= 75) {
          toast.success('🎉 Final project 75% complete! Course features unlocked!');
        } else {
          toast.success('Final project progress saved!');
        }
        
        // Refresh enrollment data
        await checkEnrollment();
      }
    } catch (error) {
      toast.error('Failed to submit final project');
    }
  };

  const checkCertificate = async () => {
    try {
      const response = await api.get('/tests/certificates');
      if (response.data.success) {
        const courseCertificate = response.data.certificates.find(
          cert => cert.course_title === course?.title
        );
        if (courseCertificate) {
          setCertificate(courseCertificate);
          setFinalTestCompleted(true);
          setFinalTestScore(courseCertificate.final_score);
        }
      }
    } catch (error) {
      console.log('No certificates found or error:', error);
    }
  };

  const downloadCertificate = async () => {
    try {
      if (certificate && certificate.download_url) {
        // Create a temporary link to download the certificate
        const link = document.createElement('a');
        link.href = `/api${certificate.download_url}`;
        link.download = `certificate_${certificate.certificate_number}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        toast.success('Certificate download started!');
      } else {
        toast.error('Certificate not available');
      }
    } catch (error) {
      toast.error('Failed to download certificate');
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading course details..." />;
  }

  if (!course) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Course Not Found</h1>
          <button onClick={() => navigate('/courses')} className="btn-primary">
            Back to Courses
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Back Button */}
        <button
          onClick={() => navigate('/courses')}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Courses</span>
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Course Header */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <div className="flex items-start justify-between mb-6">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <span className="px-3 py-1 bg-primary-100 text-primary-700 text-sm font-medium rounded-full">
                      {course.skill_level}
                    </span>
                    <div className="flex items-center space-x-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span className="text-sm text-gray-600">4.8 (234 reviews)</span>
                    </div>
                  </div>
                  
                  <h1 className="text-3xl font-bold text-gray-900 mb-4">{course.title}</h1>
                  <p className="text-gray-600 text-lg leading-relaxed">{course.description}</p>
                </div>
              </div>

              {/* Course Stats */}
              <div className="grid grid-cols-3 gap-4 py-6 border-t border-gray-200">
                <div className="text-center">
                  <Clock className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Duration</p>
                  <p className="font-semibold text-gray-900">{course.duration_weeks} weeks</p>
                </div>
                
                <div className="text-center">
                  <BookOpen className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Modules</p>
                  <p className="font-semibold text-gray-900">{course.modules_count}</p>
                </div>
                
                <div className="text-center">
                  <Users className="w-6 h-6 text-green-600 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Students</p>
                  <p className="font-semibold text-gray-900">1,234</p>
                </div>
              </div>

              {/* Enrollment Status */}
              {isEnrolled && enrollment && (
                <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-green-800 font-medium">Enrolled</span>
                    <span className="text-green-600 text-sm">
                      {enrollment.progress_percentage}% Complete
                    </span>
                  </div>
                  <div className="w-full bg-green-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${enrollment.progress_percentage}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>

            {/* Course Modules */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Course Content</h2>
              
              {isEnrolled && modules.length > 0 ? (
                <div className="space-y-4">
                  {modules.map((module, index) => {
                    const isExpanded = expandedModules.has(module.id);
                    const isCompleted = completedModules.has(module.id);
                    const testResult = moduleTestResults[module.id];
                    const moduleContent = getModuleContent(module);
                    
                    // Check if this module is unlocked (first module or previous module completed)
                    const isUnlocked = index === 0 || completedModules.has(modules[index - 1]?.id);
                    const isLocked = !isUnlocked;
                    
                    return (
                      <div key={module.id} className={`border border-gray-200 rounded-lg overflow-hidden ${
                        isLocked ? 'opacity-60' : ''
                      }`}>
                        {/* Module Header */}
                        <div className={`p-4 ${isLocked ? 'bg-gray-100' : 'bg-gray-50'}`}>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                                isCompleted ? 'bg-green-100' : 
                                isLocked ? 'bg-gray-200' : 'bg-primary-100'
                              }`}>
                                {isCompleted ? (
                                  <CheckCircle className="w-5 h-5 text-green-600" />
                                ) : isLocked ? (
                                  <Lock className="w-4 h-4 text-gray-400" />
                                ) : (
                                  <span className="text-primary-600 font-semibold text-sm">
                                    {index + 1}
                                  </span>
                                )}
                              </div>
                              <div>
                                <h3 className={`font-medium ${isLocked ? 'text-gray-500' : 'text-gray-900'}`}>
                                  {module.title}
                                </h3>
                                <p className={`text-sm ${isLocked ? 'text-gray-400' : 'text-gray-600'}`}>
                                  Module {module.order_index} • 
                                  {isCompleted ? ' ✅ Completed' : 
                                   isLocked ? ' 🔒 Locked' :
                                   testResult?.passed ? ' ✅ Test Passed - Ready to Complete' : 
                                   isExpanded ? ' 📖 Learning' : ' ⭐ Available'}
                                </p>
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-2">
                              {!isCompleted && !isLocked && (
                                <>
                                  <button
                                    onClick={() => toggleModuleContent(module.id)}
                                    className={`flex items-center space-x-1 px-3 py-1 rounded text-sm transition-colors ${
                                      isExpanded 
                                        ? 'bg-primary-600 text-white hover:bg-primary-700' 
                                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                    }`}
                                  >
                                    <BookOpen className="w-4 h-4" />
                                    <span>{isExpanded ? 'Hide Content' : 'Learn'}</span>
                                  </button>
                                  
                                  {isExpanded && (
                                    <button
                                      onClick={() => navigate(`/courses/${courseId}/test/${module.id}`)}
                                      className="flex items-center space-x-1 px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                                    >
                                      <Target className="w-4 h-4" />
                                      <span>Take Test</span>
                                    </button>
                                  )}
                                </>
                              )}
                              
                              {isCompleted && (
                                <div className="flex items-center space-x-1 px-3 py-1 bg-green-100 text-green-800 rounded text-sm">
                                  <CheckCircle className="w-4 h-4" />
                                  <span>Completed</span>
                                </div>
                              )}
                              
                              {isLocked && (
                                <div className="flex items-center space-x-1 px-3 py-1 bg-gray-100 text-gray-500 rounded text-sm">
                                  <Lock className="w-4 h-4" />
                                  <span>Locked</span>
                                </div>
                              )}
                            </div>
                          </div>
                          
                          {/* Show unlock requirement for locked modules */}
                          {isLocked && index > 0 && (
                            <div className="mt-2 text-xs text-gray-500">
                              Complete "{modules[index - 1]?.title}" to unlock this module
                            </div>
                          )}
                        </div>
                        
                        {/* Expanded Module Content */}
                        {isExpanded && (
                          <div className="p-6 bg-white border-t border-gray-200">
                            <div className="space-y-6">
                              {/* Subtopics */}
                              <div>
                                <h4 className="font-semibold text-gray-900 mb-3">Topics Covered</h4>
                                <ul className="space-y-2">
                                  {moduleContent.subtopics.map((topic, idx) => (
                                    <li key={idx} className="flex items-center space-x-2">
                                      <div className="w-2 h-2 bg-primary-600 rounded-full"></div>
                                      <span className="text-gray-700">{topic}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                              
                              {/* Key Definitions */}
                              <div>
                                <h4 className="font-semibold text-gray-900 mb-3">Key Definitions</h4>
                                <div className="space-y-3">
                                  {moduleContent.definitions.map((def, idx) => (
                                    <div key={idx} className="bg-blue-50 p-3 rounded-lg">
                                      <dt className="font-medium text-blue-900">{def.term}</dt>
                                      <dd className="text-blue-800 text-sm mt-1">{def.definition}</dd>
                                    </div>
                                  ))}
                                </div>
                              </div>
                              
                              {/* Code Examples */}
                              <div>
                                <h4 className="font-semibold text-gray-900 mb-3">Code Examples</h4>
                                <div className="space-y-4">
                                  {moduleContent.codeExamples.map((example, idx) => (
                                    <div key={idx}>
                                      <h5 className="font-medium text-gray-800 mb-2">{example.title}</h5>
                                      <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm">
                                        <code>{example.code}</code>
                                      </pre>
                                    </div>
                                  ))}
                                </div>
                              </div>
                              
                              {/* Detailed Explanation */}
                              <div>
                                <h4 className="font-semibold text-gray-900 mb-3">Detailed Explanation</h4>
                                <div className="prose prose-sm max-w-none">
                                  <p className="text-gray-700 leading-relaxed">{moduleContent.explanation}</p>
                                </div>
                              </div>
                              
                              {/* Test Status */}
                              {testResult && (
                                <div className={`p-4 rounded-lg ${
                                  testResult.passed ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                                }`}>
                                  <div className="flex items-center space-x-2">
                                    {testResult.passed ? (
                                      <CheckCircle className="w-5 h-5 text-green-600" />
                                    ) : (
                                      <AlertCircle className="w-5 h-5 text-red-600" />
                                    )}
                                    <span className={`font-medium ${
                                      testResult.passed ? 'text-green-800' : 'text-red-800'
                                    }`}>
                                      Test {testResult.passed ? 'Passed' : 'Failed'}: {testResult.score}%
                                    </span>
                                  </div>
                                  {testResult.passed && (
                                    <p className="text-green-700 text-sm mt-1">
                                      Great job! You can now complete this module.
                                    </p>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : !isEnrolled ? (
                <div className="space-y-3">
                  {Array.from({ length: course.modules_count || 6 }, (_, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 opacity-60">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                            <Lock className="w-4 h-4 text-gray-400" />
                          </div>
                          <div>
                            <h3 className="font-medium text-gray-500">Module {index + 1}</h3>
                            <p className="text-sm text-gray-400">Locked - Enroll to access</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-600">Loading course modules...</p>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Enrollment Card */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              {!isEnrolled ? (
                <div className="text-center">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Ready to start learning?
                  </h3>
                  <button
                    onClick={handleEnroll}
                    className="w-full btn-primary text-lg py-3 mb-4"
                  >
                    Enroll Now - Free
                  </button>
                  <p className="text-sm text-gray-600">
                    Join thousands of students already enrolled
                  </p>
                </div>
              ) : (
                <div className="text-center">
                  <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    You're Enrolled!
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Continue your learning journey
                  </p>
                  
                  {enrollment && (
                    <div className="space-y-3">
                      {enrollment.progress_percentage < 100 ? (
                        <>
                          <button
                            onClick={() => updateProgress(Math.min(100, enrollment.progress_percentage + 10))}
                            className="w-full btn-primary"
                          >
                            Continue Learning
                          </button>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                              style={{ width: `${enrollment.progress_percentage}%` }}
                            ></div>
                          </div>
                          <p className="text-xs text-gray-500 text-center">
                            Progress: {enrollment.progress_percentage}% • Complete all modules to unlock final test
                          </p>
                        </>
                      ) : (
                        <>
                          <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-3">
                            <div className="flex items-center space-x-2 mb-2">
                              <CheckCircle className="w-5 h-5 text-green-600" />
                              <span className="text-green-800 font-medium">All Modules Completed!</span>
                            </div>
                            <p className="text-green-700 text-sm">
                              You've completed all course modules. Take the final assessment to earn your certificate.
                            </p>
                          </div>
                          
                          {!finalTestCompleted ? (
                            <button
                              onClick={takeFinalAssessment}
                              className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium flex items-center justify-center space-x-2"
                            >
                              <Target className="w-4 h-4" />
                              <span>Take Final Assessment</span>
                            </button>
                          ) : (
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                              <div className="flex items-center space-x-2 mb-2">
                                <CheckCircle className="w-5 h-5 text-blue-600" />
                                <span className="text-blue-800 font-medium">Final Assessment Completed</span>
                              </div>
                              <p className="text-blue-700 text-sm">
                                Score: {finalTestScore}% • {finalTestScore >= 60 ? 'Passed' : 'Failed'}
                              </p>
                            </div>
                          )}
                          
                          <p className="text-xs text-gray-500 text-center">
                            Need 60% or higher on final assessment to earn certificate
                          </p>
                        </>
                      )}
                    </div>
                  )}
                  
                  {enrollment && enrollment.status === 'completed' && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <Award className="w-8 h-8 text-green-600 mx-auto mb-2" />
                      <p className="text-green-800 font-medium">Course Completed!</p>
                      <p className="text-green-600 text-sm mb-3">
                        Completed on {new Date(enrollment.completed_at).toLocaleDateString()}
                      </p>
                      <button
                        onClick={downloadCertificate}
                        className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                      >
                        Download Certificate
                      </button>
                    </div>
                  )}
                  
                  {certificate && (
                    <div className="mt-4 bg-gradient-to-br from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg p-4">
                      <div className="text-center">
                        <Award className="w-12 h-12 text-yellow-600 mx-auto mb-3" />
                        <h4 className="font-semibold text-yellow-900 mb-2">🎉 Certificate Earned!</h4>
                        <p className="text-yellow-800 text-sm mb-3">
                          Certificate #{certificate.certificate_number?.slice(-8)}
                        </p>
                        <div className="space-y-2 mb-4">
                          <p className="text-xs text-yellow-700">
                            <strong>Final Score:</strong> {certificate.final_score}%
                          </p>
                          <p className="text-xs text-yellow-700">
                            <strong>Issued:</strong> {new Date(certificate.issued_date).toLocaleDateString()}
                          </p>
                          <p className="text-xs text-yellow-700">
                            <strong>Course:</strong> {certificate.course_title}
                          </p>
                        </div>
                        <button 
                          onClick={downloadCertificate}
                          className="w-full px-4 py-2 bg-gradient-to-r from-yellow-600 to-orange-600 text-white rounded-lg hover:from-yellow-700 hover:to-orange-700 text-sm font-medium flex items-center justify-center space-x-2"
                        >
                          <Award className="w-4 h-4" />
                          <span>Download Certificate</span>
                        </button>
                        <p className="text-xs text-yellow-600 mt-2">
                          AI-generated certificate with verification
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Final Project Status */}
            {isEnrolled && finalProject && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Final Project</h3>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">{finalProject.title}</h4>
                    <p className="text-sm text-gray-600 mb-3">{finalProject.description}</p>
                  </div>
                  
                  {finalProjectSubmission ? (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">Progress</span>
                        <span className="text-sm font-semibold text-gray-900">
                          {finalProjectSubmission.completion_percentage}%
                        </span>
                      </div>
                      
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-300 ${
                            finalProjectSubmission.completion_percentage >= 75 
                              ? 'bg-green-600' 
                              : 'bg-blue-600'
                          }`}
                          style={{ width: `${finalProjectSubmission.completion_percentage}%` }}
                        ></div>
                      </div>
                      
                      <div className={`p-3 rounded-lg ${
                        finalProjectSubmission.completion_percentage >= 75
                          ? 'bg-green-50 border border-green-200'
                          : 'bg-orange-50 border border-orange-200'
                      }`}>
                        <div className="flex items-center space-x-2">
                          {finalProjectSubmission.completion_percentage >= 75 ? (
                            <CheckCircle className="w-5 h-5 text-green-600" />
                          ) : (
                            <AlertCircle className="w-5 h-5 text-orange-600" />
                          )}
                          <span className={`text-sm font-medium ${
                            finalProjectSubmission.completion_percentage >= 75
                              ? 'text-green-800'
                              : 'text-orange-800'
                          }`}>
                            {finalProjectSubmission.completion_percentage >= 75
                              ? 'Course Unlocked!'
                              : `Need ${75 - finalProjectSubmission.completion_percentage}% more to unlock`
                            }
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex space-x-2">
                        <button
                          onClick={() => submitFinalProject(
                            Math.min(100, finalProjectSubmission.completion_percentage + 10)
                          )}
                          className="flex-1 px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                        >
                          Update Progress
                        </button>
                        
                        {finalProjectSubmission.completion_percentage < 100 && (
                          <button
                            onClick={() => submitFinalProject(100)}
                            className="flex-1 px-3 py-2 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                          >
                            Mark Complete
                          </button>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <p className="text-sm text-gray-600">
                        Start your final project to unlock advanced course features.
                      </p>
                      <button
                        onClick={() => submitFinalProject(10)}
                        className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        Start Final Project
                      </button>
                    </div>
                  )}
                  
                  <div className="text-xs text-gray-500 mt-3">
                    <strong>Requirement:</strong> Complete 75% of final project to unlock all course features
                  </div>
                </div>
              </div>
            )}

            {/* What You'll Learn */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">What You'll Learn</h3>
              <ul className="space-y-3">
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Master the fundamentals and advanced concepts</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Build real-world projects and applications</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Develop industry-ready skills</span>
                </li>
                <li className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Get personalized feedback and guidance</span>
                </li>
              </ul>
            </div>

            {/* AI-Generated Learning Path */}
            {isEnrolled && learningPath && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">🤖 AI Learning Path</h3>
                  <button
                    onClick={() => setShowLearningPath(!showLearningPath)}
                    className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                  >
                    {showLearningPath ? 'Hide' : 'Show'} Path
                  </button>
                </div>
                
                {showLearningPath && (
                  <div className="space-y-4">
                    <div className="text-sm text-gray-600 mb-4">
                      <p><strong>Duration:</strong> {learningPath.total_duration_weeks} weeks</p>
                      <p><strong>Your Progress:</strong> {learningPath.user_progress?.progress_percentage || 0}%</p>
                    </div>
                    
                    {learningPath.phases?.map((phase, index) => (
                      <div key={phase.phase_number} className="border-l-4 border-primary-200 pl-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <Target className="w-4 h-4 text-primary-600" />
                          <h4 className="font-medium text-gray-900">
                            Phase {phase.phase_number}: {phase.phase_name}
                          </h4>
                        </div>
                        
                        <p className="text-sm text-gray-600 mb-2">
                          {phase.estimated_weeks} weeks • {phase.modules?.length || 0} modules
                        </p>
                        
                        <div className="text-xs text-gray-500 mb-2">
                          <strong>Milestone:</strong> {phase.milestone_project}
                        </div>
                        
                        {phase.learning_objectives && (
                          <ul className="text-xs text-gray-600 space-y-1">
                            {phase.learning_objectives.slice(0, 2).map((objective, objIndex) => (
                              <li key={objIndex} className="flex items-start space-x-1">
                                <span className="text-primary-500">•</span>
                                <span>{objective}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                    
                    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <AlertCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        <div className="text-xs text-blue-800">
                          <p className="font-medium mb-1">AI-Personalized Path</p>
                          <p>This learning path is customized based on your skill level and course content to optimize your learning experience.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Prerequisites */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Prerequisites</h3>
              <ul className="space-y-2 text-gray-700">
                <li>• Basic computer skills</li>
                <li>• Willingness to learn</li>
                <li>• No prior experience required</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;