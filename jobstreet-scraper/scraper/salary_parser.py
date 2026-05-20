"""
Robust salary parser for JobStreet scraper.
Handles various salary formats, currencies, and types (monthly, yearly, etc.)
"""

import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SalaryType(str, Enum):
    """Types of salary"""
    MONTHLY = "monthly"
    YEARLY = "yearly"
    HOURLY = "hourly"
    UNKNOWN = "unknown"


class Currency(str, Enum):
    """Supported currencies"""
    MYR = "MYR"  # Malaysian Ringgit
    IDR = "IDR"  # Indonesian Rupiah
    SGD = "SGD"  # Singapore Dollar
    USD = "USD"  # US Dollar
    UNKNOWN = "UNKNOWN"


@dataclass
class ParsedSalary:
    """Parsed salary information"""
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_average: Optional[float] = None
    salary_type: SalaryType = SalaryType.UNKNOWN
    currency: Currency = Currency.MYR
    raw_text: str = ""
    is_negotiable: bool = False
    
    def __repr__(self) -> str:
        return (
            f"ParsedSalary(min={self.salary_min}, max={self.salary_max}, "
            f"avg={self.salary_average}, type={self.salary_type}, "
            f"currency={self.currency}, negotiable={self.is_negotiable})"
        )


class SalaryParser:
    """
    Advanced salary parser with support for multiple formats.
    
    Handles formats like:
    - "RM 3,000 - RM 8,000 per month"
    - "RM 5000/month"
    - "Negotiable"
    - "Up to RM 15,000"
    - "RM 50,000 - RM 100,000 per year"
    - "RM5K - RM10K"
    - "RM 100K - RM 150K per annum"
    - "$3,000 - $8,000"
    """
    
    # Regex patterns for various salary formats
    PATTERNS = {
        # Format: "RM 3,000 - RM 8,000 per month"
        "range_with_unit": re.compile(
            r"(RM|USD|\$|SGD|IDR|Rp)\s*([\d.,]+)\s*[-–]\s*(RM|USD|\$|SGD|IDR|Rp)\s*([\d.,]+)\s*(?:per\s+|\/|a\s+)?(month|year|annum|hour|day|week|yearly|monthly|hourly|annually)?",
            re.IGNORECASE
        ),
        # Format: "Up to RM 15,000"
        "up_to": re.compile(
            r"(?:up\s+to|maximum)\s+(RM|USD|\$|SGD|IDR|Rp)\s*([\d.,]+)",
            re.IGNORECASE
        ),
        # Format: "RM 5000/month" or "RM5K" or "Rp 5.000.000"
        "single_value_with_unit": re.compile(
            r"(RM|USD|\$|SGD|IDR|Rp)\s*([\d.,]+(?:\s*[KM])|[\d.,]+)\s*(?:per\s+|\/|a\s+)?(month|year|annum|hour|day|week|yearly|monthly|hourly|annually)?",
            re.IGNORECASE
        ),
        # Format with K/M suffix: "RM 5K - RM 10K"
        "suffix_notation": re.compile(
            r"(RM|USD|\$|SGD|IDR)\s*([\d.]+)\s*[Kk]\s*[-–]\s*(RM|USD|\$|SGD|IDR)\s*([\d.]+)\s*[Kk]",
            re.IGNORECASE
        ),
        # Format: "5000 - 8000" (without currency)
        "numeric_only": re.compile(
            r"(\d{4,})\s*[-–]\s*(\d{4,})"
        ),
    }
    
    SALARY_TYPE_INDICATORS = {
        r"\bmonth|monthly": SalaryType.MONTHLY,
        r"\byear|yearly|annum|annually": SalaryType.YEARLY,
        r"\bhour|hourly": SalaryType.HOURLY,
    }
    
    CURRENCY_INDICATORS = {
        r"\brp\b|rp|rupiah": Currency.IDR,
        r"\brm\b|ringgit": Currency.MYR,
        r"\bsgd\b|singapore": Currency.SGD,
        r"\busd\b|\$": Currency.USD,
        r"\bidr\b|rupiah": Currency.IDR,
    }
    
    @classmethod
    def parse(cls, salary_text: Optional[str]) -> ParsedSalary:
        """
        Parse salary text and extract structured information.
        
        Args:
            salary_text: Raw salary text from the website
            
        Returns:
            ParsedSalary object with parsed information
        """
        result = ParsedSalary(raw_text=salary_text or "")
        
        if not salary_text or not isinstance(salary_text, str):
            return result
        
        salary_text = salary_text.strip()
        
        # Check for negotiable
        if re.search(r"negotiable|ditawarkan|sesuai|terkait|hubungi", salary_text, re.IGNORECASE):
            result.is_negotiable = True
            return result
        
        # Check for "Not specified" or empty
        if re.search(r"not specified|tidak ditentukan|belum ditentukan", salary_text, re.IGNORECASE):
            return result
        
        # Try to parse salary values
        cls._parse_salary_values(salary_text, result)
        
        # Detect salary type
        cls._detect_salary_type(salary_text, result)
        
        # Detect currency
        cls._detect_currency(salary_text, result)
        
        # Calculate average if both min and max exist
        if result.salary_min and result.salary_max:
            result.salary_average = (result.salary_min + result.salary_max) / 2
        
        return result
    
    @classmethod
    def _parse_salary_values(cls, text: str, result: ParsedSalary) -> None:
        """Extract salary min/max values"""
        
        # Try suffix notation first (e.g., "RM 5K - RM 10K")
        match = cls.PATTERNS["suffix_notation"].search(text)
        if match:
            try:
                min_val = float(match.group(2)) * 1000
                max_val = float(match.group(4)) * 1000
                result.salary_min = min_val
                result.salary_max = max_val
                return
            except (ValueError, IndexError):
                pass
        
        # Try range with unit
        match = cls.PATTERNS["range_with_unit"].search(text)
        if match:
            try:
                min_val = cls._parse_number(match.group(2))
                max_val = cls._parse_number(match.group(4))
                result.salary_min = min_val
                result.salary_max = max_val
                return
            except (ValueError, IndexError):
                pass
        
        # Try up to format
        match = cls.PATTERNS["up_to"].search(text)
        if match:
            try:
                max_val = cls._parse_number(match.group(2))
                result.salary_max = max_val
                return
            except (ValueError, IndexError):
                pass
        
        # Try single value
        match = cls.PATTERNS["single_value_with_unit"].search(text)
        if match:
            try:
                value_str = match.group(2)
                if not value_str:
                    return
                value_str = value_str.replace(" ", "")

                if value_str.upper().endswith("K"):
                    value = float(value_str[:-1]) * 1000
                elif value_str.upper().endswith("M"):
                    value = float(value_str[:-1]) * 1000000
                else:
                    value = cls._parse_number(value_str)

                result.salary_min = value
                result.salary_max = value
                return
            except (ValueError, IndexError):
                pass
        
        # Try numeric only (last resort)
        match = cls.PATTERNS["numeric_only"].search(text)
        if match:
            try:
                min_val = int(match.group(1))
                max_val = int(match.group(2))
                if min_val < max_val:  # Validate it's a real range
                    result.salary_min = float(min_val)
                    result.salary_max = float(max_val)
            except (ValueError, IndexError):
                pass
    
    @staticmethod
    def _parse_number(num_str: str) -> float:
        """Convert string number with separators to float"""
        if not num_str:
            return 0.0
        cleaned = num_str.strip().replace(" ", "")

        # If multiple dot separators appear, assume they are thousand separators.
        if cleaned.count('.') > 1:
            cleaned = cleaned.replace('.', '')
        # If multiple comma separators appear, assume they are thousand separators.
        if cleaned.count(',') > 1:
            cleaned = cleaned.replace(',', '')

        # If the string contains both comma and dot, use the last separator as decimal separator.
        if '.' in cleaned and ',' in cleaned:
            if cleaned.rfind('.') > cleaned.rfind(','):
                cleaned = cleaned.replace(',', '')
            else:
                cleaned = cleaned.replace('.', '').replace(',', '.')

        cleaned = cleaned.replace(',', '')
        return float(cleaned)
    
    @classmethod
    def _detect_salary_type(cls, text: str, result: ParsedSalary) -> None:
        """Detect if salary is monthly, yearly, or hourly"""
        text_lower = text.lower()
        
        for pattern, salary_type in cls.SALARY_TYPE_INDICATORS.items():
            if re.search(pattern, text_lower):
                result.salary_type = salary_type
                return
        
        # Default to monthly for JobStreet (most common)
        result.salary_type = SalaryType.MONTHLY
    
    @classmethod
    def _detect_currency(cls, text: str, result: ParsedSalary) -> None:
        """Detect currency from text"""
        text_lower = text.lower()
        
        for pattern, currency in cls.CURRENCY_INDICATORS.items():
            if re.search(pattern, text_lower):
                result.currency = currency
                return
        
        # Default to MYR for JobStreet Indonesia
        result.currency = Currency.MYR
    
    @staticmethod
    def normalize_to_monthly(parsed_salary: ParsedSalary) -> ParsedSalary:
        """
        Normalize salary to monthly rate.
        
        Args:
            parsed_salary: ParsedSalary object
            
        Returns:
            New ParsedSalary with values normalized to monthly
        """
        if parsed_salary.salary_type == SalaryType.YEARLY:
            # Divide by 12
            normalized = ParsedSalary(
                salary_min=parsed_salary.salary_min / 12 if parsed_salary.salary_min else None,
                salary_max=parsed_salary.salary_max / 12 if parsed_salary.salary_max else None,
                salary_average=parsed_salary.salary_average / 12 if parsed_salary.salary_average else None,
                salary_type=SalaryType.MONTHLY,
                currency=parsed_salary.currency,
                raw_text=parsed_salary.raw_text,
                is_negotiable=parsed_salary.is_negotiable,
            )
            return normalized
        elif parsed_salary.salary_type == SalaryType.HOURLY:
            # Estimate monthly: hourly * 8 hours * 22 working days
            multiplier = 8 * 22
            normalized = ParsedSalary(
                salary_min=parsed_salary.salary_min * multiplier if parsed_salary.salary_min else None,
                salary_max=parsed_salary.salary_max * multiplier if parsed_salary.salary_max else None,
                salary_average=parsed_salary.salary_average * multiplier if parsed_salary.salary_average else None,
                salary_type=SalaryType.MONTHLY,
                currency=parsed_salary.currency,
                raw_text=parsed_salary.raw_text,
                is_negotiable=parsed_salary.is_negotiable,
            )
            return normalized
        
        return parsed_salary
    
    @staticmethod
    def to_dict(parsed_salary: ParsedSalary) -> Dict:
        """Convert ParsedSalary to dictionary"""
        return {
            "salary_min": parsed_salary.salary_min,
            "salary_max": parsed_salary.salary_max,
            "salary_average": parsed_salary.salary_average,
            "salary_type": parsed_salary.salary_type.value,
            "currency": parsed_salary.currency.value,
            "is_negotiable": parsed_salary.is_negotiable,
            "raw_text": parsed_salary.raw_text,
        }


# Convenience function
def parse_salary(salary_text: Optional[str]) -> ParsedSalary:
    """Quick function to parse salary text"""
    return SalaryParser.parse(salary_text)
