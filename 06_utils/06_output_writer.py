"""
Output writing utilities for various formats.
"""

import json
import csv
import gzip
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TextIO
from datetime import datetime
from contextlib import contextmanager


class OutputWriter:
    """Base class for output writers."""
    
    def __init__(self, filepath: str, mode: str = 'w'):
        self.filepath = Path(filepath)
        self.mode = mode
        self._file: Optional[TextIO] = None
        self._count = 0
    
    def open(self):
        """Open output file."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(self.filepath, self.mode, encoding='utf-8')
    
    def close(self):
        """Close output file."""
        if self._file:
            self._file.close()
            self._file = None
    
    def write(self, item: Dict):
        """Write single item."""
        raise NotImplementedError
    
    def write_many(self, items: List[Dict]):
        """Write multiple items."""
        for item in items:
            self.write(item)
    
    @property
    def count(self) -> int:
        """Number of items written."""
        return self._count
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class JsonLinesWriter(OutputWriter):
    """Write JSON Lines format (one JSON object per line)."""
    
    def __init__(self, filepath: str, compress: bool = False):
        super().__init__(filepath)
        self.compress = compress
        if compress and not filepath.endswith('.gz'):
            self.filepath = Path(filepath + '.gz')
    
    def open(self):
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if self.compress:
            self._file = gzip.open(self.filepath, 'wt', encoding='utf-8')
        else:
            self._file = open(self.filepath, 'w', encoding='utf-8')
    
    def write(self, item: Dict):
        """Write item as JSON line."""
        if self._file is None:
            self.open()
        
        self._file.write(json.dumps(item, default=str) + '\n')
        self._count += 1
    
    def flush(self):
        """Flush to disk."""
        if self._file:
            self._file.flush()


class CsvWriter(OutputWriter):
    """Write CSV format."""
    
    def __init__(self, filepath: str, fieldnames: Optional[List[str]] = None):
        super().__init__(filepath)
        self.fieldnames = fieldnames
        self._writer: Optional[csv.DictWriter] = None
        self._header_written = False
    
    def open(self):
        super().open()
        if self.fieldnames:
            self._writer = csv.DictWriter(self._file, fieldnames=self.fieldnames)
    
    def write(self, item: Dict):
        """Write item as CSV row."""
        if self._file is None:
            self.open()
        
        # Auto-detect fieldnames from first item
        if self._writer is None:
            self.fieldnames = list(item.keys())
            self._writer = csv.DictWriter(self._file, fieldnames=self.fieldnames)
        
        # Write header if needed
        if not self._header_written:
            self._writer.writeheader()
            self._header_written = True
        
        self._writer.writerow(item)
        self._count += 1


class JsonArrayWriter(OutputWriter):
    """Write as JSON array."""
    
    def __init__(self, filepath: str, indent: int = 2):
        super().__init__(filepath)
        self.indent = indent
        self._items: List[Dict] = []
    
    def write(self, item: Dict):
        """Add item to array."""
        self._items.append(item)
        self._count += 1
    
    def close(self):
        """Write all items as JSON array."""
        if self._file is None:
            self.open()
        
        json.dump(self._items, self._file, indent=self.indent, default=str)
        super().close()


class MultiFormatWriter:
    """Write to multiple formats simultaneously."""
    
    def __init__(self, base_path: str, formats: List[str] = None):
        """
        Args:
            base_path: Base path without extension
            formats: List of formats: 'jsonl', 'csv', 'json'
        """
        formats = formats or ['jsonl']
        self.writers: List[OutputWriter] = []
        
        for fmt in formats:
            if fmt == 'jsonl':
                self.writers.append(JsonLinesWriter(f"{base_path}.jsonl"))
            elif fmt == 'csv':
                self.writers.append(CsvWriter(f"{base_path}.csv"))
            elif fmt == 'json':
                self.writers.append(JsonArrayWriter(f"{base_path}.json"))
    
    def write(self, item: Dict):
        """Write to all formats."""
        for writer in self.writers:
            writer.write(item)
    
    def open(self):
        for writer in self.writers:
            writer.open()
    
    def close(self):
        for writer in self.writers:
            writer.close()
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def write_items(items: List[Dict], filepath: str, format: str = 'auto'):
    """Convenience function to write items to file."""
    if format == 'auto':
        if filepath.endswith('.jsonl') or filepath.endswith('.jsonl.gz'):
            format = 'jsonl'
        elif filepath.endswith('.csv'):
            format = 'csv'
        elif filepath.endswith('.json'):
            format = 'json'
        else:
            format = 'jsonl'
    
    if format == 'jsonl':
        writer_class = JsonLinesWriter
    elif format == 'csv':
        writer_class = CsvWriter
    elif format == 'json':
        writer_class = JsonArrayWriter
    else:
        raise ValueError(f"Unknown format: {format}")
    
    with writer_class(filepath) as writer:
        writer.write_many(items)
    
    return writer.count
