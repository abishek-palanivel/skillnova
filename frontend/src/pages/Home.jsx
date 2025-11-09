import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  Star, 
  BookOpen, 
  Users, 
  Award, 
  TrendingUp, 
  CheckCircle,
  ArrowRight,
  Sparkles,
  Zap,
  Target,
  Rocket,
  Brain,
  Globe,
  Shield,
  Code,
  Database,
  Cpu,
  Lightbulb,
  Trophy,
  Play,
  ChevronDown,
  Quote
} from 'lucide-react';

const Home = () => {
  const { user } = useAuth();
  const [currentTestimonial, setCurrentTestimonial] = useState(0);
  const [isVisible, setIsVisible] = useState({});

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          setIsVisible(prev => ({
            ...prev,
            [entry.target.id]: entry.isIntersecting
          }));
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll('[id]').forEach((el) => {
      observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Learning',
      description: 'Advanced algorithms analyze your learning patterns to create personalized study paths.',
      color: 'from-purple-500 to-pink-500',
      delay: '0ms'
    },
    {
      icon: Users,
      title: 'Expert Mentorship',
      description: 'Connect with industry leaders who provide real-world insights and career guidance.',
      color: 'from-blue-500 to-cyan-500',
      delay: '100ms'
    },
    {
      icon: Target,
      title: 'Skill Assessment',
      description: 'Comprehensive evaluations that identify strengths and areas for improvement.',
      color: 'from-green-500 to-emerald-500',
      delay: '200ms'
    },
    {
      icon: Rocket,
      title: 'Career Acceleration',
      description: 'Fast-track your career with personalized learning and industry connections.',
      color: 'from-orange-500 to-red-500',
      delay: '300ms'
    },
    {
      icon: Shield,
      title: 'Quality Learning',
      description: 'All courses and content are industry-recognized and professionally curated.',
      color: 'from-indigo-500 to-purple-500',
      delay: '400ms'
    },
    {
      icon: Globe,
      title: 'Global Network',
      description: 'Join a worldwide community of learners and professionals in tech.',
      color: 'from-teal-500 to-blue-500',
      delay: '500ms'
    }
  ];

  const technologies = [
    { icon: Code, name: 'Java Programming', color: 'text-blue-500' },
    { icon: Database, name: 'Data Structures', color: 'text-green-500' },
    { icon: Cpu, name: 'Algorithms', color: 'text-purple-500' },
    { icon: Globe, name: 'Object-Oriented', color: 'text-orange-500' },
    { icon: Shield, name: 'Best Practices', color: 'text-red-500' },
    { icon: Lightbulb, name: 'Problem Solving', color: 'text-yellow-500' }
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Java Developer at Google',
      image: '/api/placeholder/64/64',
      quote: 'SkillNova\'s Java course was comprehensive and practical. The hands-on projects and mentorship helped me master Java and land my dream job.',
      outcome: 'Career Success'
    },
    {
      name: 'Marcus Johnson',
      role: 'Senior Java Engineer at Amazon',
      image: '/api/placeholder/64/64',
      quote: 'From Java basics to advanced concepts, SkillNova covered everything. The structured learning path made complex topics easy to understand.',
      outcome: 'Skill Mastery'
    },
    {
      name: 'Priya Patel',
      role: 'Java Intern at Microsoft',
      image: '/api/placeholder/64/64',
      quote: 'The Java programming course at SkillNova gave me the confidence to apply for internships. Now I\'m working on enterprise Java applications!',
      outcome: 'Learning Success'
    }
  ];

  const learningPath = [
    {
      step: 1,
      title: 'Assessment & Profile',
      description: 'Complete comprehensive skill assessment and build your learning profile',
      icon: Target,
      color: 'bg-blue-500'
    },
    {
      step: 2,
      title: 'Personalized Learning',
      description: 'Follow AI-curated courses and practice with real-world projects',
      icon: Brain,
      color: 'bg-purple-500'
    },
    {
      step: 3,
      title: 'Expert Mentorship',
      description: 'Connect with industry mentors for guidance and career advice',
      icon: Users,
      color: 'bg-green-500'
    },
    {
      step: 4,
      title: 'Skill Validation',
      description: 'Take comprehensive tests to validate your learning progress',
      icon: Award,
      color: 'bg-orange-500'
    },
    {
      step: 5,
      title: 'Certification',
      description: 'Earn certificates to showcase your skills and knowledge',
      icon: Trophy,
      color: 'bg-red-500'
    }
  ];



  const stats = [
    { number: '10,000+', label: 'Students Enrolled', icon: Users, color: 'text-blue-500' },
    { number: '500+', label: 'Expert Mentors', icon: Award, color: 'text-green-500' },
    { number: '100+', label: 'Courses Available', icon: BookOpen, color: 'text-purple-500' },
    { number: '94%', label: 'Success Rate', icon: TrendingUp, color: 'text-orange-500' }
  ];

  return (
    <div className="min-h-screen overflow-hidden">
      {/* Hero Section with Animated Background */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 gradient-bg">
          <div className="absolute inset-0 opacity-20">
            {[...Array(50)].map((_, i) => (
              <div
                key={i}
                className="absolute animate-pulse"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 3}s`,
                  animationDuration: `${2 + Math.random() * 3}s`
                }}
              >
                <Star className="w-2 h-2 text-white" />
              </div>
            ))}
          </div>
        </div>

        {/* Hero Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white">
          <div className="animate-bounce-in">
            <div className="flex items-center justify-center mb-8">
              <div className="relative">
                <div className="flex items-center justify-center w-20 h-20 bg-white/20 rounded-full backdrop-blur-sm animate-pulse">
                  <Star className="w-10 h-10 text-white" />
                </div>
                <div className="absolute -inset-4 bg-white/10 rounded-full animate-ping"></div>
              </div>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 animate-slide-up">
              Welcome to{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 via-pink-300 to-purple-300 animate-pulse">
                SkillNova
              </span>
            </h1>
            
            <div className="flex items-center justify-center mb-6 animate-fade-in" style={{animationDelay: '0.5s'}}>
              <Sparkles className="w-6 h-6 text-yellow-300 mr-2 animate-spin" />
              <p className="text-2xl md:text-3xl font-semibold text-yellow-200">
                "Shine with Skills. Grow with Guidance."
              </p>
              <Sparkles className="w-6 h-6 text-yellow-300 ml-2 animate-spin" />
            </div>
            
            <p className="text-lg md:text-xl mb-8 text-blue-100 max-w-4xl mx-auto animate-fade-in" style={{animationDelay: '1s'}}>
              Master Java Programming with our comprehensive learning platform. From basics to advanced concepts,
              build real-world skills through hands-on practice, expert mentorship, and AI-powered guidance.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-6 justify-center animate-fade-in" style={{animationDelay: '1.5s'}}>
              {user ? (
                <Link
                  to="/dashboard"
                  className="group inline-flex items-center bg-white text-primary-600 px-8 py-4 rounded-xl font-semibold hover:bg-blue-50 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                  <Rocket className="mr-2 w-5 h-5 group-hover:animate-bounce" />
                  Go to Dashboard
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
              ) : (
                <>
                  <Link
                    to="/signup"
                    className="group inline-flex items-center bg-white text-primary-600 px-8 py-4 rounded-xl font-semibold hover:bg-blue-50 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                  >
                    <Zap className="mr-2 w-5 h-5 group-hover:animate-pulse" />
                    Start Your Journey
                    <Sparkles className="ml-2 w-5 h-5 group-hover:animate-spin" />
                  </Link>
                  <Link
                    to="/login"
                    className="group inline-flex items-center border-2 border-white text-white px-8 py-4 rounded-xl font-semibold hover:bg-white/10 transition-all duration-300 transform hover:scale-105 backdrop-blur-sm"
                  >
                    <Play className="mr-2 w-5 h-5" />
                    Login
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <ChevronDown className="w-8 h-8 text-white/70" />
        </div>
      </section>

      {/* Floating Stats Section */}
      <section className="py-20 bg-white relative" id="stats">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div 
                  key={index} 
                  className={`text-center transform transition-all duration-700 ${
                    isVisible.stats ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
                  }`}
                  style={{transitionDelay: `${index * 100}ms`}}
                >
                  <div className="relative group">
                    <div className="absolute inset-0 bg-gradient-to-r from-primary-400 to-accent-400 rounded-2xl blur opacity-25 group-hover:opacity-40 transition-opacity"></div>
                    <div className="relative bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2">
                      <Icon className={`w-8 h-8 ${stat.color} mx-auto mb-3`} />
                      <div className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                        {stat.number}
                      </div>
                      <div className="text-gray-600 font-medium">{stat.label}</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Enhanced Features Section */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-blue-50" id="features">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className={`text-4xl md:text-5xl font-bold text-gray-900 mb-6 transition-all duration-700 ${
              isVisible.features ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
            }`}>
              Why Choose <span className="text-gradient">SkillNova</span>?
            </h2>
            <p className={`text-xl text-gray-600 max-w-3xl mx-auto transition-all duration-700 ${
              isVisible.features ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
            }`} style={{transitionDelay: '200ms'}}>
              Experience the future of learning with our cutting-edge platform that combines 
              artificial intelligence with human expertise.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div 
                  key={index} 
                  className={`group transition-all duration-700 ${
                    isVisible.features ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
                  }`}
                  style={{transitionDelay: feature.delay}}
                >
                  <div className="relative h-full">
                    <div className={`absolute inset-0 bg-gradient-to-r ${feature.color} rounded-2xl blur opacity-20 group-hover:opacity-30 transition-opacity`}></div>
                    <div className="relative bg-white rounded-2xl p-8 h-full shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100">
                      <div className={`inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r ${feature.color} rounded-xl mb-6 shadow-lg`}>
                        <Icon className="w-8 h-8 text-white" />
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 mb-4 group-hover:text-primary-600 transition-colors">
                        {feature.title}
                      </h3>
                      <p className="text-gray-600 leading-relaxed">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Interactive Learning Path */}
      <section className="py-20 bg-white" id="learning-path">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className={`text-4xl md:text-5xl font-bold text-gray-900 mb-6 transition-all duration-700 ${
              isVisible['learning-path'] ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
            }`}>
              Your <span className="text-gradient">Learning Journey</span>
            </h2>
            <p className={`text-xl text-gray-600 max-w-3xl mx-auto transition-all duration-700 ${
              isVisible['learning-path'] ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
            }`} style={{transitionDelay: '200ms'}}>
              Follow our proven 5-step methodology from assessment to career success
            </p>
          </div>

          <div className="relative">
            {/* Connection Line */}
            <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 via-green-500 via-orange-500 to-red-500 rounded-full transform -translate-y-1/2"></div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-8">
              {learningPath.map((step, index) => {
                const Icon = step.icon;
                return (
                  <div 
                    key={index}
                    className={`text-center group transition-all duration-700 ${
                      isVisible['learning-path'] ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
                    }`}
                    style={{transitionDelay: `${index * 200}ms`}}
                  >
                    <div className="relative mb-6">
                      <div className={`w-20 h-20 ${step.color} rounded-full flex items-center justify-center mx-auto shadow-lg group-hover:shadow-xl transition-all duration-300 transform group-hover:scale-110 relative z-10`}>
                        <Icon className="w-10 h-10 text-white" />
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-r from-primary-400 to-accent-400 rounded-full blur opacity-30 group-hover:opacity-50 transition-opacity"></div>
                      <div className="absolute -top-2 -right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-md border-2 border-gray-100">
                        <span className="text-sm font-bold text-gray-700">{step.step}</span>
                      </div>
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-3 group-hover:text-primary-600 transition-colors">
                      {step.title}
                    </h3>
                    <p className="text-gray-600 text-sm leading-relaxed">
                      {step.description}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>



      {/* Testimonials Section */}
      <section className="py-20 bg-white" id="testimonials">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Success <span className="text-gradient">Stories</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Hear from our graduates who transformed their careers with SkillNova
            </p>
          </div>

          <div className="relative max-w-4xl mx-auto">
            <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-3xl p-8 md:p-12 shadow-xl">
              <Quote className="w-12 h-12 text-primary-400 mb-6" />
              
              <div className="transition-all duration-500 ease-in-out">
                <p className="text-xl md:text-2xl text-gray-700 mb-8 leading-relaxed">
                  "{testimonials[currentTestimonial].quote}"
                </p>
                
                <div className="flex items-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-primary-400 to-accent-400 rounded-full flex items-center justify-center mr-4">
                    <span className="text-white font-bold text-xl">
                      {testimonials[currentTestimonial].name.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-900 text-lg">
                      {testimonials[currentTestimonial].name}
                    </h4>
                    <p className="text-gray-600">
                      {testimonials[currentTestimonial].role}
                    </p>
                    <span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium mt-2">
                      {testimonials[currentTestimonial].outcome}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Testimonial Indicators */}
            <div className="flex justify-center mt-8 space-x-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentTestimonial(index)}
                  className={`w-3 h-3 rounded-full transition-all duration-300 ${
                    index === currentTestimonial 
                      ? 'bg-primary-600 w-8' 
                      : 'bg-gray-300 hover:bg-gray-400'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Master <span className="text-gradient">In-Demand</span> Technologies
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Learn the most sought-after skills in the tech industry
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8">
            {technologies.map((tech, index) => {
              const Icon = tech.icon;
              return (
                <div 
                  key={index}
                  className="group text-center transform transition-all duration-300 hover:scale-110"
                >
                  <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 group-hover:border-primary-200">
                    <Icon className={`w-12 h-12 ${tech.color} mx-auto mb-4 group-hover:animate-pulse`} />
                    <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                      {tech.name}
                    </h3>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Developer Contact Section */}
      <section className="py-20 bg-gradient-to-br from-gray-900 to-blue-900" id="contact">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className={`text-4xl md:text-5xl font-bold text-white mb-6 transition-all duration-700 ${
              isVisible.contact ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
            }`}>
              Meet the <span className="text-gradient-light">Developer</span>
            </h2>
            <p className={`text-xl text-blue-200 max-w-3xl mx-auto transition-all duration-700 ${
              isVisible.contact ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
            }`} style={{transitionDelay: '200ms'}}>
              Get in touch with the creator of SkillNova
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className={`bg-white/10 backdrop-blur-lg rounded-3xl p-8 md:p-12 border border-white/20 shadow-2xl transition-all duration-700 ${
              isVisible.contact ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'
            }`} style={{transitionDelay: '400ms'}}>
              
              {/* Developer Profile */}
              <div className="text-center mb-8">
                <div className="w-32 h-32 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl">
                  <span className="text-white font-bold text-4xl">A</span>
                </div>
                <h3 className="text-3xl font-bold text-white mb-2">Abishek</h3>
                <p className="text-blue-200 text-lg mb-6">Full Stack Developer & AI Enthusiast</p>
                <p className="text-gray-300 leading-relaxed max-w-2xl mx-auto">
                  Passionate about creating innovative learning solutions that bridge the gap between education and industry. 
                  SkillNova represents my vision of making quality tech education accessible to everyone.
                </p>
              </div>

              {/* Contact Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                
                {/* LinkedIn */}
                <a 
                  href="https://www.linkedin.com/in/abishek-p-9ab80a326?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3Bs3vPSDQzRUu1Vq3KZGI6Ew%3D%3D"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group bg-white/10 hover:bg-white/20 rounded-2xl p-6 transition-all duration-300 transform hover:scale-105 border border-white/20 hover:border-blue-400"
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-blue-600 rounded-xl flex items-center justify-center group-hover:bg-blue-500 transition-colors">
                      <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h4 className="text-white font-semibold text-lg mb-1 group-hover:text-blue-300 transition-colors">
                        LinkedIn Profile
                      </h4>
                      <p className="text-blue-200 text-sm">
                        Connect with me professionally
                      </p>
                      <p className="text-gray-400 text-xs mt-1 break-all">
                        linkedin.com/in/abishek-p-9ab80a326
                      </p>
                    </div>
                    <ArrowRight className="w-5 h-5 text-blue-300 group-hover:translate-x-1 transition-transform" />
                  </div>
                </a>

                {/* Email */}
                <a 
                  href="mailto:abishekopennova@gmail.com"
                  className="group bg-white/10 hover:bg-white/20 rounded-2xl p-6 transition-all duration-300 transform hover:scale-105 border border-white/20 hover:border-green-400"
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-green-600 rounded-xl flex items-center justify-center group-hover:bg-green-500 transition-colors">
                      <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h4 className="text-white font-semibold text-lg mb-1 group-hover:text-green-300 transition-colors">
                        Email Address
                      </h4>
                      <p className="text-blue-200 text-sm">
                        Send me a message
                      </p>
                      <p className="text-gray-400 text-xs mt-1">
                        abishekopennova@gmail.com
                      </p>
                    </div>
                    <ArrowRight className="w-5 h-5 text-green-300 group-hover:translate-x-1 transition-transform" />
                  </div>
                </a>

              </div>

              {/* Additional Info */}
              <div className="mt-8 pt-8 border-t border-white/20">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                  <div>
                    <div className="text-2xl font-bold text-blue-300 mb-2">5+</div>
                    <div className="text-gray-300 text-sm">Years Experience</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-300 mb-2">10+</div>
                    <div className="text-gray-300 text-sm">Projects Completed</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-purple-300 mb-2">24/7</div>
                    <div className="text-gray-300 text-sm">Support Available</div>
                  </div>
                </div>
              </div>

              {/* Call to Action */}
              <div className="mt-8 text-center">
                <p className="text-blue-200 mb-4">
                  Have questions about SkillNova or want to collaborate?
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <a
                    href="mailto:abishekopennova@gmail.com"
                    className="inline-flex items-center bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold hover:from-blue-600 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    Send Email
                  </a>
                  <a
                    href="https://www.linkedin.com/in/abishek-p-9ab80a326?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3Bs3vPSDQzRUu1Vq3KZGI6Ew%3D%3D"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center bg-white/20 text-white px-6 py-3 rounded-xl font-semibold hover:bg-white/30 transition-all duration-300 transform hover:scale-105 border border-white/30"
                  >
                    <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                    Connect on LinkedIn
                  </a>
                </div>
              </div>

            </div>
          </div>
        </div>
      </section>

      {/* Enhanced CTA Section */}
      {!user && (
        <section className="py-20 relative overflow-hidden">
          <div className="absolute inset-0 gradient-bg"></div>
          <div className="absolute inset-0 bg-black/20"></div>
          
          <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-4xl md:text-6xl font-bold mb-6">
                Ready to <span className="text-yellow-300">Transform</span> Your Career?
              </h2>
              <p className="text-xl md:text-2xl mb-8 text-blue-200">
                Join over 10,000 learners who have already started their journey to success
              </p>
              
              <div className="flex flex-col sm:flex-row gap-6 justify-center mb-12">
                <Link
                  to="/signup"
                  className="group inline-flex items-center bg-white text-primary-600 px-10 py-4 rounded-xl font-bold text-lg hover:bg-blue-50 transition-all duration-300 transform hover:scale-105 shadow-xl hover:shadow-2xl"
                >
                  <Rocket className="mr-3 w-6 h-6 group-hover:animate-bounce" />
                  Start Free Today
                  <Sparkles className="ml-3 w-6 h-6 group-hover:animate-spin" />
                </Link>
                
                <Link
                  to="/login"
                  className="group inline-flex items-center border-2 border-white text-white px-10 py-4 rounded-xl font-bold text-lg hover:bg-white/10 transition-all duration-300 transform hover:scale-105 backdrop-blur-sm"
                >
                  <Play className="mr-3 w-6 h-6" />
                  Watch Demo
                </Link>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
                <div>
                  <div className="text-3xl font-bold text-yellow-300 mb-2">Free</div>
                  <div className="text-blue-200">No Hidden Costs</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-yellow-300 mb-2">24/7</div>
                  <div className="text-blue-200">Learning Support</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-yellow-300 mb-2">100%</div>
                  <div className="text-blue-200">Course Completion</div>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};

export default Home;