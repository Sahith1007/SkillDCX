"""
AI Certificate Verifier Service

Uses OCR + LLM to extract and validate certificate information:
1. OCR extraction from PDF/PNG
2. LLM validation of extracted data
3. Authenticity checks
4. Consistency validation
"""

import os
import json
from typing import Dict, Optional, Tuple
import base64
import re

try:
    import pytesseract
    from PIL import Image
    import pdf2image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: OCR dependencies not installed. Install with: pip install pytesseract pillow pdf2image")


class AICertificateVerifier:
    """AI-powered certificate verification"""
    
    def __init__(self):
        self.required_fields = [
            'student_name',
            'course_name',
            'issuer_name',
            'issue_date'
        ]
    
    async def verify_certificate(
        self, 
        file_path: str, 
        file_type: str,
        provided_data: Optional[Dict] = None
    ) -> Tuple[bool, Dict, str]:
        """
        Verify certificate authenticity
        
        Args:
            file_path: Path to certificate file
            file_type: 'pdf' or 'image'
            provided_data: Optional manually provided data
        
        Returns:
            (is_valid, extracted_data, error_message)
        """
        
        # Step 1: Extract text from certificate
        extracted_text = await self._extract_text(file_path, file_type)
        
        if not extracted_text:
            return False, {}, "Failed to extract text from certificate"
        
        # Step 2: Parse certificate data
        extracted_data = await self._parse_certificate_data(extracted_text)
        
        # Step 3: Validate against provided data if available
        if provided_data:
            is_consistent, error = self._validate_consistency(
                extracted_data, 
                provided_data
            )
            if not is_consistent:
                return False, extracted_data, error
        
        # Step 4: Check required fields
        missing_fields = [
            field for field in self.required_fields 
            if field not in extracted_data or not extracted_data[field]
        ]
        
        if missing_fields:
            return False, extracted_data, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Step 5: AI validation (authenticity checks)
        is_authentic, confidence, reason = await self._ai_authenticity_check(
            extracted_data,
            extracted_text
        )
        
        extracted_data['ai_confidence'] = confidence
        extracted_data['ai_reason'] = reason
        
        if not is_authentic:
            return False, extracted_data, f"AI validation failed: {reason}"
        
        return True, extracted_data, "Certificate verified successfully"
    
    async def _extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from certificate file using OCR"""
        
        if not OCR_AVAILABLE:
            print("OCR not available, using placeholder extraction")
            return self._placeholder_extraction(file_path)
        
        try:
            if file_type == 'pdf':
                # Convert PDF to images
                images = pdf2image.convert_from_path(file_path)
                text = ""
                for image in images:
                    text += pytesseract.image_to_string(image)
                return text
            else:
                # Direct image OCR
                image = Image.open(file_path)
                return pytesseract.image_to_string(image)
        except Exception as e:
            print(f"OCR extraction error: {e}")
            return self._placeholder_extraction(file_path)
    
    def _placeholder_extraction(self, file_path: str) -> str:
        """Placeholder for when OCR is not available"""
        # In production, this would use actual OCR
        # For now, return empty to force manual data entry
        return ""
    
    async def _parse_certificate_data(self, text: str) -> Dict:
        """Parse certificate data from extracted text using patterns"""
        
        data = {}
        
        # Common certificate patterns
        patterns = {
            'student_name': [
                r'(?:awarded to|presented to|this certifies that)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'(?:name|student):\s*([A-Za-z\s]+)',
            ],
            'course_name': [
                r'(?:course|program|training):\s*([A-Za-z\s]+)',
                r'(?:completed|finished|passed)\s+([A-Za-z\s]+(?:course|program))',
            ],
            'issuer_name': [
                r'(?:issued by|from|by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'(?:university|institute|academy|school):\s*([A-Za-z\s]+)',
            ],
            'issue_date': [
                r'(?:date|issued on|dated):\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})',
            ]
        }
        
        # Try to extract each field
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data[field] = match.group(1).strip()
                    break
        
        return data
    
    def _validate_consistency(
        self, 
        extracted_data: Dict, 
        provided_data: Dict
    ) -> Tuple[bool, str]:
        """Validate that extracted data matches provided data"""
        
        for field in self.required_fields:
            if field in provided_data and field in extracted_data:
                provided_value = provided_data[field].lower().strip()
                extracted_value = extracted_data[field].lower().strip()
                
                # Check for similarity (allow minor differences)
                if not self._is_similar(provided_value, extracted_value):
                    return False, f"Mismatch in {field}: provided '{provided_data[field]}' but extracted '{extracted_data[field]}'"
        
        return True, ""
    
    def _is_similar(self, str1: str, str2: str, threshold: float = 0.8) -> bool:
        """Check if two strings are similar (fuzzy matching)"""
        
        # Simple similarity check (can be enhanced with libraries like fuzzywuzzy)
        if str1 == str2:
            return True
        
        # Check if one is contained in the other
        if str1 in str2 or str2 in str1:
            return True
        
        # Check Levenshtein distance (simple implementation)
        max_len = max(len(str1), len(str2))
        if max_len == 0:
            return True
        
        # Count matching characters
        matches = sum(c1 == c2 for c1, c2 in zip(str1, str2))
        similarity = matches / max_len
        
        return similarity >= threshold
    
    async def _ai_authenticity_check(
        self, 
        data: Dict, 
        full_text: str
    ) -> Tuple[bool, float, str]:
        """
        AI-powered authenticity validation
        
        In production, this would use:
        - LLM (GPT-4, Claude, etc.) for semantic validation
        - ML model trained on fake vs real certificates
        - Pattern recognition for common forgery indicators
        """
        
        # Placeholder validation logic
        # TODO: Integrate with actual AI service
        
        confidence = 0.0
        reasons = []
        
        # Check 1: Required fields present
        if all(field in data for field in self.required_fields):
            confidence += 0.3
            reasons.append("All required fields present")
        
        # Check 2: Reasonable name format
        if 'student_name' in data:
            name = data['student_name']
            if len(name.split()) >= 2 and name[0].isupper():
                confidence += 0.2
                reasons.append("Valid name format")
        
        # Check 3: Reasonable course name
        if 'course_name' in data:
            course = data['course_name']
            if len(course) >= 5:
                confidence += 0.2
                reasons.append("Valid course name")
        
        # Check 4: Has issuer
        if 'issuer_name' in data and len(data['issuer_name']) > 0:
            confidence += 0.15
            reasons.append("Issuer identified")
        
        # Check 5: Has date
        if 'issue_date' in data:
            confidence += 0.15
            reasons.append("Issue date present")
        
        # Determine if authentic based on confidence
        is_authentic = confidence >= 0.7
        reason = " | ".join(reasons) if reasons else "Insufficient data for validation"
        
        return is_authentic, confidence, reason


# Example usage
async def verify_certificate_file(
    file_path: str,
    file_type: str,
    provided_data: Optional[Dict] = None
) -> Dict:
    """
    Convenient wrapper for certificate verification
    
    Returns:
        {
            'verified': bool,
            'extracted_data': dict,
            'confidence': float,
            'message': str
        }
    """
    
    verifier = AICertificateVerifier()
    is_valid, extracted_data, message = await verifier.verify_certificate(
        file_path,
        file_type,
        provided_data
    )
    
    return {
        'verified': is_valid,
        'extracted_data': extracted_data,
        'confidence': extracted_data.get('ai_confidence', 0.0),
        'message': message
    }


if __name__ == "__main__":
    # Test the verifier
    import asyncio
    
    async def test():
        # Test with placeholder data
        test_data = {
            'student_name': 'John Doe',
            'course_name': 'Blockchain Development',
            'issuer_name': 'SkillDCX',
            'issue_date': '2025-01-30'
        }
        
        verifier = AICertificateVerifier()
        
        # Simulate verification
        print("Testing AI Certificate Verifier...")
        print(f"Test data: {test_data}")
        
        # Since we don't have a real file, test with mock data
        is_valid, data, message = await verifier.verify_certificate(
            "test.pdf",
            "pdf",
            test_data
        )
        
        print(f"\nResult: {'VALID' if is_valid else 'INVALID'}")
        print(f"Message: {message}")
        print(f"Extracted data: {data}")
    
    asyncio.run(test())
