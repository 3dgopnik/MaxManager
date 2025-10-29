#!/usr/bin/env python3
"""Base parser for ini parameters from multiple sources"""
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime

@dataclass
class ParameterInfo:
    """Parsed parameter information"""
    name: str
    section: str
    source_url: str
    source_type: str  # 'official' | 'forum' | 'community'
    
    # Main info
    description_en: Optional[str] = None
    description_ru: Optional[str] = None
    recommended_en: Optional[str] = None
    recommended_ru: Optional[str] = None
    
    # Metadata
    introduced_in: Optional[str] = None
    deprecated_in: Optional[str] = None
    
    # Examples and warnings
    examples_en: Optional[str] = None
    warnings_en: Optional[str] = None
    
    # Quality flags
    has_description: bool = False
    has_recommendation: bool = False
    is_verified: bool = False
    confidence_score: float = 0.0  # 0.0 - 1.0
    
    # For review
    needs_review: bool = True
    parsed_date: str = None
    
    def __post_init__(self):
        if not self.parsed_date:
            self.parsed_date = datetime.now().isoformat()
        
        # Calculate confidence
        self.has_description = bool(self.description_en)
        self.has_recommendation = bool(self.recommended_en)
        
        score = 0.0
        if self.source_type == 'official': score += 0.5
        if self.has_description: score += 0.2
        if self.has_recommendation: score += 0.2
        if self.introduced_in: score += 0.1
        
        self.confidence_score = min(score, 1.0)

class BaseParser:
    """Base class for all parsers"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.results: List[ParameterInfo] = []
    
    def parse(self, query: str) -> List[ParameterInfo]:
        """Override in child classes"""
        raise NotImplementedError
    
    def validate_parameter(self, param: ParameterInfo) -> bool:
        """Validate if parameter is worth adding"""
        # Must have description
        if not param.has_description:
            return False
        
        # Must have minimum confidence
        if param.confidence_score < 0.3:
            return False
        
        return True
    
    def get_results(self) -> List[ParameterInfo]:
        """Get validated results"""
        return [p for p in self.results if self.validate_parameter(p)]

