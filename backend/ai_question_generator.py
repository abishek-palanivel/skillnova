#!/usr/bin/env python3
"""
AI Question Generator Service with Google Gemini Integration (FREE)
This service generates questions using Gemini models based on type, difficulty, and category
"""

import json
import random
import os
from typing import Dict, List, Any
from openai_service import gemini_service

class AIQuestionGenerator:
    """AI-powered question generator using Google Gemini"""
    
    def __init__(self):
        # Question templates and patterns for different categories
        self.question_templates = {
            'Python': {
                'easy': [
                    "What is the correct way to {action} in Python?",
                    "Which Python {concept} is used for {purpose}?",
                    "What does the Python {function} function do?",
                    "How do you {task} in Python?"
                ],
                'medium': [
                    "What is the difference between {concept1} and {concept2} in Python?",
                    "How would you implement {algorithm} in Python?",
                    "What are the advantages of using {feature} in Python?",
                    "Explain how {concept} works in Python with an example."
                ],
                'hard': [
                    "Design a Python {structure} that can {functionality}.",
                    "Optimize this Python code for {performance_aspect}.",
                    "Implement a {design_pattern} in Python for {use_case}.",
                    "What are the memory implications of {operation} in Python?"
                ]
            },
            'JavaScript': {
                'easy': [
                    "What is the difference between {keyword1} and {keyword2} in JavaScript?",
                    "How do you {action} in JavaScript?",
                    "What does the {method} method do in JavaScript?",
                    "Which JavaScript {feature} is used for {purpose}?"
                ],
                'medium': [
                    "Explain {concept} in JavaScript with an example.",
                    "How does {mechanism} work in JavaScript?",
                    "What are the benefits of using {feature} in JavaScript?",
                    "Compare {approach1} vs {approach2} in JavaScript."
                ],
                'hard': [
                    "Implement {pattern} in JavaScript for {scenario}.",
                    "How would you optimize JavaScript code for {performance}?",
                    "Design a JavaScript {architecture} that handles {requirement}.",
                    "Explain the internals of {advanced_concept} in JavaScript."
                ]
            },
            'Web Development': {
                'easy': [
                    "What is the purpose of the {html_tag} tag in HTML?",
                    "Which CSS property is used to {styling_purpose}?",
                    "How do you {basic_task} in web development?",
                    "What does {web_concept} mean in web development?"
                ],
                'medium': [
                    "How do you implement {feature} in a web application?",
                    "What are the best practices for {web_aspect}?",
                    "Explain the difference between {concept1} and {concept2} in web development.",
                    "How does {web_technology} improve {aspect}?"
                ],
                'hard': [
                    "Design a scalable web architecture for {use_case}.",
                    "How would you optimize web performance for {scenario}?",
                    "Implement {advanced_feature} with {technology_stack}.",
                    "What are the security considerations for {web_feature}?"
                ]
            },
            'Data Science': {
                'easy': [
                    "What is {basic_concept} in data science?",
                    "Which {tool} is commonly used for {task}?",
                    "How do you {basic_operation} in data analysis?",
                    "What does {term} mean in data science?"
                ],
                'medium': [
                    "How do you handle {data_issue} in data preprocessing?",
                    "What algorithm would you use for {problem_type}?",
                    "Explain the difference between {method1} and {method2}.",
                    "How do you evaluate {model_type} performance?"
                ],
                'hard': [
                    "Design a machine learning pipeline for {complex_problem}.",
                    "How would you optimize {algorithm} for {large_dataset}?",
                    "Implement {advanced_technique} for {specific_use_case}.",
                    "What are the ethical considerations in {ai_application}?"
                ]
            },
            'Algorithms': {
                'easy': [
                    "What is the time complexity of {basic_algorithm}?",
                    "How does {sorting_algorithm} work?",
                    "What is {data_structure} used for?",
                    "Which algorithm is best for {simple_problem}?"
                ],
                'medium': [
                    "Compare the efficiency of {algorithm1} vs {algorithm2}.",
                    "How would you implement {algorithm} iteratively?",
                    "What are the trade-offs of using {data_structure}?",
                    "Optimize {algorithm} for {specific_constraint}."
                ],
                'hard': [
                    "Design an algorithm to solve {complex_problem} in O({complexity}).",
                    "Prove the correctness of {advanced_algorithm}.",
                    "Implement {sophisticated_algorithm} with {optimization}.",
                    "Analyze the worst-case scenario for {algorithm}."
                ]
            }
        }
        
        # Content pools for filling templates
        self.content_pools = {
            'Python': {
                'action': ['create a list', 'define a function', 'import a module', 'handle exceptions'],
                'concept': ['list comprehension', 'decorator', 'generator', 'class'],
                'function': ['len()', 'range()', 'enumerate()', 'zip()'],
                'task': ['read a file', 'parse JSON', 'connect to database', 'create a loop'],
                'concept1': ['list', 'tuple', 'set', 'dictionary'],
                'concept2': ['tuple', 'set', 'dictionary', 'string'],
                'algorithm': ['binary search', 'quicksort', 'fibonacci', 'factorial'],
                'feature': ['lambda functions', 'context managers', 'metaclasses', 'descriptors']
            },
            'JavaScript': {
                'keyword1': ['let', 'var', 'const', 'function'],
                'keyword2': ['var', 'const', 'arrow function', 'regular function'],
                'action': ['create an array', 'define a function', 'handle events', 'make API calls'],
                'method': ['map()', 'filter()', 'reduce()', 'forEach()'],
                'concept': ['closures', 'hoisting', 'prototypes', 'async/await'],
                'mechanism': ['event loop', 'promises', 'callbacks', 'modules'],
                'feature': ['arrow functions', 'destructuring', 'template literals', 'spread operator']
            },
            'Web Development': {
                'html_tag': ['<div>', '<span>', '<section>', '<article>'],
                'styling_purpose': ['center elements', 'create layouts', 'add animations', 'responsive design'],
                'basic_task': ['create a form', 'add CSS styles', 'link pages', 'validate input'],
                'web_concept': ['responsive design', 'SEO', 'accessibility', 'performance'],
                'feature': ['responsive navigation', 'image optimization', 'form validation', 'lazy loading'],
                'web_technology': ['CSS Grid', 'Flexbox', 'Service Workers', 'Web Components']
            },
            'Data Science': {
                'basic_concept': ['correlation', 'regression', 'classification', 'clustering'],
                'tool': ['pandas', 'numpy', 'matplotlib', 'scikit-learn'],
                'basic_operation': ['clean data', 'visualize data', 'split datasets', 'normalize features'],
                'term': ['overfitting', 'cross-validation', 'feature engineering', 'bias-variance tradeoff'],
                'algorithm': ['linear regression', 'decision trees', 'k-means', 'neural networks'],
                'model_type': ['classification', 'regression', 'clustering', 'recommendation']
            },
            'Algorithms': {
                'basic_algorithm': ['linear search', 'binary search', 'bubble sort', 'insertion sort'],
                'sorting_algorithm': ['quicksort', 'mergesort', 'heapsort', 'radix sort'],
                'data_structure': ['stack', 'queue', 'hash table', 'binary tree'],
                'simple_problem': ['searching', 'sorting', 'counting', 'finding maximum'],
                'algorithm1': ['quicksort', 'mergesort', 'binary search', 'DFS'],
                'algorithm2': ['mergesort', 'heapsort', 'linear search', 'BFS']
            }
        }
    
    def generate_question(self, question_type: str, difficulty: str, category: str) -> Dict[str, Any]:
        """Generate a question using Google Gemini or fallback to templates"""
        try:
            # Try Gemini AI generation first
            if os.getenv('GEMINI_API_KEY'):
                ai_question = self._generate_with_openai(question_type, difficulty, category)
                if ai_question:
                    return ai_question
            
            # Fallback to template-based generation
            return self._generate_with_templates(question_type, difficulty, category)
        except Exception as e:
            print(f"Error generating question: {e}")
            return self._generate_with_templates(question_type, difficulty, category)
    
    def _generate_with_openai(self, question_type: str, difficulty: str, category: str) -> Dict[str, Any]:
        """Generate question using Google Gemini for ANY topic"""
        try:
            if question_type.lower() == 'multiple_choice':
                prompt = f"""Generate a {difficulty} level multiple choice question about {category}.

The question should be educational, accurate, and relevant to {category} regardless of whether it's a programming language, software tool, design tool, or any other topic.

Provide a JSON response with:
- question_text: the question (make it specific to {category})
- options: object with keys A, B, C, D and their text values
- correct_answer: the correct option letter (A, B, C, or D)
- explanation: why the correct answer is right (1-2 sentences)

Make it educational and accurate. Format: {{"question_text": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "correct_answer": "A", "explanation": "..."}}"""
            
            elif question_type.lower() == 'coding':
                prompt = f"""Generate a {difficulty} level coding/practical question about {category}.

The question should be relevant to {category} - if it's a programming language, create a coding problem. If it's a design tool like AutoCAD, create a practical task or scenario question.

Provide a JSON response with:
- question_text: the problem description (adapt to the topic - code for programming, practical task for tools)
- sample_input: example input or scenario
- sample_output: expected output or result
- explanation: hints or approach (2-3 sentences)
- test_cases: array of 3 test cases with input and expected_output (or scenarios and expected results)

Format: {{"question_text": "...", "sample_input": "...", "sample_output": "...", "explanation": "...", "test_cases": [...]}}"""
            
            else:  # essay
                prompt = f"""Generate a {difficulty} level essay question about {category}.

Provide a JSON response with:
- question_text: the essay question
- key_points: array of 3-4 key points that should be covered
- explanation: what makes a good answer (2-3 sentences)

Format: {{"question_text": "...", "key_points": [...], "explanation": "..."}}"""
            
            system_message = f"You are an expert educator creating {difficulty} level {category} questions. You can create questions for ANY topic including programming languages, design tools (AutoCAD, Photoshop, etc.), frameworks, databases, or any other subject. Always respond with valid JSON."
            
            result = gemini_service.generate_json_completion(prompt, system_message, temperature=0.8)
            
            if result:
                # Format the response
                formatted_result = {
                    'question_text': result.get('question_text', ''),
                    'question_type': question_type.lower(),
                    'difficulty_level': difficulty,
                    'category': category
                }
                
                if question_type.lower() == 'multiple_choice':
                    formatted_result['options'] = result.get('options', {})
                    formatted_result['correct_answer'] = result.get('correct_answer', 'A')
                    formatted_result['explanation'] = result.get('explanation', '')
                elif question_type.lower() == 'coding':
                    formatted_result['sample_input'] = result.get('sample_input', '')
                    formatted_result['sample_output'] = result.get('sample_output', '')
                    formatted_result['test_cases'] = result.get('test_cases', [])
                    formatted_result['explanation'] = result.get('explanation', '')
                else:
                    formatted_result['key_points'] = result.get('key_points', [])
                    formatted_result['explanation'] = result.get('explanation', '')
                
                return formatted_result
            
            return None
        except Exception as e:
            print(f"OpenAI question generation error: {e}")
            return None
    
    def _generate_with_templates(self, question_type: str, difficulty: str, category: str) -> Dict[str, Any]:
        """Fallback template-based generation"""
        try:
            # Normalize inputs
            difficulty = difficulty.lower()
            category = category.replace(' ', '_').replace('-', '_')
            
            # Get appropriate template
            if category in self.question_templates and difficulty in self.question_templates[category]:
                templates = self.question_templates[category][difficulty]
                template = random.choice(templates)
                
                # Fill template with content
                question_text = self._fill_template(template, category)
                
                # Generate options for multiple choice
                if question_type.lower() == 'multiple_choice':
                    options, correct_answer = self._generate_options(category, difficulty)
                    return {
                        'question_text': question_text,
                        'question_type': 'multiple_choice',
                        'difficulty_level': difficulty,
                        'category': category.replace('_', ' '),
                        'correct_answer': correct_answer,
                        'options': options,
                        'explanation': self._generate_explanation(question_text, correct_answer, options)
                    }
                else:
                    # For coding or essay questions
                    return {
                        'question_text': question_text,
                        'question_type': question_type.lower(),
                        'difficulty_level': difficulty,
                        'category': category.replace('_', ' '),
                        'correct_answer': self._generate_sample_answer(question_text, question_type, category),
                        'explanation': f'This is a {difficulty} level {question_type} question about {category.replace("_", " ")}.'
                    }
            else:
                # Fallback for unsupported categories
                return self._generate_fallback_question(question_type, difficulty, category)
                
        except Exception as e:
            print(f"Error generating question: {e}")
            return self._generate_fallback_question(question_type, difficulty, category)
    
    def _fill_template(self, template: str, category: str) -> str:
        """Fill template with appropriate content"""
        if category in self.content_pools:
            content_pool = self.content_pools[category]
            
            # Find placeholders in template
            import re
            placeholders = re.findall(r'\{(\w+)\}', template)
            
            filled_template = template
            for placeholder in placeholders:
                if placeholder in content_pool:
                    replacement = random.choice(content_pool[placeholder])
                    filled_template = filled_template.replace(f'{{{placeholder}}}', replacement)
                else:
                    # Generic replacement
                    filled_template = filled_template.replace(f'{{{placeholder}}}', f'[{placeholder}]')
            
            return filled_template
        
        return template
    
    def _generate_options(self, category: str, difficulty: str) -> tuple:
        """Generate multiple choice options"""
        # Sample options based on category
        option_pools = {
            'Python': {
                'A': ['x = 5', 'list.append()', 'def function():', 'import module'],
                'B': ['var x = 5', 'list.push()', 'function() {}', 'require module'],
                'C': ['int x = 5', 'list.add()', 'void function()', '#include module'],
                'D': ['x := 5', 'list.insert()', 'func function()', 'using module']
            },
            'JavaScript': {
                'A': ['let x = 5', 'array.push()', 'function() {}', 'const result'],
                'B': ['var x = 5', 'array.append()', 'def function():', 'let result'],
                'C': ['int x = 5', 'array.add()', 'void function()', 'var result'],
                'D': ['x = 5', 'array.insert()', 'function function()', 'final result']
            }
        }
        
        if category.replace('_', ' ') in option_pools:
            pool = option_pools[category.replace('_', ' ')]
            options = {}
            for key in ['A', 'B', 'C', 'D']:
                options[key] = random.choice(pool[key])
            correct_answer = random.choice(['A', 'B', 'C', 'D'])
        else:
            # Generic options
            options = {
                'A': f'Option A for {category}',
                'B': f'Option B for {category}',
                'C': f'Option C for {category}',
                'D': f'Option D for {category}'
            }
            correct_answer = 'A'
        
        return options, correct_answer
    
    def _generate_explanation(self, question: str, correct_answer: str, options: dict) -> str:
        """Generate explanation for the correct answer"""
        return f"The correct answer is {correct_answer}: {options[correct_answer]}. This is the standard approach used in this context."
    
    def _generate_sample_answer(self, question: str, question_type: str, category: str) -> str:
        """Generate sample answer for coding/essay questions"""
        if question_type.lower() == 'coding':
            return f"# Sample solution for {category.replace('_', ' ')} question\n# Implementation varies based on specific requirements"
        else:
            return f"Sample answer for this {category.replace('_', ' ')} question would include key concepts and explanations."
    
    def _generate_fallback_question(self, question_type: str, difficulty: str, category: str) -> Dict[str, Any]:
        """Generate a fallback question for ANY topic when templates are not available"""
        # Clean up category name
        category_display = category.replace('_', ' ').title()
        
        if question_type.lower() == 'multiple_choice':
            question_text = f"Which of the following is a key concept in {category_display}?"
            options = {
                'A': f'Basic fundamentals of {category_display}',
                'B': f'Advanced techniques in {category_display}',
                'C': f'Common tools used in {category_display}',
                'D': f'Best practices for {category_display}'
            }
            return {
                'question_text': question_text,
                'question_type': 'multiple_choice',
                'difficulty_level': difficulty,
                'category': category_display,
                'correct_answer': 'A',
                'options': options,
                'explanation': f'Understanding the fundamentals is essential for mastering {category_display}.'
            }
        elif question_type.lower() == 'coding':
            question_text = f"Create a practical solution or demonstration related to {category_display} at {difficulty} level."
            return {
                'question_text': question_text,
                'question_type': 'coding',
                'difficulty_level': difficulty,
                'category': category_display,
                'correct_answer': f'# Solution for {category_display}\n# Implement your solution here',
                'explanation': f'This is a {difficulty} level practical question about {category_display}. Focus on demonstrating your understanding of core concepts.',
                'test_cases': [
                    {'input': 'Example scenario 1', 'expected_output': 'Expected result 1'},
                    {'input': 'Example scenario 2', 'expected_output': 'Expected result 2'},
                    {'input': 'Example scenario 3', 'expected_output': 'Expected result 3'}
                ]
            }
        else:
            question_text = f"Explain an important concept or technique in {category_display}."
            return {
                'question_text': question_text,
                'question_type': question_type.lower(),
                'difficulty_level': difficulty,
                'category': category_display,
                'correct_answer': f'Sample answer for {category_display} question.',
                'explanation': f'This is a {difficulty} level {question_type} question about {category_display}.'
            }

# Global instance
ai_question_generator = AIQuestionGenerator()