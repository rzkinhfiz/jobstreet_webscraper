"""
Test script for salary parser.
Demonstrates the various salary formats the parser can handle.

Usage:
    python test_salary_parser.py
"""

from scraper.salary_parser import parse_salary, SalaryParser


def test_salary_parsing():
    """Test salary parsing with various formats"""
    
    test_cases = [
        # Standard formats
        "RM 3,000 - RM 8,000 per month",
        "RM 5000/month",
        "RM 5,000 - RM 10,000",
        
        # K/M notation
        "RM5K - RM10K",
        "RM 5K - RM 10K per month",
        "RM 50K - RM 100K per year",
        "RM 100K - RM 150K per annum",
        
        # Yearly salary
        "RM 50,000 - RM 100,000 per year",
        "RM 60000 yearly",
        "RM 500,000 - RM 1,000,000 per annum",
        
        # Single values
        "Up to RM 15,000",
        "RM 25,000",
        "RM 50K",
        "RM 50 K",
        
        # Currency variations
        "$3,000 - $8,000",
        "SGD 3,000 - SGD 8,000",
        "USD 5,000 - USD 10,000",
        "IDR 50,000,000 - IDR 100,000,000",
        
        # Negotiable and special cases
        "Negotiable",
        "Negotiable salary",
        "Ditawarkan sesuai pengalaman",
        "Not specified",
        "Tergantung pengalaman",
        
        # Edge cases
        "2000 - 5000",  # Numeric only
        "",  # Empty
        None,  # None
    ]
    
    print("=" * 80)
    print("SALARY PARSER TEST RESULTS")
    print("=" * 80)
    print()
    
    for salary_text in test_cases:
        result = parse_salary(salary_text)
        
        print(f"Input: {salary_text or '(empty)'}")
        print(f"  └─ Min: {result.salary_min}")
        print(f"  ├─ Max: {result.salary_max}")
        print(f"  ├─ Avg: {result.salary_average}")
        print(f"  ├─ Type: {result.salary_type.value}")
        print(f"  ├─ Currency: {result.currency.value}")
        print(f"  └─ Negotiable: {result.is_negotiable}")
        print()
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


def test_salary_normalization():
    """Test salary normalization to monthly rate"""
    
    print("\n" + "=" * 80)
    print("SALARY NORMALIZATION TEST")
    print("=" * 80)
    print()
    
    test_cases = [
        "RM 3,000 - RM 8,000 per month",
        "RM 50,000 - RM 100,000 per year",
        "RM 150 - RM 200 per hour",
    ]
    
    for salary_text in test_cases:
        parsed = parse_salary(salary_text)
        normalized = SalaryParser.normalize_to_monthly(parsed)
        
        print(f"Original: {salary_text}")
        print(f"  └─ Min: {parsed.salary_min}, Max: {parsed.salary_max}, Type: {parsed.salary_type.value}")
        print(f"Normalized to Monthly:")
        print(f"  └─ Min: {normalized.salary_min}, Max: {normalized.salary_max}, Type: {normalized.salary_type.value}")
        print()
    
    print("=" * 80)


def test_salary_dict_conversion():
    """Test salary dict conversion"""
    
    print("\n" + "=" * 80)
    print("SALARY DICT CONVERSION TEST")
    print("=" * 80)
    print()
    
    salary_text = "RM 5,000 - RM 10,000 per month"
    parsed = parse_salary(salary_text)
    salary_dict = SalaryParser.to_dict(parsed)
    
    print(f"Input: {salary_text}")
    print(f"Output Dictionary:")
    for key, value in salary_dict.items():
        print(f"  └─ {key}: {value}")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    test_salary_parsing()
    test_salary_normalization()
    test_salary_dict_conversion()
