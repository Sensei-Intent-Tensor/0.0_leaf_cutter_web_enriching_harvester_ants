# Data Storage Options

> **Where to Put All That Scraped Data**

You've scraped the data—now where does it go? This document covers storage options from simple files to distributed databases.

---

## Storage Decision Tree

```
What are your needs?
│
├── Simple, small datasets
│   └── Files (JSON, CSV, JSONL)
│
├── Structured data, queries needed
│   ├── Relational → PostgreSQL, SQLite
│   └── Document → MongoDB
│
├── Large scale, distributed
│   ├── Data warehouse → BigQuery, Snowflake
│   └── Object storage → S3, GCS
│
└── Real-time processing
    └── Streaming → Kafka, Redis
```

---

## 1. File-Based Storage

### JSON

Best for: Nested data, API responses, small datasets.

```python
import json

# Write
data = [{"title": "Widget", "price": 99.99}]
with open("products.json", "w") as f:
    json.dump(data, f, indent=2)

# Read
with open("products.json") as f:
    data = json.load(f)
```

**Pros:** Human readable, preserves structure, universal
**Cons:** Loads entire file into memory, slow for large files

### JSONL (JSON Lines)

Best for: Large datasets, streaming, append-only.

```python
import json

# Write (append mode)
def save_item(item, filename="data.jsonl"):
    with open(filename, "a") as f:
        f.write(json.dumps(item) + "\n")

# Read (streaming)
def read_jsonl(filename):
    with open(filename) as f:
        for line in f:
            yield json.loads(line)

# Usage
for item in read_jsonl("data.jsonl"):
    process(item)
```

**Pros:** Append-friendly, streaming, line-by-line processing
**Cons:** No random access, slightly larger than JSON

### CSV

Best for: Tabular data, spreadsheet compatibility.

```python
import csv

# Write
data = [{"title": "Widget", "price": 99.99}]
with open("products.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "price"])
    writer.writeheader()
    writer.writerows(data)

# Read
with open("products.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["title"], row["price"])
```

**Pros:** Excel compatible, simple, small size
**Cons:** No nested data, type information lost

### Parquet

Best for: Large datasets, analytics, columnar queries.

```python
import pandas as pd

# Write
df = pd.DataFrame(data)
df.to_parquet("products.parquet")

# Read
df = pd.read_parquet("products.parquet")

# Query specific columns (efficient)
df = pd.read_parquet("products.parquet", columns=["title", "price"])
```

**Pros:** Compressed, fast queries, preserves types
**Cons:** Not human readable, needs pandas/pyarrow

---

## 2. SQLite

Best for: Medium datasets, local storage, single-user.

```python
import sqlite3

# Connect (creates file if not exists)
conn = sqlite3.connect("scraping.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        url TEXT UNIQUE,
        title TEXT,
        price REAL,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert
cursor.execute("""
    INSERT OR REPLACE INTO products (url, title, price)
    VALUES (?, ?, ?)
""", (url, title, price))

# Query
cursor.execute("SELECT * FROM products WHERE price > ?", (100,))
products = cursor.fetchall()

conn.commit()
conn.close()
```

### With Context Manager

```python
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect("scraping.db")
    conn.row_factory = sqlite3.Row  # Dict-like access
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

# Usage
with get_db() as conn:
    cursor = conn.execute("SELECT * FROM products")
    for row in cursor:
        print(row["title"])
```

**Pros:** Zero setup, ACID compliant, SQL queries
**Cons:** Single writer, not for distributed systems

---

## 3. PostgreSQL

Best for: Production systems, multiple users, complex queries.

```python
import psycopg2
from psycopg2.extras import RealDictCursor

# Connect
conn = psycopg2.connect(
    host="localhost",
    database="scraping",
    user="user",
    password="password"
)

# Query with dict results
with conn.cursor(cursor_factory=RealDictCursor) as cur:
    cur.execute("SELECT * FROM products WHERE price > %s", (100,))
    products = cur.fetchall()

# Bulk insert
from psycopg2.extras import execute_values

data = [(url1, title1, price1), (url2, title2, price2)]
with conn.cursor() as cur:
    execute_values(
        cur,
        "INSERT INTO products (url, title, price) VALUES %s",
        data
    )

conn.commit()
conn.close()
```

### With SQLAlchemy ORM

```python
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    title = Column(String)
    price = Column(Float)

engine = create_engine('postgresql://user:pass@localhost/scraping')
Session = sessionmaker(bind=engine)

# Usage
session = Session()
product = Product(url=url, title=title, price=price)
session.add(product)
session.commit()
```

**Pros:** Robust, scalable, full SQL, concurrent access
**Cons:** Requires setup, more complex

---

## 4. MongoDB

Best for: Flexible schemas, document data, rapid prototyping.

```python
from pymongo import MongoClient

# Connect
client = MongoClient("mongodb://localhost:27017")
db = client.scraping
collection = db.products

# Insert one
collection.insert_one({
    "url": url,
    "title": title,
    "price": price,
    "metadata": {
        "scraped_at": datetime.now(),
        "source": "example.com"
    }
})

# Insert many
collection.insert_many(products)

# Query
products = collection.find({"price": {"$gt": 100}})

# Update
collection.update_one(
    {"url": url},
    {"$set": {"price": new_price}},
    upsert=True  # Insert if not exists
)

# Aggregation
pipeline = [
    {"$match": {"price": {"$gt": 50}}},
    {"$group": {"_id": "$category", "avg_price": {"$avg": "$price"}}}
]
results = collection.aggregate(pipeline)
```

