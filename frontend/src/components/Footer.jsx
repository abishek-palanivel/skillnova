import React from 'react';
import { Link } from 'react-router-dom';
import { Star, Mail, Linkedin, Github } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-primary-600 to-accent-600 rounded-lg">
                <Star className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold">SkillNova</span>
            </div>
            <p className="text-gray-300 mb-4 max-w-md">
              💫 "Shine with Skills. Grow with Guidance."
            </p>
            <p className="text-gray-400 text-sm mb-4">
              An Intelligent Learning and Career Progression System that guides learners from skill assessment to personalized learning and mentorship.
            </p>
            <div className="flex space-x-4">
              <a
                href="https://www.linkedin.com/in/abishek-p-9ab80a326"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-primary-400 transition-colors"
              >
                <Linkedin className="w-5 h-5" />
              </a>
              <a
                href="mailto:abishekopennova@gmail.com"
                className="text-gray-400 hover:text-primary-400 transition-colors"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/courses" className="text-gray-400 hover:text-white transition-colors">
                  Courses
                </Link>
              </li>
              <li>
                <Link to="/mentors" className="text-gray-400 hover:text-white transition-colors">
                  Mentors
                </Link>
              </li>
              <li>
                <Link to="/practice" className="text-gray-400 hover:text-white transition-colors">
                  Practice
                </Link>
              </li>
              <li>
                <Link to="/tests" className="text-gray-400 hover:text-white transition-colors">
                  Assessments
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Support</h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="mailto:abishekopennova@gmail.com"
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  Contact Support
                </a>
              </li>
              <li>
                <Link to="/help" className="text-gray-400 hover:text-white transition-colors">
                  Help Center
                </Link>
              </li>
              <li>
                <Link to="/privacy" className="text-gray-400 hover:text-white transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/terms" className="text-gray-400 hover:text-white transition-colors">
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-gray-400 text-sm mb-4 md:mb-0">
              © 2024 SkillNova. All rights reserved.
            </div>
            <div className="text-gray-400 text-sm">
              Developed by{' '}
              <a
                href="https://www.linkedin.com/in/abishek-p-9ab80a326"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-400 hover:text-primary-300 transition-colors"
              >
                Abishek
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;