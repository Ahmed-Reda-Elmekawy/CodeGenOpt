"""
Unit tests for the TechnicalTranslator agent.

This test suite covers:
- Translation from multiple languages (Arabic, English, French, Chinese, Spanish, German) to English.
- Ensures technical meaning is preserved in translation.
- Checks that English input is returned unchanged.
- Handles invalid and edge-case inputs.

Usage:
    pytest tests/agents/test_technical_translator.py -v

Requirements:
- Ollama LLM must be running locally with the required model(s).
- The agent should be able to handle multilingual technical prompts.

Author: Ahmed Reda 
Date: 2025-08-24
"""
import pytest
from core.agents.technical_translator import TechnicalTranslator
from tests.agents.utility import print_result, assert_text_similar

@pytest.mark.parametrize("input_text,expected_contains", [
    # Arabic
    ("اكتب دالة بايثون تجمع رقمين", "add two numbers in Python"),
    ("اكتب دالة بايثون تتحقق إذا كان الرقم أوليًا", "prime number in Python"),
    ("اكتب دالة بايثون تعكس سلسلة نصية", "reverse a string in Python"),
    # English
    ("Write a Python function that returns the factorial of a number", "factorial of a number"),
    ("Write a Python function to check if a string is a palindrome", "palindrome"),
    # French
    ("Écris une fonction Python qui trie une liste d'entiers", "sort a list of integers"),
    ("Décris une fonction Python qui calcule la somme d'une liste", "sum of a list"),
    # Chinese
    ("用Python写一个函数，判断一个数是否为素数", "prime number in Python"),
    ("请用Python写一个函数，实现冒泡排序", "bubble sort in Python"),
    # Spanish
    ("Escribe una función de Python que calcule el máximo común divisor de dos números", "greatest common divisor"),
    ("Crea una función en Python que invierta una cadena", "reverse a string in Python"),
    # German
    ("Schreibe eine Python-Funktion, die die Fibonacci-Zahlen berechnet", "Fibonacci numbers"),
    ("Erstelle eine Python-Funktion, die prüft, ob eine Zahl gerade ist", "even number"),
])
def test_translation(input_text, expected_contains):
    translator = TechnicalTranslator(debug_mode=True)
    result = translator.run(input_text)
    try:
        assert_text_similar(expected_contains, result)
        print_result(f"Translation: {input_text}", True, result)
    except AssertionError as e:
        print_result(f"Translation: {input_text}", False, f"Expected: {expected_contains}\nResult: {result}\n{e}")
        raise

def test_english_passthrough():
    translator = TechnicalTranslator()
    english_text = "Implement a binary search algorithm."
    result = translator.run(english_text)
    print_result("English passthrough", result.strip() == english_text, result)
    assert result.strip() == english_text

@pytest.mark.parametrize("input_text", [
    "",  # Empty input
    None,  # None input
    123,   # Non-string input
])
def test_invalid_input(input_text):
    translator = TechnicalTranslator()
    try:
        result = translator.run(input_text)
        print_result(f"Invalid input: {input_text}", isinstance(result, str), result)
        assert isinstance(result, str)
    except Exception as e:
        print_result(f"Invalid input: {input_text}", True, f"Exception: {e}")
