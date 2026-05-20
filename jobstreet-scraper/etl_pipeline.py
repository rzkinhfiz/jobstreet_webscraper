#!/usr/bin/env python3
"""ETL pipeline for JobStreet data (standalone script).

Usage:
    python3 etl_pipeline.py --input 'data/raw/*.json' --out-parquet data/processed/etl_output.parquet --out-csv data/processed/etl_output.csv
"""
from __future__ import annotations

import argparse
import glob
import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pandas as pd
from datetime import datetime

# Optional spaCy for improved skill extraction
try:
    import spacy
    from spacy.matcher import PhraseMatcher
    _SPACY_AVAILABLE = True
except Exception:
    spacy = None
    PhraseMatcher = None
    _SPACY_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger('etl')

TITLE_MAP = {
    'software engineer': 'Software Engineer',
    'backend engineer': 'Backend Engineer',
    'frontend engineer': 'Frontend Engineer',
    'data scientist': 'Data Scientist',
    'data engineer': 'Data Engineer',
    'data analyst': 'Data Analyst',
    'machine learning engineer': 'ML Engineer',
}

JOB_CATEGORY_KEYWORDS = {
    'Data Scientist': ['data scientist', 'ml engineer', 'machine learning'],
    'Data Engineer': ['data engineer', 'etl', 'data pipeline'],
    'Data Analyst': ['data analyst', 'business analyst', 'analytics'],
    'ML Engineer': ['machine learning engineer', 'ml engineer'],
    'Software Engineer': ['software engineer', 'backend', 'frontend', 'full stack', 'sde'],
}

COMMON_SKILLS = [
    'python','sql','pandas','numpy','tensorflow','pytorch','aws','gcp','azure','docker','kubernetes','spark','hadoop','java','scala','c++','git','bash'
]


def load_json_files(pattern: str) -> pd.DataFrame:
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f'No files found for pattern: {pattern}')
    rows = []
    for fp in files:
        logger.info(f'Loading {fp}')
        with open(fp, 'r', encoding='utf-8') as f:
            chunk = json.load(f)
            if isinstance(chunk, dict):
                rows.append(chunk)
            else:
                rows.extend(chunk)
    df = pd.DataFrame(rows)
    logger.info(f'Loaded {len(df)} records from {len(files)} files')
    return df


def normalize_title(title: str) -> str:
    if not title or not isinstance(title, str):
        return ''
    t = title.lower()
    for k, v in TITLE_MAP.items():
        if k in t:
            return v
    return title.strip().title()


