"""
AI Matching Service for Lost and Found Items
Uses TF-IDF, keyword matching, and category/color matching
"""
import re
from difflib import SequenceMatcher
from typing import Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class LostFoundMatcher:
    """Service for matching lost and found items using AI techniques"""
    
    def __init__(self):
        """Initialize the matcher with TF-IDF vectorizer"""
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )

    @staticmethod
    def _normalize_text(value: str) -> str:
        value = (value or '').lower().strip()
        value = re.sub(r'[^a-z0-9\s]', ' ', value)
        value = re.sub(r'\s+', ' ', value).strip()
        return value
    
    def compare_text_similarity(self, lost_description: str, found_description: str) -> float:
        """
        Compare text similarity using TF-IDF and cosine similarity
        Returns score between 0-100
        """
        if not lost_description or not found_description:
            return 0.0
        
        try:
            lost_description = self._normalize_text(lost_description)
            found_description = self._normalize_text(found_description)

            if lost_description == found_description:
                return 100.0

            # Combine descriptions for vectorization
            texts = [lost_description, found_description]
            
            # Fit and transform
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Add sequence similarity to better reward near-identical phrasing.
            sequence_similarity = SequenceMatcher(None, lost_description, found_description).ratio()
            blended_similarity = (0.7 * similarity) + (0.3 * sequence_similarity)
            return float(blended_similarity * 100)
        except Exception as e:
            print(f"Error in text similarity: {e}")
            return 0.0
    
    def compare_keywords(self, lost_item: Dict, found_item: Dict) -> float:
        """
        Compare keywords from item names and descriptions
        Returns score between 0-100
        """
        score = 0.0
        
        lost_name = self._normalize_text(lost_item.get('item_name', ''))
        found_name = self._normalize_text(found_item.get('item_name', ''))

        # Extract keywords from item names
        lost_name_words = set(re.findall(r'\b\w+\b', lost_name))
        found_name_words = set(re.findall(r'\b\w+\b', found_name))
        
        # Calculate name similarity
        if lost_name_words and found_name_words:
            common_words = lost_name_words.intersection(found_name_words)
            name_similarity = len(common_words) / max(len(lost_name_words), len(found_name_words))
            score += name_similarity * 40  # 40% weight for name match
            score += SequenceMatcher(None, lost_name, found_name).ratio() * 20
            if lost_name == found_name:
                score += 25
        
        # Extract keywords from descriptions
        lost_desc = self._normalize_text(lost_item.get('description', ''))
        found_desc = self._normalize_text(found_item.get('description', ''))
        lost_desc_words = set(re.findall(r'\b\w{3,}\b', lost_desc))
        found_desc_words = set(re.findall(r'\b\w{3,}\b', found_desc))
        
        if lost_desc_words and found_desc_words:
            common_desc_words = lost_desc_words.intersection(found_desc_words)
            desc_similarity = len(common_desc_words) / max(len(lost_desc_words), len(found_desc_words))
            score += desc_similarity * 30  # 30% weight for description match
            score += SequenceMatcher(None, lost_desc, found_desc).ratio() * 10
            if lost_desc == found_desc:
                score += 15
        
        return min(score, 100.0)
    
    def compare_category_color(self, lost_item: Dict, found_item: Dict) -> float:
        """
        Compare category and color matching
        Returns score between 0-100
        """
        score = 0.0
        
        # Category match (exact)
        lost_category = self._normalize_text(lost_item.get('category', ''))
        found_category = self._normalize_text(found_item.get('category', ''))
        
        if lost_category and found_category:
            if lost_category == found_category:
                score += 50  # 50% for exact category match
            elif lost_category in found_category or found_category in lost_category:
                score += 30  # Partial match
        
        # Color match
        lost_color = self._normalize_text(lost_item.get('color', ''))
        found_color = self._normalize_text(found_item.get('color', ''))
        
        if lost_color and found_color:
            if lost_color == found_color:
                score += 30  # 30% for exact color match
            elif lost_color in found_color or found_color in lost_color:
                score += 15  # Partial match
        
        return min(score, 100.0)
    
    def compare_image_features(self, lost_image_path: str, found_image_path: str) -> float:
        """
        Placeholder for image feature comparison
        In production, this would use computer vision (OpenCV, PIL, etc.)
        Returns score between 0-100
        """
        # Lightweight deterministic improvement: if the exact image file is the same,
        # treat it as a perfect image match. Full CV can be added later.
        if not lost_image_path or not found_image_path:
            return 0.0
        if self._normalize_text(lost_image_path) == self._normalize_text(found_image_path):
            return 100.0
        return 0.0

    def _exact_match_bonus(self, lost_item: Dict, found_item: Dict) -> float:
        """Bonus points for near-identical records."""
        bonus = 0.0
        if self._normalize_text(lost_item.get('item_name', '')) == self._normalize_text(found_item.get('item_name', '')):
            bonus += 10.0
        if self._normalize_text(lost_item.get('description', '')) == self._normalize_text(found_item.get('description', '')):
            bonus += 8.0
        if self._normalize_text(lost_item.get('category', '')) == self._normalize_text(found_item.get('category', '')):
            bonus += 6.0
        if self._normalize_text(lost_item.get('color', '')) == self._normalize_text(found_item.get('color', '')):
            bonus += 4.0
        if lost_item.get('image_path') and found_item.get('image_path') and self._normalize_text(lost_item.get('image_path', '')) == self._normalize_text(found_item.get('image_path', '')):
            bonus += 12.0
        return min(bonus, 30.0)
    
    def calculate_match_score(self, lost_item: Dict, found_item: Dict) -> float:
        """
        Calculate overall match score combining all comparison methods
        Returns score between 0-100
        """
        scores = []
        weights = []
        
        # Text similarity (TF-IDF)
        text_score = self.compare_text_similarity(
            lost_item.get('description', ''),
            found_item.get('description', '')
        )
        scores.append(text_score)
        weights.append(0.3)  # 30% weight
        
        # Keyword matching
        keyword_score = self.compare_keywords(lost_item, found_item)
        scores.append(keyword_score)
        weights.append(0.3)  # 30% weight
        
        # Category and color matching
        category_color_score = self.compare_category_color(lost_item, found_item)
        scores.append(category_color_score)
        weights.append(0.3)  # 30% weight
        
        # Image matching (placeholder)
        image_score = 0.0
        if lost_item.get('image_path') and found_item.get('image_path'):
            image_score = self.compare_image_features(
                lost_item.get('image_path'),
                found_item.get('image_path')
            )
        scores.append(image_score)
        weights.append(0.1)  # 10% weight (when implemented)
        
        # Calculate weighted average
        total_score = sum(score * weight for score, weight in zip(scores, weights))
        total_weight = sum(weights)
        
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0.0

        final_score += self._exact_match_bonus(lost_item, found_item)
        final_score = min(100.0, final_score)
        return round(final_score, 2)
    
    def find_matches(self, lost_item: Dict, found_items: list, threshold: float = 50.0) -> list:
        """
        Find matching found items for a lost item
        Returns list of tuples (found_item_id, score) sorted by score descending
        """
        matches = []
        
        for found_item in found_items:
            score = self.calculate_match_score(lost_item, found_item)
            
            if score >= threshold:
                matches.append({
                    'found_item_id': found_item.get('id'),
                    'score': score
                })
        
        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches
