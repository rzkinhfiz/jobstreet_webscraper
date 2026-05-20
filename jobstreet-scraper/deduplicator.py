"""Deduplication utilities for JobStreet scraping.

Provides functions to deduplicate job records using job_id primary key
and fallback to title+company+location fingerprint.
"""
from __future__ import annotations

from typing import Iterable, List, Dict


def fingerprint(record: Dict) -> str:
    parts = [
        (record.get('job_title') or '').strip().lower(),
        (record.get('company_name') or '').strip().lower(),
        (record.get('location') or '').strip().lower(),
    ]
    return '||'.join(parts)


def deduplicate(records: Iterable[Dict]) -> List[Dict]:
    seen_ids = set()
    seen_fp = set()
    out = []
    for r in records:
        jid = r.get('job_id')
        if jid and jid in seen_ids:
            continue
        fp = fingerprint(r)
        if not jid and fp in seen_fp:
            continue
        # keep
        out.append(r)
        if jid:
            seen_ids.add(jid)
        seen_fp.add(fp)
    return out
