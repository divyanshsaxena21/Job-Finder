"""
Job Quality Scoring Service

Analyzes job postings to detect spam, scams, and low-quality opportunities.
Provides quality score for intelligent filtering.
"""

import logging
import re
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class JobQualityScorer:
    """Analyzes job quality and detects red flags"""
    
    # Red flag keywords and patterns
    RED_FLAGS = {
        'spam': [
            'click here', 'call now', 'work from home guaranteed',
            'make money fast', 'easy money', 'no experience needed',
            'too good to be true', 'risk free', 'guaranteed income'
        ],
        'scam': [
            'wire transfer', 'upfront payment', 'application fee',
            'money back guarantee', 'no interview', 'instant hire'
        ],
        'low_effort': [
            'work whenever', 'flexible schedule (too vague)',
            'no deadlines', 'minimal requirements'
        ]
    }
    
    QUALITY_COMPANIES = {
        'google', 'microsoft', 'amazon', 'apple', 'meta', 'netflix',
        'spotify', 'slack', 'stripe', 'figma', 'canva', 'notion',
        'github', 'gitlab', 'jetbrains', 'ibm', 'oracle', 'salesforce'
    }
    
    @staticmethod
    def score_job(
        job_title: str,
        company_name: str,
        description: str,
        salary_min: float = None,
        salary_max: float = None
    ) -> Tuple[int, str, Dict]:
        """
        Score job quality (0-100)
        
        Args:
            job_title: Job title
            company_name: Company name
            description: Full job description
            salary_min: Minimum salary
            salary_max: Maximum salary
        
        Returns:
            Tuple[score (0-100), reason, details]
        """
        score = 100
        reasons = []
        details = {
            'red_flags': [],
            'spam_score': 0,
            'company_score': 50,
            'salary_score': 50,
            'description_score': 50
        }
        
        # Check for red flags in description
        description_lower = description.lower()
        
        for category, keywords in JobQualityScorer.RED_FLAGS.items():
            for keyword in keywords:
                if keyword in description_lower:
                    details['red_flags'].append(keyword)
                    score -= 15
                    reasons.append(f"Red flag: {keyword}")
        
        details['spam_score'] = 100 - (len(details['red_flags']) * 15)
        
        # Check company legitimacy
        company_lower = company_name.lower()
        if any(known in company_lower for known in JobQualityScorer.QUALITY_COMPANIES):
            company_score = 90
            details['company_score'] = 90
        elif len(company_name) < 3:
            company_score = 30
            details['company_score'] = 30
            score -= 20
            reasons.append("Company name too short or suspicious")
        else:
            company_score = 60
            details['company_score'] = 60
        
        # Check description quality
        desc_length = len(description)
        if desc_length < 100:
            score -= 20
            reasons.append(f"Description too short ({desc_length} chars)")
            details['description_score'] = 30
        elif desc_length > 50000:
            score -= 10
            reasons.append("Description unusually long")
            details['description_score'] = 60
        else:
            details['description_score'] = 80
        
        # Check for professional language
        professional_terms = ['responsibilities', 'requirements', 'qualifications', 'benefits']
        professional_count = sum(1 for term in professional_terms if term in description_lower)
        
        if professional_count < 2:
            score -= 15
            reasons.append("Low professional language")
        
        # Check salary sanity
        if salary_min and salary_max:
            if salary_min > 0 and salary_max > 0:
                salary_ratio = salary_max / salary_min
                
                if salary_ratio > 5:  # Min to max difference > 5x
                    score -= 20
                    reasons.append(f"Suspiciously wide salary range ({salary_min} - {salary_max})")
                    details['salary_score'] = 30
                elif salary_min < 10000:  # Unreasonably low
                    score -= 25
                    reasons.append(f"Unreasonably low minimum salary: {salary_min}")
                    details['salary_score'] = 20
                else:
                    details['salary_score'] = 85
        
        # Check for all caps overuse
        all_caps_words = len([w for w in description.split() if w.isupper() and len(w) > 1])
        all_caps_ratio = all_caps_words / max(len(description.split()), 1)
        
        if all_caps_ratio > 0.2:
            score -= 15
            reasons.append(f"Excessive capitalization ({all_caps_ratio*100:.1f}%)")
        
        # Check for excessive punctuation
        punctuation = sum(1 for c in description if c in '!?')
        punct_ratio = punctuation / max(len(description), 1)
        
        if punct_ratio > 0.01:  # More than 1% punctuation
            score -= 10
            reasons.append("Excessive punctuation")
        
        # Check for generic/template language
        generic_phrases = [
            'top candidate', 'must have', 'must be',
            'looking for someone', 'work hard', 'team player'
        ]
        generic_count = sum(1 for phrase in generic_phrases if phrase in description_lower)
        
        if generic_count >= 3:
            score -= 10
            reasons.append("Generic/templated description")
        
        # Ensure score is in valid range
        score = max(0, min(100, score))
        
        reason_text = "; ".join(reasons) if reasons else "Good quality job posting"
        
        logger.info(f"Job quality score: {score} - {reason_text}")
        
        return score, reason_text, details
    
    @staticmethod
    def is_relocation_scam(description: str) -> bool:
        """Check if posting is a relocation/visa scam"""
        red_flags = [
            'visa sponsorship guaranteed',
            'free relocation package',
            'expensive visa process',
            'work anywhere in the world',
            'international opportunity (vague)'
        ]
        
        description_lower = description.lower()
        
        flag_count = sum(1 for flag in red_flags if flag in description_lower)
        
        if flag_count >= 2:
            logger.warning("Potential relocation scam detected")
            return True
        
        return False
    
    @staticmethod
    def detect_pyramid_scheme(description: str, company_name: str) -> bool:
        """Detect pyramid scheme or MLM (multi-level marketing) postings"""
        mlm_keywords = [
            'recruit others', 'build your network', 'earn through referrals',
            'passive income', 'work from home selling', 'commission only',
            'no salary', 'startup costs', 'inventory required'
        ]
        
        suspicious_companies = [
            'herbalife', 'younique', 'lularoe', 'amway', 'primerica'
        ]
        
        description_lower = description.lower()
        company_lower = company_name.lower()
        
        # Check for suspicious company names
        for mlm_company in suspicious_companies:
            if mlm_company in company_lower:
                logger.warning(f"Suspected MLM company: {company_name}")
                return True
        
        # Check for MLM keywords
        keyword_count = sum(1 for kw in mlm_keywords if kw in description_lower)
        
        if keyword_count >= 3:
            logger.warning("Suspected MLM/pyramid scheme posting")
            return True
        
        return False
    
    @staticmethod
    def get_quality_category(score: int) -> str:
        """Get human-readable quality category"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"
    
    @staticmethod
    def should_skip_job(score: int, min_quality: int = 50) -> Tuple[bool, str]:
        """
        Determine if job should be skipped based on quality
        
        Args:
            score: Quality score (0-100)
            min_quality: Minimum acceptable quality (default 50)
        
        Returns:
            Tuple[should_skip, reason]
        """
        if score < min_quality:
            category = JobQualityScorer.get_quality_category(score)
            return True, f"Low quality ({category}, score: {score})"
        
        return False, "Quality check passed"
