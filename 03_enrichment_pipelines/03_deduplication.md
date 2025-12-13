# Deduplication

> **Eliminating Duplicate Records**

Deduplication removes exact or near-duplicate records from your dataset. This is simpler than entity resolution when you only need to remove redundant data.

---

## Deduplication Levels

```
Level 1: Exact Duplicates
         Same values in all fields
         
Level 2: Key Duplicates  
         Same values in key fields (e.g., URL, ID)
         
Level 3: Fuzzy Duplicates
         Similar but not identical (entity resolution territory)
```

---

## 1. Exact Deduplication

### Using Sets (In-Memory)

```python
def dedupe_exact(records, key_fields=None):
    """Remove exact duplicates."""
    seen = set()
    unique = []
    
    for record in records:
        # Create hashable key
        if key_fields:
            key = tuple(record.get(f) for f in key_fields)
        else:
            key = tuple(sorted(record.items()))
        
        if key not in seen:
            seen.add(key)
            unique.append(record)
    
    return unique

# Usage
records = [
    {'url': 'https://a.com', 'title': 'Page A'},
    {'url': 'https://a.com', 'title': 'Page A'},  # Duplicate
    {'url': 'https://b.com', 'title': 'Page B'},
]

unique = dedupe_exact(records, key_fields=['url'])
# 2 records
```

### Using Pandas

```python
import pandas as pd

def dedupe_df(df, subset=None, keep='first'):
    """Remove duplicates from DataFrame."""
    return df.drop_duplicates(subset=subset, keep=keep)

# keep options:
# 'first' - keep first occurrence
# 'last' - keep last occurrence  
# False - drop all duplicates

# Usage
df = pd.DataFrame(records)
df_unique = df.drop_duplicates(subset=['url'], keep='first')
```

### Using Hashing

```python
import hashlib
import json

def hash_record(record, fields=None):
    """Create hash of record for deduplication."""
    if fields:
        data = {k: record.get(k) for k in fields}
    else:
        data = record
    
    # Sort keys for consistent hashing
    json_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(json_str.encode()).hexdigest()

def dedupe_by_hash(records, fields=None):
    """Deduplicate using content hashing."""
    seen_hashes = set()
    unique = []
    
    for record in records:
        h = hash_record(record, fields)
        if h not in seen_hashes:
            seen_hashes.add(h)
            unique.append(record)
    
    return unique
```

---

## 2. Streaming Deduplication

For large datasets that don't fit in memory.

### Using Bloom Filters

```python
from pybloom_live import BloomFilter  # pip install pybloom-live

class StreamingDeduplicator:
    """Memory-efficient deduplication using Bloom filter."""
    
    def __init__(self, expected_items=1000000, error_rate=0.001):
        self.bloom = BloomFilter(
            capacity=expected_items,
            error_rate=error_rate
        )
        self.key_fields = None
    
    def set_key_fields(self, fields):
        self.key_fields = fields
        return self
    
    def _make_key(self, record):
        if self.key_fields:
            values = [str(record.get(f, '')) for f in self.key_fields]
        else:
            values = [str(v) for v in sorted(record.items())]
        return '|'.join(values)
    
    def is_duplicate(self, record):
        """Check if record is a duplicate."""
        key = self._make_key(record)
        if key in self.bloom:
            return True  # Probably duplicate (may have false positives)
        self.bloom.add(key)
        return False
    
    def process(self, records):
        """Yield unique records."""
        for record in records:
            if not self.is_duplicate(record):
                yield record

# Usage
deduper = StreamingDeduplicator(expected_items=10_000_000)
deduper.set_key_fields(['url'])

for record in deduper.process(huge_record_stream):
    save(record)
```

### Using Database

```python
import sqlite3

class DatabaseDeduplicator:
    """Persistent deduplication using SQLite."""
    
    def __init__(self, db_path='dedupe.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS seen (
                hash TEXT PRIMARY KEY,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def is_duplicate(self, record, key_fields=None):
        """Check and register record."""
        h = hash_record(record, key_fields)
        
        cursor = self.conn.execute(
            'SELECT 1 FROM seen WHERE hash = ?', (h,)
        )
        
        if cursor.fetchone():
            return True
        
        self.conn.execute('INSERT INTO seen (hash) VALUES (?)', (h,))
        self.conn.commit()
        return False
    
    def process(self, records, key_fields=None):
        """Yield unique records."""
        for record in records:
            if not self.is_duplicate(record, key_fields):
                yield record
    
    def close(self):
        self.conn.close()
```

---

## 3. URL Deduplication

URLs need special handling for normalization.

```python
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def normalize_url(url):
    """Normalize URL for deduplication."""
    parsed = urlparse(url.lower())
    
    # Sort query parameters
    if parsed.query:
        params = parse_qs(parsed.query, keep_blank_values=True)
        # Sort params and their values
        sorted_params = sorted(
            (k, sorted(v)) for k, v in params.items()
        )
        query = urlencode([(k, v) for k, vs in sorted_params for v in vs])
    else:
        query = ''
    
    # Remove default ports
    netloc = parsed.netloc
    if ':80' in netloc and parsed.scheme == 'http':
        netloc = netloc.replace(':80', '')
    if ':443' in netloc and parsed.scheme == 'https':
        netloc = netloc.replace(':443', '')
    
    # Remove trailing slash
    path = parsed.path.rstrip('/') or '/'
    
    # Remove fragment
    normalized = urlunparse((
        parsed.scheme,
        netloc,
        path,
        '',  # params
        query,
        ''   # fragment
    ))
    
    return normalized

def dedupe_urls(urls):
    """Deduplicate URLs with normalization."""
    seen = set()
    unique = []
    
    for url in urls:
        normalized = normalize_url(url)
        if normalized not in seen:
            seen.add(normalized)
            unique.append(url)  # Return original
    
    return unique

# These all normalize to the same URL:
# https://example.com/page
# https://example.com/page/
# https://EXAMPLE.COM/page
# https://example.com/page#section
# https://example.com:443/page
```

---

## 4. Content Deduplication

Detect duplicates based on content similarity.

### SimHash (Near-Duplicate Detection)

```python
import hashlib
import re
from collections import Counter

def simhash(text, hash_bits=64):
    """Calculate SimHash for near-duplicate detection."""
    # Tokenize
    tokens = re.findall(r'\w+', text.lower())
    token_counts = Counter(tokens)
    
    # Initialize vector
    v = [0] * hash_bits
    
    for token, count in token_counts.items():
        # Hash token
        h = int(hashlib.md5(token.encode()).hexdigest(), 16)
        
        for i in range(hash_bits):
            bit = (h >> i) & 1
            if bit:
                v[i] += count
            else:
                v[i] -= count
    
    # Generate fingerprint
    fingerprint = 0
    for i in range(hash_bits):
        if v[i] > 0:
            fingerprint |= (1 << i)
    
    return fingerprint

def hamming_distance(hash1, hash2):
    """Count differing bits."""
    return bin(hash1 ^ hash2).count('1')

def are_near_duplicates(text1, text2, threshold=3):
    """Check if texts are near-duplicates."""
    h1 = simhash(text1)
    h2 = simhash(text2)
    return hamming_distance(h1, h2) <= threshold

# Usage
content_hashes = {}

for article in articles:
    h = simhash(article['content'])
    
    # Check against existing
    is_duplicate = False
    for existing_hash in content_hashes:
        if hamming_distance(h, existing_hash) <= 3:
            is_duplicate = True
            break
    
    if not is_duplicate:
        content_hashes[h] = article
        save(article)
```

### MinHash (Jaccard Similarity)

```python
import random
import hashlib

class MinHash:
    """MinHash for estimating Jaccard similarity."""
    
    def __init__(self, num_hashes=100):
        self.num_hashes = num_hashes
        # Generate hash functions (a*x + b) mod p
        self.hash_funcs = [
            (random.randint(1, 2**32), random.randint(0, 2**32))
            for _ in range(num_hashes)
        ]
        self.p = 2**33 - 355  # Large prime
    
    def get_signature(self, tokens):
        """Get MinHash signature for token set."""
        signature = []
        
        for a, b in self.hash_funcs:
            min_hash = float('inf')
            for token in tokens:
                # Hash the token
                h = int(hashlib.md5(token.encode()).hexdigest(), 16)
                # Apply hash function
                hash_val = (a * h + b) % self.p
                min_hash = min(min_hash, hash_val)
            signature.append(min_hash)
        
        return signature
    
    def similarity(self, sig1, sig2):
        """Estimate Jaccard similarity from signatures."""
        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return matches / len(sig1)

# Usage
minhash = MinHash(num_hashes=100)

def tokenize(text):
    return set(text.lower().split())

sigs = {}
for doc_id, doc in documents.items():
    tokens = tokenize(doc['content'])
    sig = minhash.get_signature(tokens)
    
    # Find similar documents
    for other_id, other_sig in sigs.items():
        similarity = minhash.similarity(sig, other_sig)
        if similarity > 0.8:
            print(f"Duplicate: {doc_id} ~ {other_id} ({similarity:.2f})")
    
    sigs[doc_id] = sig
```

---

## 5. Incremental Deduplication

For ongoing scraping operations.

```python
import json
from datetime import datetime

class IncrementalDeduplicator:
    """Deduplicate across scraping runs."""
    
    def __init__(self, state_file='dedupe_state.json'):
        self.state_file = state_file
        self.seen = self._load_state()
    
    def _load_state(self):
        try:
            with open(self.state_file) as f:
                return set(json.load(f))
        except FileNotFoundError:
            return set()
    
    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(list(self.seen), f)
    
    def is_new(self, record, key_fields):
        """Check if record is new."""
        key = '|'.join(str(record.get(f, '')) for f in key_fields)
        h = hashlib.md5(key.encode()).hexdigest()
        
        if h in self.seen:
            return False
        
        self.seen.add(h)
        return True
    
    def process(self, records, key_fields):
        """Yield only new records."""
        new_count = 0
        for record in records:
            if self.is_new(record, key_fields):
                new_count += 1
                yield record
        
        # Save state after processing
        self._save_state()
        print(f"Found {new_count} new records")
    
    def clear(self):
        """Clear all state."""
        self.seen = set()
        self._save_state()

# Usage across multiple runs
deduper = IncrementalDeduplicator('products_seen.json')

for record in deduper.process(new_scrape_results, ['url']):
    save_to_database(record)
```

---

## Summary

| Method | Use Case | Memory | Speed |
|--------|----------|--------|-------|
| Set/Dict | Small datasets | O(n) | Fast |
| Pandas | DataFrames | O(n) | Fast |
| Bloom Filter | Large streams | Fixed | Fast |
| Database | Persistent | Disk | Medium |
| SimHash | Content | O(n) | Medium |
| MinHash | Text similarity | O(n) | Slow |

---

*Next: [04_schema_normalization.md](04_schema_normalization.md) - Standardizing data structures*
