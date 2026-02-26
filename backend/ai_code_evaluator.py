#!/usr/bin/env python3
"""
AI Code Evaluator Service with Google Gemini Integration (FREE)
This service evaluates coding submissions using AI and test cases
"""

import json
import re
import subprocess
import tempfile
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime
from openai_service import gemini_service

class AICodeEvaluator:
    """AI-powered code evaluator for multiple programming languages"""
    
    def __init__(self):
        self.supported_languages = {
            'python': {
                'extension': '.py',
                'command': 'python',
                'timeout': 10,
                'description': 'Python 3.x'
            },
            'java': {
                'extension': '.java',
                'command': 'javac',
                'run_command': 'java',
                'timeout': 15,
                'description': 'Java 8+'
            },
            'cpp': {
                'extension': '.cpp',
                'command': 'g++',
                'run_command': './a.out',
                'timeout': 15,
                'description': 'C++ 11/14/17'
            },
            'c': {
                'extension': '.c',
                'command': 'gcc',
                'run_command': './a.out',
                'timeout': 15,
                'description': 'C99/C11'
            },
            'javascript': {
                'extension': '.js',
                'command': 'node',
                'timeout': 10,
                'description': 'Node.js'
            },
            'typescript': {
                'extension': '.ts',
                'command': 'tsc',
                'run_command': 'node',
                'timeout': 12,
                'description': 'TypeScript'
            },
            'csharp': {
                'extension': '.cs',
                'command': 'csc',
                'run_command': 'mono',
                'timeout': 15,
                'description': 'C# .NET'
            },
            'go': {
                'extension': '.go',
                'command': 'go',
                'run_command': 'go run',
                'timeout': 12,
                'description': 'Go 1.15+'
            },
            'rust': {
                'extension': '.rs',
                'command': 'rustc',
                'run_command': './main',
                'timeout': 15,
                'description': 'Rust'
            },
            'php': {
                'extension': '.php',
                'command': 'php',
                'timeout': 10,
                'description': 'PHP 7.4+'
            },
            'ruby': {
                'extension': '.rb',
                'command': 'ruby',
                'timeout': 10,
                'description': 'Ruby 2.7+'
            },
            'kotlin': {
                'extension': '.kt',
                'command': 'kotlinc',
                'run_command': 'kotlin',
                'timeout': 15,
                'description': 'Kotlin'
            },
            'swift': {
                'extension': '.swift',
                'command': 'swift',
                'timeout': 12,
                'description': 'Swift 5+'
            },
            'scala': {
                'extension': '.scala',
                'command': 'scalac',
                'run_command': 'scala',
                'timeout': 15,
                'description': 'Scala 2.13+'
            }
        }
    
    def evaluate_code_submission(self, code: str, language: str, test_cases: List[Dict], 
                               question_text: str = "") -> Dict[str, Any]:
        """
        Evaluate code submission against test cases
        
        Args:
            code: The submitted code
            language: Programming language (python, java, cpp, c, javascript)
            test_cases: List of test cases with input/expected_output
            question_text: The original question for context
            
        Returns:
            Dictionary with evaluation results
        """
        try:
            language = language.lower()
            if language not in self.supported_languages:
                return {
                    'success': False,
                    'error': f'Unsupported language: {language}',
                    'score': 0,
                    'total_tests': len(test_cases),
                    'passed_tests': 0
                }
            
            # Basic code validation
            validation_result = self._validate_code(code, language)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'score': 0,
                    'total_tests': len(test_cases),
                    'passed_tests': 0,
                    'compilation_error': True
                }
            
            # Run test cases
            test_results = []
            passed_tests = 0
            
            for i, test_case in enumerate(test_cases):
                result = self._run_test_case(code, language, test_case, i)
                test_results.append(result)
                if result['passed']:
                    passed_tests += 1
            
            # Calculate score
            score = (passed_tests / len(test_cases)) * 100 if test_cases else 0
            
            # AI-based code quality analysis
            quality_analysis = self._analyze_code_quality(code, language, question_text)
            
            return {
                'success': True,
                'score': round(score, 2),
                'total_tests': len(test_cases),
                'passed_tests': passed_tests,
                'test_results': test_results,
                'code_quality': quality_analysis,
                'evaluation_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Evaluation error: {str(e)}',
                'score': 0,
                'total_tests': len(test_cases),
                'passed_tests': 0
            }
    
    def _validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code syntax and basic structure"""
        try:
            # Basic validation checks
            if not code or not code.strip():
                return {'valid': False, 'error': 'Empty code submission'}
            
            # Language-specific validation
            if language == 'python':
                try:
                    compile(code, '<string>', 'exec')
                    return {'valid': True}
                except SyntaxError as e:
                    return {'valid': False, 'error': f'Python syntax error: {str(e)}'}
            
            elif language == 'java':
                # Check for class definition
                if 'class' not in code or 'public static void main' not in code:
                    return {'valid': False, 'error': 'Java code must contain a class with main method'}
                return {'valid': True}
            
            elif language in ['cpp', 'c']:
                # Check for main function
                if 'int main' not in code and 'void main' not in code:
                    return {'valid': False, 'error': f'{language.upper()} code must contain a main function'}
                return {'valid': True}
            
            elif language == 'javascript':
                # Basic JS validation - check for common syntax issues
                if code.count('{') != code.count('}'):
                    return {'valid': False, 'error': 'Mismatched braces in JavaScript code'}
                return {'valid': True}
            
            return {'valid': True}
            
        except Exception as e:
            return {'valid': False, 'error': f'Validation error: {str(e)}'}
    
    def _run_test_case(self, code: str, language: str, test_case: Dict, test_index: int) -> Dict[str, Any]:
        """Run a single test case"""
        try:
            input_data = test_case.get('input', '')
            expected_output = str(test_case.get('expected_output', '')).strip()
            
            # Execute code with input
            actual_output = self._execute_code(code, language, input_data)
            
            if actual_output['success']:
                actual_output_str = str(actual_output['output']).strip()
                passed = self._compare_outputs(expected_output, actual_output_str)
                
                return {
                    'test_index': test_index,
                    'input': input_data,
                    'expected_output': expected_output,
                    'actual_output': actual_output_str,
                    'passed': passed,
                    'execution_time': actual_output.get('execution_time', 0)
                }
            else:
                return {
                    'test_index': test_index,
                    'input': input_data,
                    'expected_output': expected_output,
                    'actual_output': '',
                    'passed': False,
                    'error': actual_output['error'],
                    'execution_time': 0
                }
                
        except Exception as e:
            return {
                'test_index': test_index,
                'input': input_data if 'input_data' in locals() else '',
                'expected_output': expected_output if 'expected_output' in locals() else '',
                'actual_output': '',
                'passed': False,
                'error': f'Test execution error: {str(e)}',
                'execution_time': 0
            }
    
    def _execute_code(self, code: str, language: str, input_data: str) -> Dict[str, Any]:
        """Execute code with given input"""
        try:
            lang_config = self.supported_languages[language]
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create source file
                file_path = os.path.join(temp_dir, f'solution{lang_config["extension"]}')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                start_time = datetime.now()
                
                if language == 'python':
                    result = subprocess.run(
                        ['python', file_path],
                        input=input_data,
                        capture_output=True,
                        text=True,
                        timeout=lang_config['timeout'],
                        cwd=temp_dir
                    )
                
                elif language == 'java':
                    # Compile first
                    compile_result = subprocess.run(
                        ['javac', file_path],
                        capture_output=True,
                        text=True,
                        timeout=lang_config['timeout'],
                        cwd=temp_dir
                    )
                    
                    if compile_result.returncode != 0:
                        return {
                            'success': False,
                            'error': f'Compilation error: {compile_result.stderr}',
                            'output': ''
                        }
                    
                    # Extract class name from file
                    class_name = 'solution'  # Default
                    class_match = re.search(r'public\s+class\s+(\w+)', code)
                    if class_match:
                        class_name = class_match.group(1)
                    
                    # Run
                    result = subprocess.run(
                        ['java', class_name],
                        input=input_data,
                        capture_output=True,
                        text=True,
                        timeout=lang_config['timeout'],
                        cwd=temp_dir
                    )
                
                elif language in ['cpp', 'c']:
                    # Compile first
                    compile_cmd = ['g++' if language == 'cpp' else 'gcc', file_path, '-o', 'solution']
                    compile_result = subprocess.run(
                        compile_cmd,
                        capture_output=True,
                        text=True,
                        timeout=lang_config['timeout'],
                        cwd=temp_dir
                    )
                    
                    if compile_result.returncode != 0:
                        return {
                            'success': False,
                            'error': f'Compilation error: {compile_result.stderr}',
                            'output': ''
                        }
                    
                    # Run
                    result = subprocess.run(
                        ['./solution'],
                        input=input_data,
                        capture_output=True,
                        text=True,
                        timeout=lang_config['timeout'],
                        cwd=temp_dir
                    )
                
                elif language == 'javascript':
                    result = subprocess.run(
                        ['node', file_path],
                        input=input_data,
                        capture_output=True,
                        text=True,
                        timeout=lang_config['timeout'],
                        cwd=temp_dir
                    )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                if result.returncode == 0:
                    return {
                        'success': True,
                        'output': result.stdout,
                        'execution_time': execution_time
                    }
                else:
                    return {
                        'success': False,
                        'error': result.stderr or 'Runtime error',
                        'output': result.stdout,
                        'execution_time': execution_time
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Code execution timed out',
                'output': ''
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Execution error: {str(e)}',
                'output': ''
            }
    
    def _compare_outputs(self, expected: str, actual: str) -> bool:
        """Compare expected and actual outputs"""
        # Normalize whitespace and line endings
        expected_normalized = re.sub(r'\s+', ' ', expected.strip())
        actual_normalized = re.sub(r'\s+', ' ', actual.strip())
        
        # Try exact match first
        if expected_normalized == actual_normalized:
            return True
        
        # Try case-insensitive match
        if expected_normalized.lower() == actual_normalized.lower():
            return True
        
        # Try numeric comparison for floating point numbers
        try:
            expected_float = float(expected_normalized)
            actual_float = float(actual_normalized)
            return abs(expected_float - actual_float) < 1e-6
        except ValueError:
            pass
        
        return False
    
    def _analyze_code_quality(self, code: str, language: str, question_text: str) -> Dict[str, Any]:
        """Analyze code quality using Google Gemini or heuristics"""
        try:
            # Try Gemini AI analysis first
            if os.getenv('GEMINI_API_KEY'):
                ai_analysis = self._analyze_with_openai(code, language, question_text)
                if ai_analysis:
                    return ai_analysis
            
            # Fallback to heuristic analysis
            return self._analyze_with_heuristics(code, language)
        except Exception as e:
            print(f"Code quality analysis error: {e}")
            return self._analyze_with_heuristics(code, language)
    
    def _analyze_with_openai(self, code: str, language: str, question_text: str) -> Dict[str, Any]:
        """Use Google Gemini to analyze code quality"""
        try:
            prompt = f"""Analyze this {language} code for quality:

