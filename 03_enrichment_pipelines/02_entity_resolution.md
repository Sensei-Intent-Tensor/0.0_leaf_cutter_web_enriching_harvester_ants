# Entity Resolution

> **Matching Records That Represent the Same Thing**

Entity resolution (also called record linkage or deduplication) identifies when different records refer to the same real-world entity.

---

## The Problem

```
Record A: {"name": "Acme Inc.",     "address": "123 Main St"}
Record B: {"name": "ACME, Inc",     "address": "123 Main Street"}
Record C: {"name": "Acme Incorporated", "address": "123 Main St."}

Question: Are these the same company?
```

---

## Resolution Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Block     │───▶│   Compare   │───▶│   Score     │───▶│   Decide    │
│  (Reduce    │    │  (Calculate │    │  (Weight &  │    │  (Match or  │
│   pairs)    │    │   similarity)│    │   combine)  │    │   no match) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## 1. String Similarity Functions

### Exact Match

```python
def exact_match(s1, s2):
    """Case-insensitive exact match."""
    if not s1 or not s2:
        return 0.0
    return 1.0 if s1.lower().strip() == s2.lower().strip() else 0.0
```

### Levenshtein Distance

```python
def levenshtein_distance(s1, s2):
    """Number of single-character edits needed."""
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    
    if len(s2) == 0:
        return len(s1)
    
    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row
    
    return prev_row[-1]

def levenshtein_similarity(s1, s2):
    """Normalized similarity (0-1)."""
    if not s1 or not s2:
        return 0.0
    distance = levenshtein_distance(s1.lower(), s2.lower())
    max_len = max(len(s1), len(s2))
    return 1 - (distance / max_len)

# "ACME Inc" vs "Acme Inc." → 0.89
```

### Jaro-Winkler

```python
def jaro_similarity(s1, s2):
    """Jaro similarity - good for short strings."""
    if not s1 or not s2:
        return 0.0
    
    s1, s2 = s1.lower(), s2.lower()
    
    if s1 == s2:
        return 1.0
    
    len1, len2 = len(s1), len(s2)
    match_distance = max(len1, len2) // 2 - 1
    
    s1_matches = [False] * len1
    s2_matches = [False] * len2
    
    matches = 0
    transpositions = 0
    
    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)
        
        for j in range(start, end):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break
    
    if matches == 0:
        return 0.0
    
    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1
    
    jaro = (matches/len1 + matches/len2 + 
            (matches - transpositions/2)/matches) / 3
    
    return jaro

def jaro_winkler(s1, s2, prefix_weight=0.1):
    """Jaro-Winkler - boosts score for common prefix."""
    jaro = jaro_similarity(s1, s2)
    
    # Find common prefix (up to 4 chars)
    prefix_len = 0
    for i in range(min(len(s1), len(s2), 4)):
        if s1[i].lower() == s2[i].lower():
            prefix_len += 1
        else:
            break
    
    return jaro + prefix_len * prefix_weight * (1 - jaro)

# "ACME Inc" vs "ACME Incorporated" → 0.92
```

### Token-Based Similarity

```python
def jaccard_similarity(s1, s2):
    """Similarity based on shared tokens."""
    if not s1 or not s2:
        return 0.0
    
    tokens1 = set(s1.lower().split())
    tokens2 = set(s2.lower().split())
    
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2
    
    return len(intersection) / len(union) if union else 0.0

def token_sort_ratio(s1, s2):
    """Sort tokens then compare."""
    if not s1 or not s2:
        return 0.0
    
    sorted1 = ' '.join(sorted(s1.lower().split()))
    sorted2 = ' '.join(sorted(s2.lower().split()))
    
    return levenshtein_similarity(sorted1, sorted2)

# "John Smith" vs "Smith John" → 1.0
```

### Phonetic Matching

