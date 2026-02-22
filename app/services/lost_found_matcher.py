"""
AI Matching Service for Lost and Found Items
Uses TF-IDF, keyword matching, and category/color matching
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import Dict, Tuple

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
    
    def compare_text_similarity(self, lost_description: str, found_description: str) -> float:
        """
        Compare text similarity using TF-IDF and cosine similarity
        Returns score between 0-100
        """
        if not lost_description or not found_description:
            return 0.0
        
        try:
            # Combine descriptions for vectorization
            texts = [lost_description.lower(), found_description.lower()]
            
            # Fit and transform
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Convert to 0-100 scale
            return float(similarity * 100)
        except Exception as e:
            print(f"Error in text similarity: {e}")
            return 0.0
    
    def compare_keywords(self, lost_item: Dict, found_item: Dict) -> float:
        """
        Compare keywords from item names and descriptions
        Returns score between 0-100
        """
        score = 0.0
        
        # Extract keywords from item names
        lost_name_words = set(re.findall(r'\b\w+\b', lost_item.get('item_name', '').lower()))
        found_name_words = set(re.findall(r'\b\w+\b', found_item.get('item_name', '').lower()))
        
        # Calculate name similarity
        if lost_name_words and found_name_words:
            common_words = lost_name_words.intersection(found_name_words)
            name_similarity = len(common_words) / max(len(lost_name_words), len(found_name_words))
            score += name_similarity * 40  # 40% weight for name match
        
        # Extract keywords from descriptions
        lost_desc_words = set(re.findall(r'\b\w{3,}\b', lost_item.get('description', '').lower()))
        found_desc_words = set(re.findall(r'\b\w{3,}\b', found_item.get('description', '').lower()))
        
        if lost_desc_words and found_desc_words:
            common_desc_words = lost_desc_words.intersection(found_desc_words)
            desc_similarity = len(common_desc_words) / max(len(lost_desc_words), len(found_desc_words))
            score += desc_similarity * 30  # 30% weight for description match
        
        return min(score, 100.0)
    
    def compare_category_color(self, lost_item: Dict, found_item: Dict) -> float:
        """
        Compare category and color matching
        Returns score between 0-100
        """
        score = 0.0
        
        # Category match (exact)
        lost_category = lost_item.get('category', '').lower().strip()
        found_category = found_item.get('category', '').lower().strip()
        
        if lost_category and found_category:
            if lost_category == found_category:
                score += 50  # 50% for exact category match
            elif lost_category in found_category or found_category in lost_category:
                score += 30  # Partial match
        
        # Color match
        lost_color = lost_item.get('color', '').lower().strip()
        found_color = found_item.get('color', '').lower().strip()
        
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
        # TODO: Implement actual image comparison using:
        # - Feature extraction (SIFT, ORB, etc.)
        # - Histogram comparison
        # - Deep learning models
        
        # Placeholder: return 0 for now
        return 0.0
    
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