def extract_experience(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    t = text.lower()
    if re.search(r'\b(senior|sr\b|lead|principal)\b', t):
        return 'Senior'
    if re.search(r'\b(mid|middle|experienced)\b', t):
        return 'Mid'
    if re.search(r'\b(junior|jr\b|entry|trainee|intern)\b', t):
        return 'Junior'
    return None


def standardize_location(loc: Optional[str]) -> str:
    if not loc or not isinstance(loc, str):
        return ''
    t = loc.lower()
    if 'remote' in t or 'work from home' in t or 'wfh' in t:
        return 'Remote'
    if 'jakarta' in t or 'jakarta raya' in t:
        return 'Jakarta'
    if 'bekasi' in t:
        return 'Bekasi'
    if 'tangerang' in t:
        return 'Tangerang'
    return loc.strip().split(',')[0].title()


def map_job_category(title: str, description: str) -> str:
    combined = f"{title or ''} {description or ''}".lower()
    for cat, keywords in JOB_CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in combined:
                return cat
    return 'Other'


def clean_description(text: Optional[str]) -> str:
    if not text or not isinstance(text, str):
        return ''
    txt = re.sub(r'<[^>]+>', ' ', text)
    txt = re.sub(r'\s+', ' ', txt).strip()
    return txt


def extract_skills(text: Optional[str], skills_list: List[str] = COMMON_SKILLS) -> List[str]:
    if not text or not isinstance(text, str):
        return []

    # Try spaCy if available
    if _SPACY_AVAILABLE:
        try:
            # Initialize model and matcher lazily
            if 'nlp' not in globals() or globals().get('nlp') is None:
                try:
                    nlp = spacy.load('en_core_web_sm')
                except Exception:
                    # If model missing, avoid crashing; fall back
                    nlp = None
                globals()['nlp'] = nlp
                if nlp:
                    matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
                    patterns = [nlp.make_doc(s) for s in COMMON_SKILLS]
                    matcher.add('SKILLS', patterns)
                    globals()['_spacy_matcher'] = matcher

            nlp = globals().get('nlp')
            matcher = globals().get('_spacy_matcher')
            found = set()
            if nlp and matcher:
                doc = nlp(text)
                matches = matcher(doc)
                for _, start, end in matches:
                    span = doc[start:end]
                    found.add(span.text.lower())
                # Include named entities that might be tech or products
                for ent in doc.ents:
                    if ent.label_ in ('PRODUCT', 'ORG'):
                        found.add(ent.text.lower())
                # noun chunks as candidates
                for chunk in doc.noun_chunks:
                    txt = chunk.text.strip()
                    if 2 <= len(txt) <= 40 and any(c.isalpha() for c in txt):
                        found.add(txt.lower())
                if found:
                    return sorted(found)
        except Exception:
            # If spaCy fails for any reason, fall back to regex
            pass

    # Fallback regex-based extraction
    t = text.lower()
    found = set()
    for s in skills_list:
        if re.search(r'\b' + re.escape(s) + r"\b", t):
            found.add(s)
    caps = re.findall(r'\b([A-Z][A-Za-z0-9+_\-]{1,30})\b', text)
    for c in caps:
        found.add(c.lower())
    return sorted(found)


def parse_salary_field(salary_raw: Optional[str]) -> Dict[str, Optional[float]]:
    if not salary_raw or not isinstance(salary_raw, str):
        return {'min': None, 'max': None, 'midpoint': None, 'currency': None, 'period': None}
    s = salary_raw.replace('\xa0', ' ').replace('\u200b', '')
    s = s.replace(',', '')
    currency = 'IDR' if 'rp' in s.lower() or 'idr' in s.lower() else ('USD' if '$' in s else None)
    nums = re.findall(r'\d+[\.\d]*', s.replace('\u202f',''))
    clean_nums = []
    for n in nums:
        nn = n.replace('.', '')
        try:
            clean_nums.append(float(nn))
        except Exception:
            continue
    if not clean_nums:
        return {'min': None, 'max': None, 'midpoint': None, 'currency': currency, 'period': None}
    if len(clean_nums) == 1:
        v = clean_nums[0]
        return {'min': v, 'max': v, 'midpoint': v, 'currency': currency, 'period': 'monthly'}
    vmin = min(clean_nums[:2])
    vmax = max(clean_nums[:2])
    midpoint = (vmin + vmax) / 2
    return {'min': vmin, 'max': vmax, 'midpoint': midpoint, 'currency': currency, 'period': 'monthly'}


def feature_engineer(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['job_title'] = df.get('job_title', df.get('job_title', ''))
    df['job_title_norm'] = df['job_title'].astype(str).apply(normalize_title)
    df['experience_from_title'] = df['job_title'].astype(str).apply(extract_experience)
    df['job_description'] = df.get('job_description', '').astype(str)
    df['experience_from_description'] = df['job_description'].apply(extract_experience)
    df['experience_level'] = df['experience_from_title'].fillna(df['experience_from_description'])
    df['location'] = df.get('location', '')
    df['location_std'] = df['location'].astype(str).apply(standardize_location)

    def location_group(loc: str) -> str:
        if loc == 'Remote':
            return 'Remote'
        if loc in ('Jakarta', 'Bekasi', 'Tangerang'):
            return 'Jakarta Area'
        return 'Other'

    df['location_group'] = df['location_std'].apply(location_group)
    df['is_remote'] = df['location'].str.contains('remote', case=False, na=False) | df['location'].str.contains('work from home', case=False, na=False)
    df['job_category'] = df.apply(lambda r: map_job_category(r.get('job_title',''), r.get('job_description','')), axis=1)
    df['skills_extracted'] = df['job_description'].apply(lambda t: extract_skills(t))

    parsed = df['salary'].apply(lambda s: parse_salary_field(s) if not isinstance(s, dict) else {
        'min': s.get('min') or s.get('salary_min') or s.get('salary_minimum'),
        'max': s.get('max') or s.get('salary_max') or s.get('salary_maximum'),
        'midpoint': s.get('average') or s.get('midpoint'),
        'currency': s.get('currency'),
        'period': s.get('type')
    })

    df['salary_min'] = parsed.apply(lambda x: x.get('min'))
    df['salary_max'] = parsed.apply(lambda x: x.get('max'))
    df['salary_midpoint'] = parsed.apply(lambda x: x.get('midpoint'))
    df['salary_mid_millions'] = df['salary_midpoint'].apply(lambda v: (v / 1_000_000) if v else None)
    df['salary_range'] = df.apply(lambda r: (r['salary_max'] - r['salary_min']) if r['salary_max'] and r['salary_min'] else None, axis=1)

    def seniority_from(row) -> str:
        if row['experience_level'] == 'Senior':
            return 'Senior'
        if row['experience_level'] == 'Mid':
            return 'Mid'
        if row['experience_level'] == 'Junior':
            return 'Junior'
        t = (row.get('job_title') or '').lower()
        if 'lead' in t or 'senior' in t or 'principal' in t:
            return 'Senior'
        if 'junior' in t or 'jr' in t or 'intern' in t:
            return 'Junior'
        return 'Unknown'

    df['seniority'] = df.apply(seniority_from, axis=1)
    return df


def save_outputs(df: pd.DataFrame, out_parquet: str, out_csv: Optional[str] = None) -> None:
    Path(out_parquet).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_parquet, index=False)
    logger.info(f'Saved parquet: {out_parquet}')
    if out_csv:
        Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_csv, index=False)
        logger.info(f'Saved csv: {out_csv}')


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.dropna(subset=['salary_midpoint']).groupby('job_category')
    summary = grp['salary_midpoint'].agg(['count', 'mean', 'median']).rename(columns={'count':'n','mean':'mean_salary','median':'median_salary'})
    summary['mean_salary_millions'] = (summary['mean_salary'] / 1_000_000).round(2)
    summary['median_salary_millions'] = (summary['median_salary'] / 1_000_000).round(2)
    return summary.reset_index()


def run_etl(input_pattern: str, out_parquet: str, out_csv: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_raw = load_json_files(input_pattern)
    for c in ['job_title','location','job_description','salary']:
        if c not in df_raw.columns:
            df_raw[c] = None
    df = feature_engineer(df_raw)
    save_outputs(df, out_parquet, out_csv)
    summary = summarize(df)
    logger.info('Summary by job category:')
    logger.info('\n' + summary.to_string(index=False))
    return df, summary


def parse_args(argv=None):
    p = argparse.ArgumentParser(description='ETL pipeline for JobStreet data')
    p.add_argument('--input', default='data/raw/*.json')
    p.add_argument('--out-parquet', default='data/processed/etl_output.parquet')
    p.add_argument('--out-csv', default='data/processed/etl_output.csv')
    return p.parse_args(argv)


if __name__ == '__main__':
    args = parse_args()
    df, summary = run_etl(args.input, args.out_parquet, args.out_csv)
    print('\nTop categories:')
    print(summary.head())