**Pros:** Flexible schema, good for nested data, easy to start
**Cons:** No joins, eventual consistency options

---

## 5. Redis

Best for: Caching, queues, real-time data.

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

# Cache responses
def get_cached_or_fetch(url):
    cached = r.get(f"page:{url}")
    if cached:
        return json.loads(cached)
    
    data = fetch(url)
    r.setex(f"page:{url}", 3600, json.dumps(data))  # 1 hour TTL
    return data

# Queue for URLs to scrape
r.lpush("urls:pending", url)
url = r.rpop("urls:pending")

# Set for seen URLs
if not r.sismember("urls:seen", url):
    r.sadd("urls:seen", url)
    scrape(url)

# Rate limiting
key = f"requests:{domain}:{minute}"
count = r.incr(key)
r.expire(key, 60)
if count > MAX_REQUESTS:
    wait()
```

**Pros:** Very fast, built-in TTL, pub/sub support
**Cons:** Memory-only (by default), limited query capability

---

## 6. Cloud Storage

### Amazon S3

```python
import boto3
import json

s3 = boto3.client('s3')

# Upload
s3.put_object(
    Bucket='my-scraping-bucket',
    Key='products/2024-01-15.json',
    Body=json.dumps(data)
)

# Download
response = s3.get_object(Bucket='my-scraping-bucket', Key='products/2024-01-15.json')
data = json.loads(response['Body'].read())

# List objects
response = s3.list_objects_v2(Bucket='my-scraping-bucket', Prefix='products/')
for obj in response['Contents']:
    print(obj['Key'])
```

### Google Cloud Storage

```python
from google.cloud import storage

client = storage.Client()
bucket = client.bucket('my-scraping-bucket')

# Upload
blob = bucket.blob('products/2024-01-15.json')
blob.upload_from_string(json.dumps(data))

# Download
blob = bucket.blob('products/2024-01-15.json')
data = json.loads(blob.download_as_text())
```

**Pros:** Unlimited scale, cheap, durable
**Cons:** No querying (need separate analytics tool)

---

## 7. Data Warehouses

### BigQuery

```python
from google.cloud import bigquery

client = bigquery.Client()

# Load from GCS
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    autodetect=True
)

load_job = client.load_table_from_uri(
    "gs://bucket/products/*.json",
    "dataset.products",
    job_config=job_config
)

# Query
query = """
    SELECT category, AVG(price) as avg_price
    FROM `project.dataset.products`
    GROUP BY category
"""
results = client.query(query)
for row in results:
    print(row.category, row.avg_price)
```

**Pros:** SQL on massive data, serverless, integrates with GCS
**Cons:** Cost can grow, not for real-time

---

## Storage Patterns

### Pattern 1: Incremental Saves

```python
import json
from datetime import datetime

def save_batch(items, prefix="data"):
    """Save batch with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.jsonl"
    
    with open(filename, "w") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")
    
    return filename
```

### Pattern 2: Deduplication

```python
import sqlite3

def save_unique(items, db_path="seen.db"):
    """Only save items not seen before."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seen (
            id TEXT PRIMARY KEY
        )
    """)
    
    new_items = []
    for item in items:
        item_id = item.get('url') or item.get('id')
        cursor.execute("SELECT 1 FROM seen WHERE id = ?", (item_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO seen VALUES (?)", (item_id,))
            new_items.append(item)
    
    conn.commit()
    conn.close()
    return new_items
```

### Pattern 3: Pipeline Storage

```python
# Scrapy-style pipeline
class JsonLinesExporter:
    def __init__(self, filename):
        self.file = open(filename, 'a')
    
    def process_item(self, item):
        self.file.write(json.dumps(item) + "\n")
        self.file.flush()
        return item
    
    def close(self):
        self.file.close()
```

---

## Comparison Table

| Storage | Best For | Scale | Query | Setup |
|---------|----------|-------|-------|-------|
| **JSON/JSONL** | Small projects | Small | None | None |
| **CSV** | Spreadsheets | Small | None | None |
| **SQLite** | Local, single-user | Medium | SQL | Minimal |
| **PostgreSQL** | Production | Large | SQL | Moderate |
| **MongoDB** | Flexible schemas | Large | Limited | Moderate |
| **Redis** | Caching, queues | Medium | Limited | Minimal |
| **S3/GCS** | Archive, scale | Huge | None | Moderate |
| **BigQuery** | Analytics | Huge | SQL | Moderate |

---

## Summary

| Use Case | Recommended |
|----------|-------------|
| **Quick prototype** | JSONL files |
| **Local analysis** | SQLite + Parquet |
| **Production app** | PostgreSQL |
| **Flexible documents** | MongoDB |
| **Need caching** | Redis |
| **Archive at scale** | S3/GCS |
| **Analytics** | BigQuery/Snowflake |

---

*This completes the Tools Ecosystem section and the 00_foundations wiki!*
