"""
AI Course Generator - Creates comprehensive courses with modules, questions, and learning paths
"""

import random
from datetime import datetime
from typing import Dict, List, Any

class AICourseGenerator:
    def __init__(self):
        # AI-powered dynamic course generation - no fixed templates
        self.ai_course_patterns = {
            'programming_languages': {
                'java': ['fundamentals', 'oop', 'collections', 'multithreading', 'frameworks'],
                'python': ['basics', 'data_structures', 'libraries', 'web_frameworks', 'data_science'],
                'javascript': ['syntax', 'dom', 'async', 'frameworks', 'nodejs'],
                'csharp': ['basics', 'oop', 'linq', 'asp_net', 'entity_framework'],
                'cpp': ['syntax', 'pointers', 'oop', 'stl', 'advanced_topics']
            },
            'technologies': {
                'web_development': ['html_css', 'javascript', 'frontend_frameworks', 'backend', 'databases', 'deployment'],
                'mobile_development': ['platform_basics', 'ui_design', 'data_management', 'apis', 'testing', 'publishing'],
                'data_science': ['statistics', 'data_manipulation', 'visualization', 'machine_learning', 'deep_learning', 'deployment'],
                'cybersecurity': ['fundamentals', 'network_security', 'cryptography', 'ethical_hacking', 'incident_response'],
                'cloud_computing': ['cloud_basics', 'services', 'deployment', 'security', 'monitoring', 'optimization']
            },
            'difficulty_levels': {
                'beginner': ['easy', 'easy', 'easy', 'medium', 'medium', 'medium', 'medium', 'hard'],
                'intermediate': ['easy', 'medium', 'medium', 'medium', 'hard', 'hard', 'hard', 'hard'],
                'advanced': ['medium', 'medium', 'hard', 'hard', 'hard', 'hard', 'hard', 'hard']
            }
        }
            'web_development': {
                'modules': [
                    'HTML Fundamentals',
                    'CSS Styling and Layout',
                    'JavaScript Basics',
                    'DOM Manipulation',
                    'Responsive Web Design',
                    'Frontend Frameworks (React/Vue)',
                    'Backend Development (Node.js)',
                    'Database Integration',
                    'API Development',
                    'Authentication and Security',
                    'Deployment and Hosting',
                    'Full-Stack Project'
                ],
                'questions_per_module': 4,
                'difficulty_progression': ['easy', 'easy', 'medium', 'medium', 'medium', 'medium', 'hard', 'hard', 'hard', 'hard', 'hard', 'hard']
            },
            'python': {
                'modules': [
                    'Python Basics and Syntax',
                    'Variables and Data Types',
                    'Control Flow and Loops',
                    'Functions and Modules',
                    'Data Structures (Lists, Dicts)',
                    'Object-Oriented Programming',
                    'File Handling and I/O',
                    'Error Handling and Debugging',
                    'Libraries and Packages',
                    'Web Development with Flask/Django',
                    'Data Analysis with Pandas',
                    'Final Python Project'
                ],
                'questions_per_module': 4,
                'difficulty_progression': ['easy', 'easy', 'medium', 'medium', 'medium', 'medium', 'hard', 'hard', 'hard', 'hard', 'hard', 'hard']
            },
            'data_science': {
                'modules': [
                    'Introduction to Data Science',
                    'Python for Data Science',
                    'NumPy and Pandas',
                    'Data Visualization',
                    'Statistical Analysis',
                    'Machine Learning Basics',
                    'Supervised Learning',
                    'Unsupervised Learning',
                    'Data Preprocessing',
                    'Model Evaluation',
                    'Deep Learning Introduction',
                    'Capstone Data Science Project'
                ],
                'questions_per_module': 4,
                'difficulty_progression': ['easy', 'easy', 'medium', 'medium', 'medium', 'hard', 'hard', 'hard', 'hard', 'hard', 'hard', 'hard']
            },
            'mobile_development': {
                'modules': [
                    'Mobile Development Overview',
                    'React Native Fundamentals',
                    'Navigation and Routing',
                    'State Management',
                    'UI Components and Styling',
                    'API Integration',
                    'Local Storage and Databases',
                    'Push Notifications',
                    'Device Features (Camera, GPS)',
                    'Performance Optimization',
                    'App Store Deployment',
                    'Mobile App Project'
                ],
                'questions_per_module': 4,
                'difficulty_progression': ['easy', 'easy', 'medium', 'medium', 'medium', 'medium', 'hard', 'hard', 'hard', 'hard', 'hard', 'hard']
            }
        }
        
        self.sample_questions = {
            'java': [
                {
                    'question_text': 'What is the correct way to declare a variable in Java?',
                    'question_type': 'multiple_choice',
                    'difficulty_level': 'easy',
                    'correct_answer': 'int number = 5;',
                    'options': ['int number = 5;', 'number int = 5;', 'var number = 5;', 'declare int number = 5;']
                },
                {
                    'question_text': 'Which keyword is used to create a class in Java?',
                    'question_type': 'multiple_choice',
                    'difficulty_level': 'easy',
                    'correct_answer': 'class',
                    'options': ['class', 'Class', 'create', 'new']
                },
                {
                    'question_text': 'What is inheritance in Java?',
                    'question_type': 'multiple_choice',
                    'difficulty_level': 'medium',
                    'correct_answer': 'A mechanism where one class acquires properties of another class',
                    'options': [
                        'A mechanism where one class acquires properties of another class',
                        'A way to create multiple objects',
                        'A method to delete classes',
                        'A type of loop structure'
                    ]
                },
                {
                    'question_text': 'Explain the concept of polymorphism in Java with an example.',
                    'question_type': 'essay',
                    'difficulty_level': 'hard',
                    'correct_answer': 'Polymorphism allows objects of different classes to be treated as objects of a common base class. Example: Animal class with Dog and Cat subclasses, each implementing makeSound() method differently.'
                }
            ],
            'web_development': [
                {
                    'question_text': 'What does HTML stand for?',
                    'question_type': 'multiple_choice',
                    'difficulty_level': 'easy',
                    'correct_answer': 'HyperText Markup Language',
                    'options': ['HyperText Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyperlink and Text Markup Language']
                },
                {
                    'question_text': 'Which CSS property is used to change the text color?',
                    'question_type': 'multiple_choice',
                    'difficulty_level': 'easy',
                    'correct_answer': 'color',
                    'options': ['color', 'text-color', 'font-color', 'text-style']
                },
                {
                    'question_text': 'What is the difference between let, const, and var in JavaScript?',
                    'question_type': 'essay',
                    'difficulty_level': 'medium',
                    'correct_answer': 'var has function scope and can be redeclared, let has block scope and can be reassigned, const has block scope and cannot be reassigned.'
                }
            ],
            'python': [
                {
                    'question_text': 'How do you create a list in Python?',
                    'question_type': 'multiple_choice',
                    'difficulty_level': 'easy',
                    'correct_answer': 'my_list = []',
                    'options': ['my_list = []', 'my_list = ()', 'my_list = {}', 'my_list = <>']
                },
                {
                    'question_text': 'What is the output of print(type([]))?',
                    'question_type': 'multiple_choice',
                    'difficulty_level': 'medium',
                    'correct_answer': "<class 'list'>",
                    'options': ["<class 'list'>", "<class 'array'>", "<class 'tuple'>", "<class 'dict'>"]
                }
            ]
        }

    def detect_course_type(self, course_title: str) -> str:
        """Intelligently detect course type and generate custom content based on title"""
        title_lower = course_title.lower()
        
        # Enhanced detection with more specific patterns
        if any(keyword in title_lower for keyword in ['java', 'spring', 'hibernate', 'maven', 'gradle']):
            return 'java'
        elif any(keyword in title_lower for keyword in ['web', 'html', 'css', 'javascript', 'react', 'vue', 'angular', 'frontend', 'backend', 'fullstack', 'node', 'express']):
            return 'web_development'
        elif any(keyword in title_lower for keyword in ['python', 'django', 'flask', 'pandas', 'numpy']):
            return 'python'
        elif any(keyword in title_lower for keyword in ['data science', 'machine learning', 'ai', 'artificial intelligence', 'analytics', 'data analysis', 'ml', 'deep learning', 'neural network']):
            return 'data_science'
        elif any(keyword in title_lower for keyword in ['mobile', 'app development', 'react native', 'flutter', 'ios', 'android', 'swift', 'kotlin']):
            return 'mobile_development'
        elif any(keyword in title_lower for keyword in ['devops', 'docker', 'kubernetes', 'aws', 'cloud', 'deployment', 'ci/cd']):
            return 'devops'
        elif any(keyword in title_lower for keyword in ['cybersecurity', 'security', 'ethical hacking', 'penetration testing']):
            return 'cybersecurity'
        elif any(keyword in title_lower for keyword in ['database', 'sql', 'mysql', 'postgresql', 'mongodb', 'nosql']):
            return 'database'
        else:
            # Use AI to generate custom course type based on title
            return self._ai_analyze_course_title(course_title)

    def _ai_analyze_course_title(self, course_title: str) -> str:
        """AI-powered analysis of course title to determine content type"""
        title_words = course_title.lower().split()
        
        # AI logic to analyze title components
        tech_keywords = {
            'programming': ['programming', 'coding', 'development', 'software'],
            'web': ['web', 'website', 'frontend', 'backend', 'fullstack'],
            'mobile': ['mobile', 'app', 'android', 'ios'],
            'data': ['data', 'analytics', 'science', 'analysis'],
            'ai_ml': ['ai', 'ml', 'machine', 'learning', 'neural', 'deep'],
            'security': ['security', 'cyber', 'hacking', 'penetration'],
            'cloud': ['cloud', 'aws', 'azure', 'gcp', 'devops']
        }
        
        # Score each category
        scores = {}
        for category, keywords in tech_keywords.items():
            scores[category] = sum(1 for word in title_words if any(kw in word for kw in keywords))
        
        # Return highest scoring category or 'custom' for unique titles
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'custom'

    def _ai_generate_modules_for_title(self, course_title: str, modules_count: int, skill_level: str) -> List[str]:
        """AI generates contextually relevant modules based on course title"""
        title_lower = course_title.lower()
        
        # AI-powered module generation based on title analysis
        if 'java' in title_lower:
            if 'spring' in title_lower:
                return self._generate_spring_java_modules(modules_count, skill_level)
            elif 'android' in title_lower:
                return self._generate_android_java_modules(modules_count, skill_level)
            else:
                return self._generate_core_java_modules(modules_count, skill_level)
        
        elif 'python' in title_lower:
            if 'django' in title_lower or 'web' in title_lower:
                return self._generate_python_web_modules(modules_count, skill_level)
            elif 'data' in title_lower or 'science' in title_lower:
                return self._generate_python_data_modules(modules_count, skill_level)
            else:
                return self._generate_core_python_modules(modules_count, skill_level)
        
        elif any(word in title_lower for word in ['web', 'html', 'css', 'javascript', 'react', 'vue', 'angular']):
            return self._generate_web_development_modules(modules_count, skill_level, title_lower)
        
        elif any(word in title_lower for word in ['mobile', 'app', 'react native', 'flutter']):
            return self._generate_mobile_development_modules(modules_count, skill_level, title_lower)
        
        elif any(word in title_lower for word in ['data science', 'machine learning', 'ai', 'analytics']):
            return self._generate_data_science_modules(modules_count, skill_level)
        
        else:
            # AI generates custom modules for unique course titles
            return self._generate_custom_modules(course_title, modules_count, skill_level)

    def _generate_core_java_modules(self, count: int, skill_level: str) -> List[str]:
        """Generate Java-specific modules"""
        beginner_modules = [
            "Java Introduction and Environment Setup",
            "Java Syntax and Basic Programming Concepts",
            "Variables, Data Types, and Operators",
            "Control Flow: Conditionals and Loops",
            "Arrays and String Manipulation",
            "Methods and Function Programming",
            "Object-Oriented Programming Fundamentals",
            "Classes, Objects, and Constructors",
            "Inheritance and Polymorphism",
            "Exception Handling and Error Management",
            "File I/O and Data Persistence",
            "Java Collections Framework",
            "Final Project: Java Application Development"
        ]
        
        intermediate_modules = [
            "Advanced Java Concepts and Best Practices",
            "Generics and Type Safety",
            "Multithreading and Concurrency",
            "Java 8+ Features: Streams and Lambda Expressions",
            "Design Patterns in Java",
            "Database Connectivity with JDBC",
            "Unit Testing with JUnit",
            "Java Memory Management and Performance",
            "Networking and Socket Programming",
            "Java Reflection and Annotations",
            "Building RESTful APIs with Java",
            "Enterprise Java Application Development"
        ]
        
        advanced_modules = [
            "Java Virtual Machine Internals",
            "Advanced Concurrency and Parallel Programming",
            "Microservices Architecture with Java",
            "Spring Framework Deep Dive",
            "Performance Tuning and Optimization",
            "Security in Java Applications",
            "Reactive Programming with Java",
            "Cloud-Native Java Development",
            "Advanced Testing Strategies",
            "Java Application Monitoring and Debugging",
            "Enterprise Integration Patterns",
            "Capstone: Scalable Java System Design"
        ]
        
        if skill_level.lower() == 'beginner':
            return beginner_modules[:count]
        elif skill_level.lower() == 'intermediate':
            return intermediate_modules[:count]
        else:
            return advanced_modules[:count]

    def _generate_web_development_modules(self, count: int, skill_level: str, title_context: str) -> List[str]:
        """Generate web development modules based on specific technologies mentioned"""
        if 'react' in title_context:
            modules = [
                "React Fundamentals and JSX",
                "Components and Props",
                "State Management and Hooks",
                "Event Handling and Forms",
                "React Router for Navigation",
                "API Integration and HTTP Requests",
                "State Management with Redux/Context",
                "Testing React Applications",
                "Performance Optimization",
                "Deployment and Production Build",
                "Advanced React Patterns",
                "Full-Stack React Project"
            ]
        elif 'vue' in title_context:
            modules = [
                "Vue.js Fundamentals and Template Syntax",
                "Vue Components and Data Binding",
                "Directives and Event Handling",
                "Vue Router and Single Page Applications",
                "Vuex State Management",
                "API Integration with Axios",
                "Vue CLI and Build Tools",
                "Testing Vue Applications",
                "Performance and Optimization",
                "Deployment Strategies",
                "Advanced Vue Concepts",
                "Vue.js Full-Stack Project"
            ]
        else:
            # General web development
            modules = [
                "HTML5 Fundamentals and Semantic Markup",
                "CSS3 Styling and Layout Techniques",
                "Responsive Web Design and Mobile-First Approach",
                "JavaScript ES6+ Fundamentals",
                "DOM Manipulation and Event Handling",
                "Asynchronous JavaScript and APIs",
                "Frontend Framework Introduction",
                "Backend Development with Node.js",
                "Database Integration and CRUD Operations",
                "Authentication and Security",
                "Testing and Debugging Web Applications",
                "Deployment and DevOps for Web Apps"
            ]
        
        return modules[:count]

    def _generate_spring_java_modules(self, count: int, skill_level: str) -> List[str]:
        """Generate Spring Framework specific modules"""
        modules = [
            "Spring Framework Introduction and Setup",
            "Dependency Injection and IoC Container",
            "Spring Boot Fundamentals",
            "Spring MVC and Web Development",
            "Spring Data JPA and Database Integration",
            "Spring Security Implementation",
            "RESTful Web Services with Spring",
            "Spring Boot Testing Strategies",
            "Microservices with Spring Cloud",
            "Spring Boot Production Deployment",
            "Advanced Spring Concepts",
            "Spring Boot Enterprise Project"
        ]
        return modules[:count]

    def _generate_android_java_modules(self, count: int, skill_level: str) -> List[str]:
        """Generate Android Java specific modules"""
        modules = [
            "Android Development Environment Setup",
            "Java for Android Fundamentals",
            "Android Activities and Lifecycle",
            "User Interface Design with XML",
            "Event Handling and User Interaction",
            "Data Storage and SharedPreferences",
            "Working with Lists and RecyclerView",
            "Networking and API Integration",
            "Location Services and Maps",
            "Camera and Media Integration",
            "App Testing and Debugging",
            "Publishing Android Apps"
        ]
        return modules[:count]

    def _generate_python_web_modules(self, count: int, skill_level: str) -> List[str]:
        """Generate Python web development modules"""
        modules = [
            "Python Web Development Fundamentals",
            "Django Framework Introduction",
            "Models and Database Design",
            "Views and URL Routing",
            "Templates and Frontend Integration",
            "Forms and User Input Handling",
            "User Authentication and Authorization",
            "REST API Development",
            "Testing Django Applications",
            "Deployment and Production Setup",
            "Advanced Django Features",
            "Full-Stack Python Web Project"
        ]
        return modules[:count]

    def _generate_python_data_modules(self, count: int, skill_level: str) -> List[str]:
        """Generate Python data science modules"""
        modules = [
            "Python for Data Science Setup",
            "NumPy for Numerical Computing",
            "Pandas for Data Manipulation",
            "Data Visualization with Matplotlib",
            "Statistical Analysis with Python",
            "Machine Learning with Scikit-learn",
            "Data Cleaning and Preprocessing",
            "Exploratory Data Analysis",
            "Advanced Machine Learning Techniques",
            "Deep Learning with TensorFlow",
            "Data Science Project Deployment",
            "Capstone Data Science Project"
        ]
        return modules[:count]

    def _generate_core_python_modules(self, count: int, skill_level: str) -> List[str]:
        """Generate core Python programming modules"""
        modules = [
            "Python Installation and Environment Setup",
            "Python Syntax and Basic Data Types",
            "Control Structures and Flow Control",
            "Functions and Modular Programming",
            "Data Structures: Lists, Tuples, Dictionaries",
            "Object-Oriented Programming in Python",
            "File Handling and I/O Operations",
            "Error Handling and Exception Management",
            "Python Libraries and Package Management",
            "Testing and Debugging Python Code",
            "Python Best Practices and PEP 8",
            "Advanced Python Project Development"
        ]
        return modules[:count]

    def _generate_mobile_development_modules(self, count: int, skill_level: str, title_context: str) -> List[str]:
        """Generate mobile development modules"""
        if 'react native' in title_context:
            modules = [
                "React Native Development Setup",
                "JavaScript and React Fundamentals",
                "React Native Components and Navigation",
                "State Management in Mobile Apps",
                "Mobile UI/UX Design Principles",
                "Device APIs and Native Features",
                "Data Storage and Offline Functionality",
                "Push Notifications and Background Tasks",
                "Testing React Native Applications",
                "Performance Optimization",
                "App Store Deployment Process",
                "Cross-Platform Mobile Project"
            ]
        elif 'flutter' in title_context:
            modules = [
                "Flutter Development Environment",
                "Dart Programming Language",
                "Flutter Widgets and Layouts",
                "State Management with Provider/Bloc",
                "Navigation and Routing",
                "HTTP Requests and API Integration",
                "Local Storage and Databases",
                "Platform-Specific Features",
                "Testing Flutter Applications",
                "App Performance and Optimization",
                "Publishing to App Stores",
                "Advanced Flutter Development"
            ]
        else:
            modules = [
                "Mobile Development Fundamentals",
                "Platform-Specific Development Setup",
                "User Interface Design for Mobile",
                "Mobile App Architecture Patterns",
                "Data Management and Storage",
                "Network Communication and APIs",
                "Device Features Integration",
                "Mobile App Testing Strategies",
                "Performance and Memory Management",
                "Security in Mobile Applications",
                "App Store Guidelines and Deployment",
                "Mobile Development Best Practices"
            ]
        return modules[:count]

    def _generate_data_science_modules(self, count: int, skill_level: str) -> List[str]:
        """Generate data science specific modules"""
        modules = [
            "Introduction to Data Science and Analytics",
            "Python/R Programming for Data Science",
            "Statistics and Probability for Data Analysis",
            "Data Collection and Web Scraping",
            "Data Cleaning and Preprocessing",
            "Exploratory Data Analysis and Visualization",
            "Machine Learning Fundamentals",
            "Supervised Learning Algorithms",
            "Unsupervised Learning and Clustering",
            "Deep Learning and Neural Networks",
            "Model Evaluation and Deployment",
            "Data Science Capstone Project"
        ]
        return modules[:count]

    def _generate_custom_modules(self, course_title: str, count: int, skill_level: str) -> List[str]:
        """AI generates completely custom modules for unique course titles"""
        # Extract key concepts from title
        title_words = [word.strip('.,!?()[]{}') for word in course_title.split()]
        main_topic = title_words[0] if title_words else "Programming"
        
        # Generate progressive modules
        modules = []
        progression = ["Introduction", "Fundamentals", "Core Concepts", "Practical Applications", 
                      "Advanced Topics", "Integration", "Best Practices", "Real-World Projects",
                      "Performance & Optimization", "Testing & Debugging", "Deployment", "Mastery Project"]
        
        for i in range(count):
            if i < len(progression):
                module_name = f"{main_topic} {progression[i]}"
            else:
                module_name = f"Advanced {main_topic} Topic {i - len(progression) + 1}"
            modules.append(module_name)
        
        return modules

    def generate_complete_course(self, course_title: str, skill_level: str, duration_weeks: int = 8, modules_count: int = 8) -> Dict[str, Any]:
        """AI generates a complete course with modules, questions, and learning path relevant to the course title"""
        
        print(f"🤖 AI Analyzing course title: {course_title}")
        
        # AI-powered course analysis and generation
        course_type = self.detect_course_type(course_title)
        
        # AI generates contextually relevant modules
        module_titles = self._ai_generate_modules_for_title(course_title, modules_count, skill_level)
        
        # Generate detailed modules with AI-powered content
        modules = self._ai_generate_detailed_modules(course_title, module_titles, skill_level)
        
        # AI generates relevant questions based on course content
        questions = self._ai_generate_relevant_questions(course_title, modules, skill_level)
        
        # AI generates contextual assessments
        assessments = self._ai_generate_contextual_assessments(course_title, skill_level, len(modules))
        
        # Generate learning path
        learning_path = self._generate_learning_path(course_title, skill_level, modules)
        
        # Generate completion criteria
        completion_criteria = self._generate_completion_criteria(len(modules))
        
        course_content = {
            'course_info': {
                'title': course_title,
                'type': course_type,
                'skill_level': skill_level,
                'duration_weeks': duration_weeks,
                'description': f"Comprehensive {course_title} course with AI-generated content covering {len(modules)} modules"
            },
            'modules': modules,
            'questions': questions,
            'assessments': assessments,
            'learning_path': learning_path,
            'completion_criteria': completion_criteria
        }
        
        print(f"✅ Generated course with {len(modules)} modules and {len(questions)} questions")
        return course_content

    def _ai_generate_detailed_modules(self, course_title: str, module_titles: List[str], skill_level: str) -> List[Dict[str, Any]]:
        """AI generates detailed module content relevant to course title"""
        modules = []
        
        for i, title in enumerate(module_titles):
            # AI generates contextual content for each module
            content = self._ai_generate_module_content(course_title, title, skill_level, i + 1)
            
            module = {
                'title': title,
                'content': content,
                'order_index': i + 1,
                'estimated_duration': self._calculate_module_duration(title, skill_level),
                'learning_objectives': self._ai_generate_learning_objectives(course_title, title, skill_level)
            }
            modules.append(module)
        
        return modules

    def _ai_generate_module_content(self, course_title: str, module_title: str, skill_level: str, module_index: int) -> str:
        """AI generates contextually relevant module content"""
        
        # Extract key concepts from course and module titles
        course_context = course_title.lower()
        module_context = module_title.lower()
        
        # AI-powered content generation based on context
        intro_templates = {
            'beginner': f"Welcome to {module_title}! This module is designed to introduce you to the fundamental concepts of {module_title.lower()} in the context of {course_title}.",
            'intermediate': f"In this module on {module_title}, we'll explore intermediate concepts and practical applications within {course_title}.",
            'advanced': f"This advanced module on {module_title} covers sophisticated techniques and best practices for {course_title} development."
        }
        
        intro = intro_templates.get(skill_level.lower(), intro_templates['intermediate'])
        
        # Generate contextual learning objectives
        objectives = [
            f"Master the core concepts of {module_title.lower()}",
            f"Apply {module_title.lower()} techniques in real-world {course_title.lower()} scenarios",
            f"Understand best practices and common patterns in {module_title.lower()}",
            f"Complete hands-on exercises and practical implementations"
        ]
        
        # Generate contextual content sections
        content_sections = self._generate_contextual_content_sections(course_title, module_title, skill_level)
        
        content = f"""
{intro}

## Learning Objectives
By the end of this module, you will be able to:
{chr(10).join(f"• {obj}" for obj in objectives)}

## Module Overview
{content_sections['overview']}

## Key Topics Covered
{content_sections['topics']}

## Practical Exercises
{content_sections['exercises']}

## Assessment Preparation
{content_sections['assessment']}

## Next Steps
{content_sections['next_steps']}
        """.strip()
        
        return content

    def _generate_contextual_content_sections(self, course_title: str, module_title: str, skill_level: str) -> Dict[str, str]:
        """Generate contextual content sections based on course and module context"""
        
        sections = {
            'overview': f"This module provides comprehensive coverage of {module_title.lower()} as it applies to {course_title}. You'll learn through a combination of theoretical concepts and practical implementations.",
            
            'topics': f"""• Fundamental principles of {module_title.lower()}
• Practical implementation techniques
• Best practices and industry standards
• Common challenges and solutions
• Integration with other {course_title.lower()} components
• Performance considerations and optimization
• Real-world case studies and examples""",
            
            'exercises': f"""• Hands-on coding exercises related to {module_title.lower()}
• Step-by-step guided implementations
• Problem-solving challenges
• Code review and debugging practice
• Mini-projects to reinforce learning
• Peer collaboration opportunities""",
            
            'assessment': f"""• Review key concepts from {module_title.lower()}
• Practice with sample questions and scenarios
• Complete the module quiz (passing score: 60%)
• Apply concepts in practical coding challenges
• Prepare for integration with subsequent modules""",
            
            'next_steps': f"""Complete all exercises and assessments in this module before proceeding. The concepts learned in {module_title} will be essential for understanding the next module in your {course_title} learning journey."""
        }
        
        return sections

    def _ai_generate_learning_objectives(self, course_title: str, module_title: str, skill_level: str) -> List[str]:
        """AI generates contextual learning objectives"""
        base_objectives = [
            f"Understand the fundamental concepts of {module_title.lower()}",
            f"Apply {module_title.lower()} techniques in {course_title.lower()} development",
            f"Implement practical solutions using {module_title.lower()}",
            f"Analyze and debug {module_title.lower()}-related issues"
        ]
        
        if skill_level.lower() == 'advanced':
            base_objectives.extend([
                f"Design scalable architectures incorporating {module_title.lower()}",
                f"Optimize performance in {module_title.lower()} implementations"
            ])
        
        return base_objectives

    def _calculate_module_duration(self, module_title: str, skill_level: str) -> str:
        """Calculate estimated module duration based on complexity"""
        base_hours = 2
        
        if skill_level.lower() == 'beginner':
            base_hours = 3
        elif skill_level.lower() == 'advanced':
            base_hours = 4
        
        # Adjust based on module complexity
        complex_keywords = ['advanced', 'optimization', 'architecture', 'design patterns', 'security']
        if any(keyword in module_title.lower() for keyword in complex_keywords):
            base_hours += 1
        
        return f"{base_hours}-{base_hours + 1} hours"

    def _ai_generate_relevant_questions(self, course_title: str, modules: List[Dict], skill_level: str) -> List[Dict[str, Any]]:
        """AI generates questions specifically relevant to the course content"""
        questions = []
        
        # Determine difficulty progression based on skill level
        difficulty_progression = self.ai_course_patterns['difficulty_levels'].get(
            skill_level.lower(), 
            self.ai_course_patterns['difficulty_levels']['intermediate']
        )
        
        questions_per_module = 4 if skill_level.lower() == 'beginner' else 5
        
        for i, module in enumerate(modules):
            module_title = module['title']
            difficulty = difficulty_progression[i % len(difficulty_progression)]
            
            # Generate contextual questions for this module
            for q_index in range(questions_per_module):
                question = self._generate_contextual_question(
                    course_title, module_title, difficulty, q_index + 1
                )
                question['module_index'] = i + 1
                questions.append(question)
        
        return questions

    def _generate_contextual_question(self, course_title: str, module_title: str, difficulty: str, question_number: int) -> Dict[str, Any]:
        """Generate a contextually relevant question"""
        
        # AI-powered question generation based on context
        question_templates = {
            'easy': {
                'multiple_choice': f"What is the primary purpose of {module_title.lower()} in {course_title}?",
                'coding': f"Write a simple example demonstrating {module_title.lower()} in {course_title}.",
                'essay': f"Explain the basic concepts of {module_title.lower()} and its importance in {course_title}."
            },
            'medium': {
                'multiple_choice': f"Which best practice should be followed when implementing {module_title.lower()} in {course_title}?",
                'coding': f"Implement a solution that demonstrates {module_title.lower()} concepts in {course_title}.",
                'essay': f"Compare different approaches to {module_title.lower()} in {course_title} and discuss their trade-offs."
            },
            'hard': {
                'multiple_choice': f"What is the most efficient way to optimize {module_title.lower()} performance in {course_title}?",
                'coding': f"Design and implement an advanced {module_title.lower()} solution for a complex {course_title} scenario.",
                'essay': f"Analyze the architectural implications of {module_title.lower()} in large-scale {course_title} systems."
            }
        }
        
        # Select question type based on difficulty
        if difficulty == 'easy':
            question_type = 'multiple_choice'
        elif difficulty == 'medium':
            question_type = random.choice(['multiple_choice', 'essay'])
        else:
            question_type = random.choice(['multiple_choice', 'coding', 'essay'])
        
        question_text = question_templates[difficulty][question_type]
        
        # Generate contextual options for multiple choice
        options = []
        correct_answer = ""
        
        if question_type == 'multiple_choice':
            options, correct_answer = self._generate_contextual_options(course_title, module_title, difficulty)
        else:
            correct_answer = f"Sample answer demonstrating understanding of {module_title.lower()} in {course_title} context."
        
        return {
            'question_text': question_text,
            'question_type': question_type,
            'difficulty_level': difficulty,
            'category': course_title,
            'correct_answer': correct_answer,
            'options': options if question_type == 'multiple_choice' else []
        }

    def _generate_contextual_options(self, course_title: str, module_title: str, difficulty: str) -> tuple:
        """Generate contextual multiple choice options"""
        
        # AI generates relevant options based on context
        correct_option = f"Implement {module_title.lower()} following {course_title} best practices"
        
        wrong_options = [
            f"Ignore {module_title.lower()} principles in {course_title}",
            f"Use outdated {module_title.lower()} approaches",
            f"Skip {module_title.lower()} implementation entirely"
        ]
        
        options = [correct_option] + wrong_options
        random.shuffle(options)
        
        return options, correct_option

    def _ai_generate_contextual_assessments(self, course_title: str, skill_level: str, num_modules: int) -> List[Dict[str, Any]]:
        """AI generates assessments relevant to the specific course"""
        
        assessments = [
            {
                'type': 'module_quiz',
                'title': f'{course_title} Module Assessment',
                'description': f'Quick assessment covering key concepts from each {course_title} module',
                'questions_count': 5,
                'time_limit_minutes': 15,
                'passing_score': 60,
                'context': f'Tests understanding of {course_title} fundamentals'
            },
            {
                'type': 'practical_assessment',
                'title': f'{course_title} Practical Challenge',
                'description': f'Hands-on coding/implementation challenge for {course_title}',
                'questions_count': 3,
                'time_limit_minutes': 60,
                'passing_score': 70,
                'context': f'Practical application of {course_title} skills'
            },
            {
                'type': 'comprehensive_assessment',
                'title': f'{course_title} Final Certification Exam',
                'description': f'Comprehensive assessment covering all aspects of {course_title}',
                'questions_count': 20,
                'time_limit_minutes': 120,
                'passing_score': 75,
                'certificate_eligible': True,
                'context': f'Complete mastery of {course_title} concepts and applications'
            }
        ]
        
        # Adjust based on skill level
        if skill_level.lower() == 'beginner':
            for assessment in assessments:
                assessment['passing_score'] -= 5
                assessment['time_limit_minutes'] += 15
        elif skill_level.lower() == 'advanced':
            for assessment in assessments:
                assessment['passing_score'] += 5
                assessment['questions_count'] += 2
        
        return assessments

    def _generate_modules(self, course_title: str, course_type: str, template: Dict, modules_count: int) -> List[Dict[str, Any]]:
        """Generate course modules based on template"""
        modules = []
        module_titles = template['modules'][:modules_count]
        
        for i, title in enumerate(module_titles):
            content = self._generate_module_content(title, course_type, i + 1)
            
            module = {
                'title': title,
                'content': content,
                'order_index': i + 1,
                'estimated_duration': '1-2 hours',
                'learning_objectives': self._generate_learning_objectives(title, course_type)
            }
            modules.append(module)
        
        return modules

    def _generate_module_content(self, module_title: str, course_type: str, module_index: int) -> str:
        """Generate detailed content for a module"""
        
        content_templates = {
            'java': {
                'intro': f"Welcome to {module_title}. In this module, you will learn essential Java programming concepts.",
                'objectives': "By the end of this module, you will be able to:",
                'content': f"This module covers {module_title.lower()} in Java programming. You'll learn through practical examples and hands-on exercises.",
                'summary': "Practice the concepts learned in this module before proceeding to the next one."
            },
            'web_development': {
                'intro': f"In this module on {module_title}, we'll explore modern web development techniques.",
                'objectives': "Learning objectives for this module:",
                'content': f"This section focuses on {module_title.lower()} with real-world examples and best practices.",
                'summary': "Apply these web development concepts in your projects."
            },
            'python': {
                'intro': f"Let's dive into {module_title} in Python programming.",
                'objectives': "What you'll master in this module:",
                'content': f"Explore {module_title.lower()} with Python examples and interactive coding exercises.",
                'summary': "Practice Python coding with the concepts from this module."
            }
        }
        
        template = content_templates.get(course_type, content_templates['java'])
        
        content = f"""
{template['intro']}

{template['objectives']}
• Understand the core concepts of {module_title.lower()}
• Apply practical techniques and best practices
• Complete hands-on exercises and examples
• Prepare for the module assessment

{template['content']}

Key Topics Covered:
• Fundamental concepts and terminology
• Step-by-step implementation guide
• Common patterns and best practices
• Troubleshooting and debugging tips
• Real-world applications and examples

{template['summary']}

Next Steps: Complete the module quiz to test your understanding before moving to the next module.
        """.strip()
        
        return content

    def _generate_learning_objectives(self, module_title: str, course_type: str) -> List[str]:
        """Generate learning objectives for a module"""
        objectives = [
            f"Understand the fundamentals of {module_title.lower()}",
            f"Apply {module_title.lower()} concepts in practical scenarios",
            f"Demonstrate proficiency in {module_title.lower()} techniques"
        ]
        return objectives

    def _generate_questions(self, course_type: str, template: Dict, num_modules: int) -> List[Dict[str, Any]]:
        """Generate questions for the course"""
        questions = []
        sample_questions = self.sample_questions.get(course_type, self.sample_questions['java'])
        questions_per_module = template.get('questions_per_module', 4)
        
        # Generate questions for each module
        for module_index in range(num_modules):
            difficulty = template['difficulty_progression'][module_index] if module_index < len(template['difficulty_progression']) else 'medium'
            
            for q_index in range(questions_per_module):
                # Use sample questions as templates and modify them
                base_question = random.choice(sample_questions)
                
                question = {
                    'question_text': base_question['question_text'],
                    'question_type': base_question['question_type'],
                    'difficulty_level': difficulty,
                    'category': course_type,
                    'correct_answer': base_question['correct_answer'],
                    'options': base_question.get('options', []),
                    'module_index': module_index + 1
                }
                questions.append(question)
        
        return questions

    def _generate_assessments(self, course_type: str, skill_level: str) -> List[Dict[str, Any]]:
        """Generate assessment structure"""
        assessments = [
            {
                'type': 'module_quiz',
                'description': 'Quick quiz after each module (5 questions)',
                'questions_count': 5,
                'time_limit_minutes': 15,
                'passing_score': 60
            },
            {
                'type': 'midterm_assessment',
                'description': 'Comprehensive assessment covering first half of course',
                'questions_count': 10,
                'time_limit_minutes': 45,
                'passing_score': 60
            },
            {
                'type': 'final_assessment',
                'description': 'Final comprehensive assessment covering entire course',
                'questions_count': 15,
                'time_limit_minutes': 90,
                'passing_score': 60,
                'certificate_eligible': True,
                'perfect_score_certificate': True
            }
        ]
        return assessments

    def _generate_learning_path(self, course_title: str, skill_level: str, modules: List[Dict]) -> Dict[str, Any]:
        """Generate AI learning path"""
        
        learning_path = {
            'course_title': course_title,
            'skill_level': skill_level,
            'total_modules': len(modules),
            'estimated_completion_time': f"{len(modules) * 2} hours",
            'learning_sequence': [],
            'milestones': [],
            'recommendations': []
        }
        
        # Create learning sequence
        for i, module in enumerate(modules):
            sequence_item = {
                'step': i + 1,
                'module_title': module['title'],
                'description': f"Complete {module['title']} module",
                'estimated_time': '1-2 hours',
                'prerequisites': [modules[i-1]['title']] if i > 0 else [],
                'learning_activities': [
                    'Read module content',
                    'Complete practice exercises',
                    'Take module quiz (60% to pass)',
                    'Review and reinforce concepts'
                ]
            }
            learning_path['learning_sequence'].append(sequence_item)
        
        # Create milestones
        quarter_point = len(modules) // 4
        half_point = len(modules) // 2
        three_quarter_point = (len(modules) * 3) // 4
        
        milestones = [
            {
                'milestone': 'Course Start',
                'module': 1,
                'description': 'Begin your learning journey',
                'achievement': 'Course enrollment completed'
            }
        ]
        
        if quarter_point > 0:
            milestones.append({
                'milestone': 'Quarter Progress',
                'module': quarter_point,
                'description': '25% course completion',
                'achievement': 'Foundation concepts mastered'
            })
        
        if half_point > 0:
            milestones.append({
                'milestone': 'Midpoint Achievement',
                'module': half_point,
                'description': '50% course completion',
                'achievement': 'Intermediate skills developed'
            })
        
        if three_quarter_point > 0:
            milestones.append({
                'milestone': 'Advanced Progress',
                'module': three_quarter_point,
                'description': '75% course completion',
                'achievement': 'Advanced concepts understood'
            })
        
        milestones.append({
            'milestone': 'Course Completion',
            'module': len(modules),
            'description': '100% course completion',
            'achievement': 'Final assessment and certificate eligibility'
        })
        
        learning_path['milestones'] = milestones
        
        # Add recommendations based on skill level
        if skill_level.lower() == 'beginner':
            learning_path['recommendations'] = [
                'Take your time with each module - understanding is more important than speed',
                'Practice coding examples multiple times to reinforce learning',
                'Don\'t hesitate to revisit previous modules if needed',
                'Join study groups or forums for additional support'
            ]
        elif skill_level.lower() == 'intermediate':
            learning_path['recommendations'] = [
                'Focus on practical applications and real-world examples',
                'Try to implement concepts in your own projects',
                'Explore additional resources and advanced topics',
                'Consider mentoring beginners to reinforce your knowledge'
            ]
        else:  # Advanced
            learning_path['recommendations'] = [
                'Challenge yourself with complex implementations',
                'Contribute to open-source projects related to the course',
                'Explore cutting-edge developments in the field',
                'Consider teaching or creating content to share knowledge'
            ]
        
        return learning_path

    def _generate_completion_criteria(self, num_modules: int) -> Dict[str, Any]:
        """Generate course completion criteria"""
        return {
            'module_completion': {
                'required': True,
                'description': 'Complete all course modules',
                'progress_tracking': 'Module by module completion'
            },
            'quiz_performance': {
                'required': True,
                'minimum_score': 60,
                'description': 'Achieve 60% or higher on module quizzes',
                'retake_policy': 'Unlimited attempts allowed'
            },
            'final_assessment': {
                'required': True,
                'minimum_score': 60,
                'description': 'Pass final assessment with 60% or higher',
                'certificate_requirement': 'Required for course completion certificate'
            },
            'perfect_score_certificate': {
                'required': False,
                'minimum_score': 100,
                'description': 'Achieve 100% on final assessment for special AI-generated certificate',
                'benefits': 'Premium certificate with enhanced design and verification'
            },
            'time_requirements': {
                'minimum_time': f"{num_modules} hours",
                'recommended_pace': '1-2 modules per week',
                'maximum_duration': '6 months from enrollment'
            }
        }

# Create global instance
ai_course_generator = AICourseGenerator()