```python
import re

def soundex(name):
    """Soundex phonetic algorithm."""
    if not name:
        return None
    
    name = name.upper()
    name = re.sub(r'[^A-Z]', '', name)
    
    if not name:
        return None
    
    first = name[0]
    
    # Encoding table
    codes = {
        'BFPV': '1', 'CGJKQSXZ': '2', 'DT': '3',
        'L': '4', 'MN': '5', 'R': '6'
    }
    
    encoded = first
    for char in name[1:]:
        for letters, code in codes.items():
            if char in letters:
                if code != encoded[-1]:
                    encoded += code
                break
    
    # Remove vowels and pad/truncate
    encoded = first + encoded[1:].replace('0', '')
    return (encoded + '000')[:4]

def metaphone_match(s1, s2):
    """Check if strings sound similar."""
    return soundex(s1) == soundex(s2)

# "Smith" and "Smyth" both → S530
```

---

## 2. Blocking Strategies

Comparing every record to every other is O(n²). Blocking reduces this.

```python
class Blocker:
    """Generate candidate pairs using blocking."""
    
    def __init__(self, blocking_keys):
        """
        blocking_keys: list of functions that extract blocking keys
        """
        self.blocking_keys = blocking_keys
    
    def get_blocks(self, records):
        """Group records by blocking key."""
        blocks = {}
        
        for i, record in enumerate(records):
            for key_func in self.blocking_keys:
                key = key_func(record)
                if key:
                    if key not in blocks:
                        blocks[key] = []
                    blocks[key].append(i)
        
        return blocks
    
    def get_candidate_pairs(self, records):
        """Generate pairs to compare."""
        blocks = self.get_blocks(records)
        pairs = set()
        
        for indices in blocks.values():
            for i in range(len(indices)):
                for j in range(i + 1, len(indices)):
                    pair = tuple(sorted([indices[i], indices[j]]))
                    pairs.add(pair)
        
        return pairs

# Blocking key functions
def first_letter_block(record):
    name = record.get('name', '')
    return name[0].upper() if name else None

def zip_block(record):
    return record.get('zip_code', '').strip()[:5]

def soundex_block(record):
    name = record.get('name', '')
    return soundex(name.split()[0]) if name else None

# Usage
blocker = Blocker([first_letter_block, zip_block])
candidates = blocker.get_candidate_pairs(records)
# Compare only records in same block
```

---

## 3. Comparison and Scoring

```python
from dataclasses import dataclass
from typing import Callable, List, Tuple

@dataclass
class ComparisonRule:
    """Rule for comparing a field."""
    field: str
    similarity_func: Callable
    weight: float = 1.0
    missing_value: float = 0.5  # Score when field missing

class EntityMatcher:
    """Match entities based on field comparisons."""
    
    def __init__(self, threshold: float = 0.8):
        self.rules: List[ComparisonRule] = []
        self.threshold = threshold
    
    def add_rule(self, field: str, similarity_func: Callable,
                 weight: float = 1.0, missing_value: float = 0.5):
        """Add a comparison rule."""
        self.rules.append(ComparisonRule(
            field, similarity_func, weight, missing_value
        ))
        return self
    
    def compare(self, record1: dict, record2: dict) -> float:
        """Calculate similarity score between records."""
        total_weight = 0
        total_score = 0
        
        for rule in self.rules:
            val1 = record1.get(rule.field)
            val2 = record2.get(rule.field)
            
            if val1 is None or val2 is None:
                score = rule.missing_value
            else:
                score = rule.similarity_func(val1, val2)
            
            total_score += score * rule.weight
            total_weight += rule.weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def is_match(self, record1: dict, record2: dict) -> bool:
        """Determine if records match."""
        return self.compare(record1, record2) >= self.threshold
    
    def find_matches(self, records: List[dict], 
                     blocker: Blocker = None) -> List[Tuple[int, int, float]]:
        """Find all matching pairs."""
        matches = []
        
        if blocker:
            candidates = blocker.get_candidate_pairs(records)
        else:
            # All pairs (expensive!)
            candidates = [(i, j) for i in range(len(records)) 
                          for j in range(i+1, len(records))]
        
        for i, j in candidates:
            score = self.compare(records[i], records[j])
            if score >= self.threshold:
                matches.append((i, j, score))
        
        return matches

# Usage
matcher = EntityMatcher(threshold=0.85)
matcher.add_rule('name', jaro_winkler, weight=2.0)
matcher.add_rule('address', token_sort_ratio, weight=1.5)
matcher.add_rule('phone', exact_match, weight=1.0)
matcher.add_rule('email', exact_match, weight=1.0)

matches = matcher.find_matches(records, blocker)
```

