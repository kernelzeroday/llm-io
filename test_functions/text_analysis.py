import re
import json
from collections import Counter

def analyze_text(text: str) -> str:
    """
    Comprehensive text analysis function.
    
    Analyzes text and returns detailed statistics including:
    - Character, word, sentence counts
    - Reading level metrics
    - Most common words
    - Text complexity indicators
    
    Args:
        text (str): The text to analyze
        
    Returns:
        str: JSON string with analysis results
    """
    if not text or not isinstance(text, str):
        return json.dumps({"error": "Invalid input: text must be a non-empty string"})
    
    # Basic counts
    char_count = len(text)
    char_count_no_spaces = len(text.replace(' ', ''))
    word_count = len(text.split())
    sentence_count = len(re.findall(r'[.!?]+', text))
    paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
    
    # Word analysis
    words = re.findall(r'\b\w+\b', text.lower())
    unique_words = len(set(words))
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
    most_common = Counter(words).most_common(5)
    
    # Complexity metrics
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    lexical_diversity = unique_words / word_count if word_count > 0 else 0
    
    # Reading level (simplified Flesch formula approximation)
    avg_words_per_sentence = avg_sentence_length
    avg_syllables_per_word = avg_word_length * 0.6  # rough approximation
    flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
    
    if flesch_score >= 90:
        reading_level = "Very Easy"
    elif flesch_score >= 80:
        reading_level = "Easy"
    elif flesch_score >= 70:
        reading_level = "Fairly Easy"
    elif flesch_score >= 60:
        reading_level = "Standard"
    elif flesch_score >= 50:
        reading_level = "Fairly Difficult"
    elif flesch_score >= 30:
        reading_level = "Difficult"
    else:
        reading_level = "Very Difficult"
    
    analysis = {
        "basic_stats": {
            "characters": char_count,
            "characters_no_spaces": char_count_no_spaces,
            "words": word_count,
            "sentences": sentence_count,
            "paragraphs": paragraph_count,
            "unique_words": unique_words
        },
        "averages": {
            "word_length": round(avg_word_length, 2),
            "sentence_length": round(avg_sentence_length, 2),
            "words_per_paragraph": round(word_count / paragraph_count, 2) if paragraph_count > 0 else 0
        },
        "complexity": {
            "lexical_diversity": round(lexical_diversity, 3),
            "flesch_score": round(flesch_score, 1),
            "reading_level": reading_level
        },
        "most_common_words": [{"word": word, "count": count} for word, count in most_common]
    }
    
    return json.dumps(analysis, indent=2) 