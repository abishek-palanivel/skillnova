#!/usr/bin/env python3
"""
Test script to verify AI question generation for AutoCAD and other topics
"""

import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_question_generator import ai_question_generator

def test_question_generation():
    """Test question generation for various topics"""
    
    test_cases = [
        ('AutoCAD', 'easy', 'multiple_choice'),
        ('AutoCAD', 'medium', 'multiple_choice'),
        ('AutoCAD', 'hard', 'multiple_choice'),
        ('Photoshop', 'medium', 'multiple_choice'),
        ('Python', 'easy', 'multiple_choice'),
        ('JavaScript', 'medium', 'coding'),
    ]
    
    print("=" * 80)
    print("Testing AI Question Generation")
    print("=" * 80)
    
    for category, difficulty, question_type in test_cases:
        print(f"\n{'='*80}")
        print(f"Testing: {category} | {difficulty} | {question_type}")
        print(f"{'='*80}")
        
        try:
            question = ai_question_generator.generate_question(
                question_type, difficulty, category
            )
            
            print(f"\n✅ SUCCESS!")
            print(f"\nQuestion: {question['question_text']}")
            print(f"Type: {question['question_type']}")
            print(f"Difficulty: {question['difficulty_level']}")
            print(f"Category: {question['category']}")
            
            if question_type == 'multiple_choice':
                print(f"\nOptions:")
                for key, value in question.get('options', {}).items():
                    marker = "✓" if key == question.get('correct_answer') else " "
                    print(f"  [{marker}] {key}: {value}")
                print(f"\nCorrect Answer: {question.get('correct_answer')}")
                print(f"Explanation: {question.get('explanation', 'N/A')}")
            
        except Exception as e:
            print(f"\n❌ FAILED: {str(e)}")
    
    print(f"\n{'='*80}")
    print("Test Complete!")
    print(f"{'='*80}")

if __name__ == '__main__':
    test_question_generation()