---

## 4. Clustering Matches

```python
class UnionFind:
    """Union-Find data structure for clustering."""
    
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
    
    def get_clusters(self):
        clusters = {}
        for i in range(len(self.parent)):
            root = self.find(i)
            if root not in clusters:
                clusters[root] = []
            clusters[root].append(i)
        return list(clusters.values())

def cluster_matches(records, matches):
    """Group matched records into clusters."""
    uf = UnionFind(len(records))
    
    for i, j, score in matches:
        uf.union(i, j)
    
    clusters = uf.get_clusters()
    
    # Return records grouped by cluster
    return [[records[i] for i in cluster] for cluster in clusters]
```

---

## 5. Merging Matched Records

```python
def merge_records(records: List[dict], strategy: str = 'most_complete'):
    """Merge multiple records into one."""
    if not records:
        return {}
    if len(records) == 1:
        return records[0].copy()
    
    merged = {}
    
    for key in set().union(*[r.keys() for r in records]):
        values = [r.get(key) for r in records if r.get(key) is not None]
        
        if not values:
            continue
        
        if strategy == 'first':
            merged[key] = values[0]
        
        elif strategy == 'most_common':
            from collections import Counter
            # For hashable values only
            try:
                merged[key] = Counter(values).most_common(1)[0][0]
            except:
                merged[key] = values[0]
        
        elif strategy == 'most_complete':
            # Prefer longer/more complete values
            merged[key] = max(values, key=lambda x: len(str(x)))
        
        elif strategy == 'newest':
            # Requires timestamp field
            merged[key] = values[-1]
        
        elif strategy == 'all':
            # Keep all unique values
            unique = []
            for v in values:
                if v not in unique:
                    unique.append(v)
            merged[key] = unique if len(unique) > 1 else unique[0]
    
    return merged

# Usage
clusters = cluster_matches(records, matches)
deduplicated = [merge_records(cluster) for cluster in clusters]
```

---

## 6. Complete Pipeline

```python
class EntityResolver:
    """Complete entity resolution pipeline."""
    
    def __init__(self, threshold=0.85):
        self.blocker = Blocker([])
        self.matcher = EntityMatcher(threshold)
        self.merge_strategy = 'most_complete'
    
    def add_blocking_key(self, key_func):
        self.blocker.blocking_keys.append(key_func)
        return self
    
    def add_comparison(self, field, similarity_func, weight=1.0):
        self.matcher.add_rule(field, similarity_func, weight)
        return self
    
    def resolve(self, records):
        """Run full resolution pipeline."""
        # Find matches
        matches = self.matcher.find_matches(records, self.blocker)
        
        # Cluster
        clusters = cluster_matches(records, matches)
        
        # Merge
        resolved = [merge_records(cluster, self.merge_strategy) 
                    for cluster in clusters]
        
        return resolved

# Usage
resolver = EntityResolver(threshold=0.85)
resolver.add_blocking_key(first_letter_block)
resolver.add_blocking_key(zip_block)
resolver.add_comparison('name', jaro_winkler, weight=2.0)
resolver.add_comparison('address', token_sort_ratio, weight=1.5)
resolver.add_comparison('phone', exact_match, weight=1.0)

deduplicated = resolver.resolve(scraped_records)
```

---

## Summary

| Technique | Best For | Speed |
|-----------|----------|-------|
| Exact match | IDs, emails | Fast |
| Levenshtein | Short strings, typos | Medium |
| Jaro-Winkler | Names | Medium |
| Jaccard | Descriptions, addresses | Fast |
| Soundex | Names (phonetic) | Fast |
| Token sort | Reordered words | Medium |

---

*Next: [03_deduplication.md](03_deduplication.md) - Removing duplicate records*