Question: {question_text}

Code:
```{language}
{code}
```

Provide a JSON response with:
- readability_score: 0-100 (code clarity, naming, structure)
- efficiency_score: 0-100 (algorithm efficiency, performance)
- best_practices_score: 0-100 (follows language conventions)
- overall_score: 0-100 (average of above)
- comments: array of 2-4 specific feedback points (both positive and areas for improvement)

Be constructive and educational. Format: {{"readability_score": 85, "efficiency_score": 75, ...}}"""

            system_message = f"You are an expert {language} code reviewer. Provide constructive feedback. Always respond with valid JSON."
            
            result = gemini_service.generate_json_completion(prompt, system_message, temperature=0.5)
            
            if result:
                return {
                    'readability_score': min(100, max(0, result.get('readability_score', 70))),
                    'efficiency_score': min(100, max(0, result.get('efficiency_score', 70))),
                    'best_practices_score': min(100, max(0, result.get('best_practices_score', 70))),
                    'overall_score': min(100, max(0, result.get('overall_score', 70))),
                    'comments': result.get('comments', [])
                }
            
            return None
        except Exception as e:
            print(f"OpenAI code analysis error: {e}")
            return None
    
    def _analyze_with_heuristics(self, code: str, language: str) -> Dict[str, Any]:
        """Fallback heuristic-based analysis"""
        try:
            analysis = {
                'readability_score': 0,
                'efficiency_score': 0,
                'best_practices_score': 0,
                'comments': []
            }
            
            # Basic readability analysis
            lines = code.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            # Check for comments
            comment_ratio = 0
            if language == 'python':
                comment_lines = [line for line in lines if line.strip().startswith('#')]
                comment_ratio = len(comment_lines) / len(non_empty_lines) if non_empty_lines else 0
            elif language in ['java', 'cpp', 'c', 'javascript']:
                comment_lines = [line for line in lines if '//' in line or '/*' in line]
                comment_ratio = len(comment_lines) / len(non_empty_lines) if non_empty_lines else 0
            
            # Readability scoring
            readability_score = 70  # Base score
            if comment_ratio > 0.1:
                readability_score += 15
                analysis['comments'].append("Good use of comments")
            
            # Check for meaningful variable names
            if language == 'python':
                if re.search(r'\b[a-z_][a-z0-9_]{2,}\b', code):
                    readability_score += 10
                    analysis['comments'].append("Good variable naming")
            
            # Efficiency analysis (basic)
            efficiency_score = 75  # Base score
            
            # Check for nested loops (potential O(n²) complexity)
            nested_loop_pattern = r'for.*for|while.*while|for.*while|while.*for'
            if re.search(nested_loop_pattern, code, re.IGNORECASE):
                efficiency_score -= 15
                analysis['comments'].append("Consider optimizing nested loops")
            
            # Best practices
            best_practices_score = 80  # Base score
            
            if language == 'python':
                # Check for list comprehensions vs loops
                if 'for' in code and '[' in code and ']' in code:
                    best_practices_score += 10
                    analysis['comments'].append("Good use of Python idioms")
            
            analysis['readability_score'] = min(100, max(0, readability_score))
            analysis['efficiency_score'] = min(100, max(0, efficiency_score))
            analysis['best_practices_score'] = min(100, max(0, best_practices_score))
            
            # Overall quality score
            analysis['overall_score'] = round(
                (analysis['readability_score'] + analysis['efficiency_score'] + analysis['best_practices_score']) / 3, 1
            )
            
            return analysis
            
        except Exception as e:
            return {
                'readability_score': 50,
                'efficiency_score': 50,
                'best_practices_score': 50,
                'overall_score': 50,
                'comments': [f'Analysis error: {str(e)}']
            }

    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported programming languages"""
        return {
            'languages': [
                {
                    'id': lang_id,
                    'name': lang_id.title(),
                    'description': config['description'],
                    'extension': config['extension'],
                    'timeout': config['timeout']
                }
                for lang_id, config in self.supported_languages.items()
            ],
            'total_languages': len(self.supported_languages)
        }

# Global instance
ai_code_evaluator = AICodeEvaluator()