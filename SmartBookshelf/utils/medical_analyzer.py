import re
from typing import List, Dict, Any
import streamlit as st

class MedicalAnalyzer:
    """Analyze medical content and phenotypes for diagnosis suggestions."""
    
    def __init__(self):
        # Medical terminology patterns
        self.syndrome_patterns = [
            r'syndrome',
            r'disorder',
            r'disease',
            r'condition',
            r'malformation',
            r'anomaly'
        ]
        
        # Common craniosynostosis and genetic terms
        self.craniosynostosis_terms = [
            'craniosynostosis', 'synostosis', 'suture', 'sagittal', 'coronal', 
            'metopic', 'lambdoid', 'fontanelle', 'brachycephaly', 'dolichocephaly',
            'trigonocephaly', 'plagiocephaly', 'scaphocephaly', 'cloverleaf skull'
        ]
        
        self.genetic_terms = [
            'mutation', 'gene', 'FGFR1', 'FGFR2', 'FGFR3', 'TWIST1', 'MSX2',
            'chromosome', 'deletion', 'duplication', 'variant', 'polymorphism'
        ]
        
        self.phenotype_terms = [
            'developmental delay', 'hearing loss', 'intellectual disability',
            'growth retardation', 'cardiac', 'skeletal', 'facial', 'limb'
        ]
    
    def extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key medical terms from text.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            List[str]: List of identified medical terms
        """
        text_lower = text.lower()
        found_terms = []
        
        # Combine all term lists
        all_terms = (self.craniosynostosis_terms + 
                    self.genetic_terms + 
                    self.phenotype_terms)
        
        for term in all_terms:
            if term.lower() in text_lower:
                found_terms.append(term)
        
        # Find syndrome names (pattern matching)
        syndrome_matches = re.findall(r'\b[A-Z][a-z]+ [Ss]yndrome\b', text)
        found_terms.extend(syndrome_matches)
        
        return list(set(found_terms))  # Remove duplicates
    
    def analyze_phenotype(self, phenotype_description: str, pdf_text: str) -> List[Dict[str, Any]]:
        """
        Analyze phenotype description against PDF content.
        
        Args:
            phenotype_description (str): Patient phenotype description
            pdf_text (str): Reference PDF text content
            
        Returns:
            List[Dict]: List of diagnosis suggestions with confidence scores
        """
        suggestions = []
        
        # Normalize inputs
        phenotype_lower = phenotype_description.lower()
        pdf_lower = pdf_text.lower()
        
        # Extract features from phenotype description
        phenotype_features = self._extract_features(phenotype_description)
        
        # Find potential conditions in PDF
        potential_conditions = self._find_conditions_in_pdf(pdf_text)
        
        for condition in potential_conditions:
            suggestion = self._analyze_condition_match(
                condition, phenotype_features, pdf_text, phenotype_description
            )
            if suggestion:
                suggestions.append(suggestion)
        
        # Sort by confidence score
        suggestions.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        # Format for display
        formatted_suggestions = []
        for suggestion in suggestions[:5]:  # Top 5 suggestions
            formatted_suggestions.append({
                'condition': suggestion['condition'],
                'confidence': self._format_confidence(suggestion['confidence_score']),
                'matching_features': suggestion['matching_features'],
                'evidence': suggestion['evidence'],
                'additional_info': suggestion.get('additional_info', '')
            })
        
        return formatted_suggestions
    
    def _extract_features(self, phenotype_description: str) -> List[str]:
        """Extract individual phenotypic features from description."""
        features = []
        
        # Split by common delimiters
        parts = re.split(r'[,;\.]\s*', phenotype_description.lower())
        
        for part in parts:
            part = part.strip()
            if part:
                features.append(part)
        
        return features
    
    def _find_conditions_in_pdf(self, pdf_text: str) -> List[str]:
        """Find mentioned medical conditions in PDF text."""
        conditions = []
        
        # Pattern for syndrome names
        syndrome_pattern = r'\b[A-Z][a-zA-Z\s]+ [Ss]yndrome\b'
        syndromes = re.findall(syndrome_pattern, pdf_text)
        conditions.extend(syndromes)
        
        # Pattern for condition names ending with specific terms
        condition_patterns = [
            r'\b[A-Z][a-zA-Z\s]+ craniosynostosis\b',
            r'\b[A-Z][a-zA-Z\s]+ disorder\b',
            r'\b[A-Z][a-zA-Z\s]+ disease\b'
        ]
        
        for pattern in condition_patterns:
            matches = re.findall(pattern, pdf_text)
            conditions.extend(matches)
        
        # Remove duplicates and clean
        conditions = list(set(conditions))
        conditions = [c.strip() for c in conditions if len(c.strip()) > 5]
        
        return conditions
    
    def _analyze_condition_match(self, condition: str, phenotype_features: List[str], 
                                pdf_text: str, phenotype_description: str) -> Dict[str, Any]:
        """Analyze how well a condition matches the phenotype."""
        
        # Find the section of PDF text related to this condition
        condition_context = self._extract_condition_context(condition, pdf_text)
        
        if not condition_context:
            return None
        
        matching_features = []
        evidence_snippets = []
        confidence_score = 0
        
        # Check each phenotype feature against condition context
        for feature in phenotype_features:
            if self._feature_matches_condition(feature, condition_context):
                matching_features.append(feature)
                confidence_score += 10
                
                # Extract evidence snippet
                evidence = self._extract_evidence_snippet(feature, condition_context)
                if evidence:
                    evidence_snippets.append(evidence)
        
        # Boost confidence for exact matches
        if condition.lower() in phenotype_description.lower():
            confidence_score += 20
        
        # Only return suggestions with some confidence
        if confidence_score < 5:
            return None
        
        return {
            'condition': condition.strip(),
            'confidence_score': min(confidence_score, 100),
            'matching_features': matching_features,
            'evidence': '; '.join(evidence_snippets[:3]),  # Top 3 evidence pieces
            'additional_info': self._extract_additional_info(condition, condition_context)
        }
    
    def _extract_condition_context(self, condition: str, pdf_text: str) -> str:
        """Extract relevant context around a condition mention."""
        sentences = pdf_text.split('.')
        context_sentences = []
        
        for sentence in sentences:
            if condition.lower() in sentence.lower():
                context_sentences.append(sentence.strip())
        
        return ' '.join(context_sentences)
    
    def _feature_matches_condition(self, feature: str, condition_context: str) -> bool:
        """Check if a phenotype feature is mentioned in condition context."""
        feature_words = feature.split()
        context_lower = condition_context.lower()
        
        # Check for exact phrase match
        if feature.lower() in context_lower:
            return True
        
        # Check for partial matches (at least 50% of words)
        matching_words = sum(1 for word in feature_words if word.lower() in context_lower)
        return matching_words >= len(feature_words) * 0.5
    
    def _extract_evidence_snippet(self, feature: str, condition_context: str) -> str:
        """Extract a snippet that shows evidence for the feature."""
        sentences = condition_context.split('.')
        
        for sentence in sentences:
            if feature.lower() in sentence.lower():
                return sentence.strip()[:200] + "..." if len(sentence) > 200 else sentence.strip()
        
        return ""
    
    def _extract_additional_info(self, condition: str, condition_context: str) -> str:
        """Extract additional relevant information about the condition."""
        # Look for genetics information
        genetic_info = []
        
        genetic_patterns = [
            r'mutation[s]? in \w+',
            r'gene[s]? \w+',
            r'chromosome \d+',
            r'FGFR\d+',
            r'autosomal \w+'
        ]
        
        for pattern in genetic_patterns:
            matches = re.findall(pattern, condition_context, re.IGNORECASE)
            genetic_info.extend(matches)
        
        if genetic_info:
            return f"Genetic factors: {', '.join(set(genetic_info[:3]))}"
        
        return ""
    
    def _format_confidence(self, score: int) -> str:
        """Format confidence score as descriptive text."""
        if score >= 80:
            return "High confidence"
        elif score >= 50:
            return "Moderate confidence"
        elif score >= 20:
            return "Low confidence"
        else:
            return "Very low confidence"
    
    def analyze_images(self, images: List[bytes]) -> List[str]:
        """
        Analyze medical images from PDF.
        
        Args:
            images (List[bytes]): List of image data
            
        Returns:
            List[str]: List of image analysis descriptions
        """
        analyses = []
        
        for i, image_data in enumerate(images):
            # Since we don't have advanced image analysis capabilities,
            # provide basic information and medical context
            analysis = f"""
Image {i+1} Analysis:
- This appears to be a medical illustration or clinical photograph from the reference document
- Medical images in craniosynostosis literature typically show:
  * Skull morphology and suture patterns
  * CT scan reconstructions showing bone fusion
  * Clinical photographs demonstrating phenotypic features
  * Anatomical diagrams illustrating normal vs. abnormal development
- For detailed image interpretation, consult with a medical professional
- This image should be reviewed in conjunction with the clinical phenotype description
            """.strip()
            
            analyses.append(analysis)
        
        return analyses
