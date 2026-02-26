#!/usr/bin/env python3
"""
Fix questions that are missing options for multiple choice questions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, Question
from app import app

def fix_question_options():
    """Add default options to multiple choice questions that don't have them"""
    with app.app_context():
        try:
            # Find all multiple choice questions without options
            questions = Question.query.filter_by(
                question_type='multiple_choice',
                is_active=True
            ).all()
            
            fixed_count = 0
            for question in questions:
                if not question.options or (isinstance(question.options, list) and len(question.options) == 0):
                    print(f"Fixing question: {question.question_text[:50]}...")
                    
                    # Generate contextual options based on the correct answer
                    correct = question.correct_answer
                    
                    # Create plausible wrong answers
                    if "dictionary" in question.question_text.lower():
                        question.options = [
                            "Dictionaries are mutable, tuples are immutable",
                            "Dictionaries are immutable, tuples are mutable",
                            "Both are mutable",
                            "Both are immutable"
                        ]
                        if not correct or correct == "":
                            question.correct_answer = "Dictionaries are mutable, tuples are immutable"
                    
                    elif "list" in question.question_text.lower():
                        question.options = [
                            "Lists are mutable and ordered",
                            "Lists are immutable and ordered",
                            "Lists are mutable and unordered",
                            "Lists are immutable and unordered"
                        ]
                        if not correct or correct == "":
                            question.correct_answer = "Lists are mutable and ordered"
                    
                    elif "function" in question.question_text.lower() or "method" in question.question_text.lower():
                        question.options = [
                            "def function_name():",
                            "function function_name():",
                            "func function_name():",
                            "define function_name():"
                        ]
                        if not correct or correct == "":
                            question.correct_answer = "def function_name():"
                    
                    elif "class" in question.question_text.lower():
                        question.options = [
                            "class ClassName:",
                            "Class ClassName:",
                            "define ClassName:",
                            "object ClassName:"
                        ]
                        if not correct or correct == "":
                            question.correct_answer = "class ClassName:"
                    
                    elif "loop" in question.question_text.lower():
                        question.options = [
                            "for and while",
                            "loop and repeat",
                            "iterate and cycle",
                            "do and repeat"
                        ]
                        if not correct or correct == "":
                            question.correct_answer = "for and while"
                    
                    elif "variable" in question.question_text.lower():
                        question.options = [
                            "x = 10",
                            "var x = 10",
                            "int x = 10",
                            "declare x = 10"
                        ]
                        if not correct or correct == "":
                            question.correct_answer = "x = 10"
                    
                    else:
                        # Generic options
                        question.options = [
                            correct if correct else "Option A",
                            "Option B",
                            "Option C",
                            "Option D"
                        ]
                        if not correct or correct == "":
                            question.correct_answer = "Option A"
                    
                    fixed_count += 1
            
            if fixed_count > 0:
                db.session.commit()
                print(f"\n✅ Fixed {fixed_count} questions with missing options")
            else:
                print("\n✅ All multiple choice questions already have options")
            
            # Show summary
            total_mc = Question.query.filter_by(question_type='multiple_choice', is_active=True).count()
            print(f"📊 Total multiple choice questions: {total_mc}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == "__main__":
    print("🔧 Fixing question options...")
    fix_question_options()
