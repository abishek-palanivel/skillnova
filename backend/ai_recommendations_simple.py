#!/usr/bin/env python3
"""
AI Recommendations Engine with Google Gemini Integration (FREE)
Provides intelligent recommendation functionality using Gemini models
"""

import random
import os
from typing import Dict, List, Any
from openai_service import gemini_service

class SimpleAIEngine:
    """Simple AI recommendation engine with basic functionality"""
    
    def __init__(self):
        self.skill_categories = {
            'Programming': {
                'keywords': ['programming', 'coding', 'development', 'software', 'python', 'java', 'javascript'],
                'courses': ['Python Fundamentals', 'Java Programming', 'Web Development', 'Data Structures'],
                'mentors': ['Senior Developer', 'Software Engineer', 'Full Stack Developer'],
                'tests': ['Programming Basics', 'Algorithm Challenges', 'Code Review']
            },
            'Data Science': {
                'keywords': ['data', 'analytics', 'machine learning', 'statistics', 'ai'],
                'courses': ['Data Analysis', 'Machine Learning', 'Statistics', 'Python for Data Science'],
                'mentors': ['Data Scientist', 'ML Engineer', 'Analytics Expert'],
                'tests': ['Data Analysis Test', 'ML Fundamentals', 'Statistics Quiz']
            },
            'Web Development': {
                'keywords': ['web', 'frontend', 'backend', 'html', 'css', 'react', 'node'],
                'courses': ['HTML/CSS Basics', 'React Development', 'Node.js', 'Full Stack Web Dev'],
                'mentors': ['Frontend Developer', 'Backend Developer', 'Full Stack Engineer'],
                'tests': ['Web Fundamentals', 'Frontend Skills', 'Backend Development']
            },
            'Mobile Development': {
                'keywords': ['mobile', 'android', 'ios', 'app', 'flutter', 'react native'],
                'courses': ['Android Development', 'iOS Development', 'Flutter', 'React Native'],
                'mentors': ['Mobile Developer', 'Android Engineer', 'iOS Developer'],
                'tests': ['Mobile App Basics', 'Android Quiz', 'iOS Fundamentals']
            },
            'Creative Technology': {
                'keywords': ['arts', 'creative', 'design', 'graphics', 'digital art', 'multimedia', 'animation', 'video', 'photography'],
                'courses': ['Digital Design Fundamentals', 'Web Design', 'UI/UX Design', 'Creative Coding', 'Digital Marketing'],
                'mentors': ['UI/UX Designer', 'Creative Director', 'Digital Artist'],
                'tests': ['Design Principles', 'Creative Thinking', 'Digital Tools']
            },
            'Digital Arts & Media': {
                'keywords': ['art', 'media', 'visual', 'creative', 'content', 'storytelling', 'branding', 'marketing'],
                'courses': ['Digital Content Creation', 'Social Media Marketing', 'Brand Design', 'Creative Writing for Tech'],
                'mentors': ['Content Creator', 'Digital Marketer', 'Brand Strategist'],
                'tests': ['Creative Portfolio', 'Digital Marketing', 'Content Strategy']
            },
            'Tech for Creatives': {
                'keywords': ['creative', 'artist', 'designer', 'writer', 'musician', 'performer', 'visual', 'audio'],
                'courses': ['Technology for Artists', 'Creative Coding with p5.js', 'Digital Portfolio Building', 'Freelancing in Tech'],
                'mentors': ['Creative Technologist', 'Digital Artist', 'Tech Entrepreneur'],
                'tests': ['Creative Problem Solving', 'Digital Tools Mastery', 'Tech Fundamentals']
            },
            'Business & Entrepreneurship': {
                'keywords': ['business', 'entrepreneur', 'startup', 'management', 'leadership', 'finance', 'marketing'],
                'courses': ['Tech Entrepreneurship', 'Digital Business Strategy', 'Project Management', 'Tech Sales'],
                'mentors': ['Tech Entrepreneur', 'Business Analyst', 'Product Manager'],
                'tests': ['Business Fundamentals', 'Entrepreneurship Quiz', 'Leadership Skills']
            }
        }
    
    def analyze_user_profile(self, bio_data: Dict, assessment_scores: List = None) -> Dict:
        """Analyze user profile using Google Gemini and return structured data"""
        try:
            # Try Gemini AI analysis first
            if os.getenv('GEMINI_API_KEY'):
                ai_analysis = self._analyze_with_openai(bio_data, assessment_scores)
                if ai_analysis:
                    return ai_analysis
            
            # Fallback to rule-based analysis
            return self._analyze_with_rules(bio_data, assessment_scores)
        except Exception as e:
            print(f"Error analyzing user profile: {e}")
            return self._analyze_with_rules(bio_data, assessment_scores)
    
    def _analyze_with_openai(self, bio_data: Dict, assessment_scores: List = None) -> Dict:
        """Use Google Gemini to analyze user profile"""
        try:
            prompt = f"""Analyze this user profile and provide recommendations:

Bio Data:
- Skills: {bio_data.get('skills', 'Not provided')}
- Goals: {bio_data.get('goals', 'Not provided')}
- Interests: {bio_data.get('interests', 'Not provided')}
- Education: {bio_data.get('education', 'Not provided')}
- Experience Level: {bio_data.get('experience_level', 'Beginner')}

Assessment Scores: {assessment_scores if assessment_scores else 'No scores yet'}

Provide a JSON response with:
- interests: array of 3 main interest areas (e.g., ["Programming", "Web Development", "Data Science"])
- skill_level: one of "Beginner", "Intermediate", "Advanced"
- experience_level: same as skill_level
- profile_completeness: number 0-100
- learning_style: one of "Visual", "Hands-on", "Reading", "Interactive"
- goals: brief summary of user's learning goals
- recommended_focus: array of 2-3 specific areas to focus on"""

            system_message = "You are an expert educational advisor analyzing student profiles. Always respond with valid JSON."
            
            result = gemini_service.generate_json_completion(prompt, system_message, temperature=0.5)
            
            if result:
                # Ensure all required fields are present
                return {
                    'interests': result.get('interests', ['Programming'])[:3],
                    'skill_level': result.get('skill_level', 'Beginner'),
                    'experience_level': result.get('experience_level', 'Beginner'),
                    'profile_completeness': result.get('profile_completeness', 50),
                    'learning_style': result.get('learning_style', 'Visual'),
                    'goals': result.get('goals', 'Learn programming'),
                    'recommended_focus': result.get('recommended_focus', [])
                }
            
            return None
        except Exception as e:
            print(f"OpenAI analysis error: {e}")
            return None
    
    def _analyze_with_rules(self, bio_data: Dict, assessment_scores: List = None) -> Dict:
        """Fallback rule-based analysis"""
        try:
            interests = []
            skill_level = 'Beginner'
            
            if bio_data:
                # Extract interests from bio data
                if 'interests' in bio_data and bio_data['interests']:
                    interests = [interest.strip() for interest in bio_data['interests'].split(',')]
                
                # Determine skill level
                if 'experience_level' in bio_data:
                    skill_level = bio_data['experience_level'] or 'Beginner'
                
                # Enhanced analysis for all fields including arts/creative backgrounds
                all_text = ""
                if bio_data.get('skills'):
                    all_text += bio_data['skills'].lower() + " "
                if bio_data.get('goals'):
                    all_text += bio_data['goals'].lower() + " "
                if bio_data.get('interests'):
                    all_text += bio_data['interests'].lower() + " "
                if bio_data.get('education'):
                    all_text += bio_data['education'].lower() + " "
                
                # Analyze all text for category matching
                category_scores = {}
                for category, data in self.skill_categories.items():
                    score = 0
                    for keyword in data['keywords']:
                        if keyword in all_text:
                            score += 1
                    category_scores[category] = score
                
                # Get top categories based on keyword matches
                sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
                
                # Add categories with matches to interests
                for category, score in sorted_categories:
                    if score > 0 and category not in interests:
                        interests.append(category)
                
                # Special handling for arts/creative backgrounds
                creative_keywords = ['art', 'arts', 'creative', 'design', 'visual', 'music', 'dance', 'theater', 
                                   'painting', 'drawing', 'sculpture', 'photography', 'film', 'video', 'animation',
                                   'graphic', 'illustration', 'fashion', 'interior', 'architecture', 'media']
                
                if any(keyword in all_text for keyword in creative_keywords):
                    # Prioritize creative technology paths for arts backgrounds
                    if 'Creative Technology' not in interests:
                        interests.insert(0, 'Creative Technology')
                    if 'Digital Arts & Media' not in interests:
                        interests.insert(1, 'Digital Arts & Media')
                    if 'Tech for Creatives' not in interests:
                        interests.insert(2, 'Tech for Creatives')
            
            # Default interests if none found
            if not interests:
                interests = ['Programming', 'Web Development']
            
            # Adjust skill level based on assessment scores
            if assessment_scores:
                avg_score = sum(assessment_scores) / len(assessment_scores)
                if avg_score >= 80:
                    skill_level = 'Advanced'
                elif avg_score >= 60:
                    skill_level = 'Intermediate'
                else:
                    skill_level = 'Beginner'
            
            return {
                'interests': interests[:3],  # Limit to top 3
                'skill_level': skill_level,
                'experience_level': skill_level,
                'profile_completeness': 85 if bio_data else 20,
                'learning_style': 'Visual',  # Default
                'goals': bio_data.get('goals', 'Learn programming') if bio_data else 'Learn programming'
            }
        except Exception as e:
            print(f"Error analyzing user profile: {e}")
            return {
                'interests': ['Programming'],
                'skill_level': 'Beginner',
                'experience_level': 'Beginner',
                'profile_completeness': 20,
                'learning_style': 'Visual',
                'goals': 'Learn programming'
            }
    
    def analyze_bio_data_with_ai(self, bio_data: Dict) -> Dict:
        """Analyze bio data and return AI insights"""
        return self.analyze_user_profile(bio_data)
    
    def recommend_courses(self, user_profile: Dict, limit: int = 5) -> List[Dict]:
        """Enhanced course recommendations with Google Gemini"""
        try:
            # Try Gemini AI recommendations first
            if os.getenv('GEMINI_API_KEY'):
                ai_recommendations = self._recommend_courses_with_openai(user_profile, limit)
                if ai_recommendations:
                    return ai_recommendations
            
            # Fallback to rule-based recommendations
            return self._recommend_courses_with_rules(user_profile, limit)
        except Exception as e:
            print(f"Error recommending courses: {e}")
            return self._recommend_courses_with_rules(user_profile, limit)
    
    def _recommend_courses_with_openai(self, user_profile: Dict, limit: int) -> List[Dict]:
        """Use Google Gemini to recommend courses"""
        try:
            interests = user_profile.get('interests', ['Programming'])
            skill_level = user_profile.get('skill_level', 'Beginner')
            goals = user_profile.get('goals', '')
            
            prompt = f"""Recommend {limit} online courses for a student with:
- Interests: {', '.join(interests)}
- Skill Level: {skill_level}
- Goals: {goals}

Provide a JSON response with an array of courses, each containing:
- title: course name
- category: main category
- difficulty: Beginner/Intermediate/Advanced
- match_score: 75-98 (how well it matches the user)
- description: brief description (1-2 sentences)
- duration: e.g., "6 weeks"
- rating: 4.0-5.0
- reason: why this course is recommended (1 sentence)
- skills_gained: array of 3-4 skills
- career_paths: array of 2-3 career options

Format as: {{"courses": [...]}}"""

            system_message = "You are an expert course advisor. Recommend real, high-quality courses. Always respond with valid JSON."
            
            result = gemini_service.generate_json_completion(prompt, system_message, temperature=0.7)
            
            if result and 'courses' in result:
                return result['courses'][:limit]
            
            return None
        except Exception as e:
            print(f"OpenAI course recommendation error: {e}")
            return None
    
    def _recommend_courses_with_rules(self, user_profile: Dict, limit: int) -> List[Dict]:
        """Fallback rule-based course recommendations"""
        try:
            recommendations = []
            interests = user_profile.get('interests', ['Programming'])
            skill_level = user_profile.get('skill_level', 'Beginner')
            goals = user_profile.get('goals', '').lower()
            
            # Enhanced recommendations for each interest
            for interest in interests:
                if interest in self.skill_categories:
                    courses = self.skill_categories[interest]['courses']
                    for course in courses[:limit//len(interests) + 1]:
                        # Calculate enhanced match score
                        match_score = random.randint(75, 85)
                        
                        # Boost for creative backgrounds
                        if interest in ['Creative Technology', 'Digital Arts & Media', 'Tech for Creatives']:
                            match_score += 10
                        
                        # Boost based on goals
                        if any(word in goals for word in ['career', 'job', 'transition', 'professional']):
                            match_score += 5
                        
                        recommendations.append({
                            'title': course,
                            'category': interest,
                            'difficulty': skill_level,
                            'match_score': min(match_score, 98),
                            'description': self._get_course_description(course, interest),
                            'duration': f'{random.randint(4, 12)} weeks',
                            'rating': round(random.uniform(4.2, 4.9), 1),
                            'reason': self._get_recommendation_reason(interest, course, user_profile),
                            'skills_gained': self._get_skills_for_course(course, interest),
                            'career_paths': self._get_career_paths(interest)
                        })
            
            # Add special recommendations for creative backgrounds
            if any(interest in ['Creative Technology', 'Digital Arts & Media', 'Tech for Creatives'] for interest in interests):
                creative_courses = [
                    {
                        'title': 'Creative Coding for Artists',
                        'category': 'Creative Technology',
                        'difficulty': 'Beginner',
                        'match_score': 95,
                        'description': 'Learn programming through creative projects and visual art',
                        'duration': '8 weeks',
                        'rating': 4.8,
                        'reason': 'Perfect bridge between your artistic background and programming',
                        'skills_gained': ['JavaScript', 'p5.js', 'Creative Coding', 'Visual Programming'],
                        'career_paths': ['Creative Technologist', 'Interactive Designer', 'Digital Artist']
                    },
                    {
                        'title': 'Portfolio Website for Creatives',
                        'category': 'Tech for Creatives',
                        'difficulty': 'Beginner',
                        'match_score': 92,
                        'description': 'Build a professional online portfolio using modern web technologies',
                        'duration': '6 weeks',
                        'rating': 4.7,
                        'reason': 'Essential for showcasing your work and attracting clients',
                        'skills_gained': ['HTML/CSS', 'Responsive Design', 'Portfolio Building', 'Web Hosting'],
                        'career_paths': ['Freelance Creative', 'Web Designer', 'Digital Portfolio Specialist']
                    }
                ]
                recommendations.extend(creative_courses)
            
            # Sort by match score and return top recommendations
            recommendations.sort(key=lambda x: x['match_score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error recommending courses: {e}")
            return self._get_default_creative_recommendations(limit)
    
    def _get_recommendation_reason(self, interest: str, course: str, user_profile: Dict) -> str:
        """Generate personalized recommendation reason"""
        reasons = {
            'Creative Technology': [
                "Perfect for combining your creative background with technology",
                "Ideal transition from arts to tech industry",
                "Builds on your creative skills while learning programming"
            ],
            'Digital Arts & Media': [
                "Leverages your artistic talents in the digital world",
                "Great for monetizing your creative skills online",
                "Perfect blend of creativity and technology"
            ],
            'Tech for Creatives': [
                "Designed specifically for people with creative backgrounds",
                "Learn tech skills without losing your artistic identity",
                "Bridge your creative experience with modern technology"
            ]
        }
        
        if interest in reasons:
            return random.choice(reasons[interest])
        else:
            return f"Based on your interest in {interest} and career goals"
    
    def _get_skills_for_course(self, course: str, category: str) -> List[str]:
        """Get skills that will be gained from a course"""
        skill_mapping = {
            'creative coding': ['JavaScript', 'p5.js', 'Processing', 'Interactive Design'],
            'web design': ['HTML', 'CSS', 'Responsive Design', 'UI/UX'],
            'digital design': ['Photoshop', 'Illustrator', 'Figma', 'Design Thinking'],
            'python': ['Python Programming', 'Data Analysis', 'Automation'],
            'portfolio': ['Web Development', 'Design', 'Personal Branding', 'Online Presence']
        }
        
        course_lower = course.lower()
        for key, skills in skill_mapping.items():
            if key in course_lower:
                return skills
        
        return ['Problem Solving', 'Critical Thinking', 'Technical Skills', 'Digital Literacy']
    
    def _get_career_paths(self, category: str) -> List[str]:
        """Get potential career paths for a category"""
        career_mapping = {
            'Creative Technology': ['Creative Technologist', 'Interactive Designer', 'Digital Artist', 'UX Designer'],
            'Digital Arts & Media': ['Content Creator', 'Digital Marketer', 'Social Media Manager', 'Brand Designer'],
            'Tech for Creatives': ['Freelance Developer', 'Creative Consultant', 'Tech Entrepreneur', 'Product Designer'],
            'Programming': ['Software Developer', 'Web Developer', 'Data Analyst', 'DevOps Engineer'],
            'Web Development': ['Frontend Developer', 'Full Stack Developer', 'Web Designer', 'UI/UX Developer']
        }
        
        return career_mapping.get(category, ['Tech Professional', 'Software Developer', 'Digital Specialist'])
    
    def _get_course_description(self, course: str, category: str) -> str:
        """Generate enhanced course descriptions"""
        descriptions = {
            'Creative Technology': f'Learn {course} with a focus on creative applications and artistic expression',
            'Digital Arts & Media': f'Master {course} to enhance your digital presence and creative output',
            'Tech for Creatives': f'Practical {course} skills designed specifically for creative professionals',
        }
        
        if category in descriptions:
            return descriptions[category]
        else:
            return f'Learn {course} fundamentals and advanced concepts with hands-on projects'
    
    def _get_default_creative_recommendations(self, limit: int) -> List[Dict]:
        """Default recommendations for creative backgrounds"""
        return [
            {
                'title': 'Introduction to Creative Technology',
                'category': 'Creative Technology',
                'difficulty': 'Beginner',
                'match_score': 85,
                'description': 'Perfect starting point for artists entering the tech world',
                'duration': '6 weeks',
                'rating': 4.5,
                'reason': 'Designed for creative professionals transitioning to tech',
                'skills_gained': ['Digital Literacy', 'Creative Problem Solving', 'Tech Fundamentals'],
                'career_paths': ['Creative Technologist', 'Digital Creative', 'Tech-Savvy Artist']
            }
        ][:limit]
    
    def recommend_mentors(self, user_profile: Dict, limit: int = 5) -> List[Dict]:
        """Recommend mentors based on user profile"""
        try:
            recommendations = []
            interests = user_profile.get('interests', ['Programming'])
            
            for interest in interests:
                if interest in self.skill_categories:
                    mentors = self.skill_categories[interest]['mentors']
                    for mentor in mentors[:limit//len(interests) + 1]:
                        recommendations.append({
                            'name': f'{mentor} Expert',
                            'expertise': interest,
                            'experience': f'{random.randint(3, 10)} years',
                            'match_score': random.randint(80, 98),
                            'rating': round(random.uniform(4.5, 5.0), 1),
                            'availability': 'Available',
                            'description': f'Experienced {mentor} with expertise in {interest}'
                        })
            
            return recommendations[:limit]
        except Exception as e:
            print(f"Error recommending mentors: {e}")
            return []
    
    def recommend_practice_exercises(self, user_profile: Dict, limit: int = 5) -> List[Dict]:
        """Recommend practice exercises based on user profile"""
        try:
            recommendations = []
            interests = user_profile.get('interests', ['Programming'])
            skill_level = user_profile.get('skill_level', 'Beginner')
            
            exercise_types = ['Coding Challenge', 'Project', 'Quiz', 'Interactive Tutorial']
            
            for i in range(limit):
                interest = random.choice(interests)
                exercise_type = random.choice(exercise_types)
                
                recommendations.append({
                    'title': f'{interest} {exercise_type} #{i+1}',
                    'type': exercise_type,
                    'category': interest,
                    'difficulty': skill_level,
                    'estimated_time': f'{random.randint(15, 120)} minutes',
                    'match_score': random.randint(70, 95),
                    'description': f'Practice {interest} skills with this {exercise_type.lower()}'
                })
            
            return recommendations
        except Exception as e:
            print(f"Error recommending practice exercises: {e}")
            return []
    
    def recommend_tests(self, user_profile: Dict, limit: int = 5) -> List[Dict]:
        """Recommend tests based on user profile"""
        try:
            recommendations = []
            interests = user_profile.get('interests', ['Programming'])
            skill_level = user_profile.get('skill_level', 'Beginner')
            
            for interest in interests:
                if interest in self.skill_categories:
                    tests = self.skill_categories[interest]['tests']
                    for test in tests[:limit//len(interests) + 1]:
                        recommendations.append({
                            'title': test,
                            'category': interest,
                            'difficulty': skill_level,
                            'questions': random.randint(10, 25),
                            'duration': f'{random.randint(20, 60)} minutes',
                            'match_score': random.randint(75, 92),
                            'description': f'Test your {interest} knowledge and skills'
                        })
            
            return recommendations[:limit]
        except Exception as e:
            print(f"Error recommending tests: {e}")
            return []
    
    def generate_learning_path(self, user_profile: Dict) -> List[Dict]:
        """Generate a learning path based on user profile"""
        try:
            interests = user_profile.get('interests', ['Programming'])
            skill_level = user_profile.get('skill_level', 'Beginner')
            
            path = []
            for i, interest in enumerate(interests):
                path.append({
                    'step': i + 1,
                    'title': f'{interest} Fundamentals',
                    'category': interest,
                    'difficulty': 'Beginner',
                    'estimated_duration': '4-6 weeks',
                    'description': f'Master the basics of {interest}',
                    'status': 'available' if i == 0 else 'locked'
                })
                
                if skill_level in ['Intermediate', 'Advanced']:
                    path.append({
                        'step': i + 2,
                        'title': f'Advanced {interest}',
                        'category': interest,
                        'difficulty': 'Advanced',
                        'estimated_duration': '6-8 weeks',
                        'description': f'Advanced concepts and real-world applications',
                        'status': 'locked'
                    })
            
            return path[:6]  # Limit to 6 steps
        except Exception as e:
            print(f"Error generating learning path: {e}")
            return []
    
    def get_learning_recommendations(self, user_profile: Dict, course_progress: Dict = None, assessment_scores: List = None) -> Dict:
        """Get comprehensive learning recommendations"""
        try:
            return {
                'next_courses': self.recommend_courses(user_profile, 3),
                'suggested_mentors': self.recommend_mentors(user_profile, 2),
                'practice_exercises': self.recommend_practice_exercises(user_profile, 3),
                'skill_gaps': user_profile.get('interests', ['Programming'])[:2],
                'learning_path': self.generate_learning_path(user_profile)[:3]
            }
        except Exception as e:
            print(f"Error getting learning recommendations: {e}")
            return {}
    
    def generate_intelligent_assessment_questions(self, user_profile: Dict, count: int = 20) -> List[Dict]:
        """Generate intelligent assessment questions"""
        try:
            questions = []
            interests = user_profile.get('interests', ['Programming'])
            
            question_templates = {
                'Programming': [
                    'What is the output of this Python code?',
                    'Which data structure is best for this scenario?',
                    'What is the time complexity of this algorithm?',
                    'How would you optimize this code?'
                ],
                'Web Development': [
                    'Which HTML tag is used for this purpose?',
                    'What CSS property controls this behavior?',
                    'How do you implement responsive design?',
                    'What is the difference between these frameworks?'
                ],
                'Data Science': [
                    'Which algorithm is best for this problem?',
                    'How do you handle missing data?',
                    'What does this statistical measure indicate?',
                    'How do you evaluate model performance?'
                ]
            }
            
            for i in range(count):
                interest = random.choice(interests)
                if interest in question_templates:
                    template = random.choice(question_templates[interest])
                    
                    questions.append({
                        'id': i + 1,
                        'question': template,
                        'category': interest,
                        'difficulty': user_profile.get('skill_level', 'Beginner'),
                        'options': [f'Option {j+1}' for j in range(4)],
                        'correct_answer': 0,
                        'explanation': f'This tests your understanding of {interest} concepts.'
                    })
            
            return questions
        except Exception as e:
            print(f"Error generating assessment questions: {e}")
            return []
    
    def recommend_courses_ai(self, user_profile: Dict, score: float, limit: int = 5) -> List[Dict]:
        """AI-based course recommendations considering performance"""
        recommendations = self.recommend_courses(user_profile, limit)
        
        # Adjust recommendations based on score
        for rec in recommendations:
            if score >= 80:
                rec['difficulty'] = 'Advanced'
                rec['match_score'] = min(95, rec['match_score'] + 10)
            elif score >= 60:
                rec['difficulty'] = 'Intermediate'
                rec['match_score'] = min(90, rec['match_score'] + 5)
        
        return recommendations
    
    def recommend_external_courses(self, user_profile: Dict, assessment_results: Dict = None, limit: int = 5) -> List[Dict]:
        """Recommend external courses from platforms like Udemy, Coursera"""
        try:
            recommendations = []
            interests = user_profile.get('interests', ['Programming'])
            
            platforms = ['Udemy', 'Coursera', 'edX', 'Pluralsight']
            
            for i in range(limit):
                interest = random.choice(interests)
                platform = random.choice(platforms)
                
                recommendations.append({
                    'title': f'{interest} Masterclass',
                    'platform': platform,
                    'category': interest,
                    'rating': round(random.uniform(4.0, 4.8), 1),
                    'students': f'{random.randint(1000, 50000):,}',
                    'price': f'${random.randint(29, 199)}',
                    'duration': f'{random.randint(10, 40)} hours',
                    'match_score': random.randint(75, 95),
                    'url': f'https://{platform.lower()}.com/course/{interest.lower().replace(" ", "-")}'
                })
            
            return recommendations
        except Exception as e:
            print(f"Error recommending external courses: {e}")
            return []
    
    def get_external_course_recommendations(self, interests: List[str], skill_level: str, limit: int = 5) -> List[Dict]:
        """Get external course recommendations"""
        user_profile = {
            'interests': interests,
            'skill_level': skill_level
        }
        return self.recommend_external_courses(user_profile, limit=limit)
    
    def generate_certificate_data(self, user_data: Dict, course_data: Dict, completion_data: Dict) -> Dict:
        """Generate certificate data"""
        try:
            return {
                'certificate_id': f'CERT-{random.randint(100000, 999999)}',
                'user_name': user_data.get('name', 'Student'),
                'course_title': course_data.get('title', 'Course'),
                'completion_date': completion_data.get('completed_at', '2024-01-01'),
                'grade': completion_data.get('final_grade', 'A'),
                'skills_acquired': course_data.get('skills', ['Programming', 'Problem Solving']),
                'certificate_url': f'/certificates/{random.randint(100000, 999999)}',
                'verification_code': f'VER-{random.randint(10000, 99999)}'
            }
        except Exception as e:
            print(f"Error generating certificate data: {e}")
            return {}

# Create global instance
ai_engine = SimpleAIEngine()