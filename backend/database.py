import aiosqlite
import json
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from backend.models import ProductRecord, SourceDocument

logger = logging.getLogger("database")
DB_PATH = Path(__file__).parent / "product_intelligence.db"

async def init_db():
    """Initialize database schema with tables for sources, products, and human edits."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                source_id TEXT PRIMARY KEY,
                source_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                filename TEXT NOT NULL,
                uploaded_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                product_name TEXT,
                category TEXT,
                overall_confidence REAL,
                review_status TEXT,
                record_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS human_edits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                field_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                reviewer TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                reason TEXT
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_products_review_status ON products(review_status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_human_edits_product_id ON human_edits(product_id)")
        await db.commit()

async def check_db_health() -> bool:
    """Execute a simple query to verify SQLite database readiness."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT 1") as cursor:
                row = await cursor.fetchone()
                return row is not None and row[0] == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

async def save_source(source: SourceDocument):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO sources (source_id, source_type, file_path, filename, uploaded_at) VALUES (?, ?, ?, ?, ?)",
            (source.source_id, source.source_type, source.file_path, source.filename, source.uploaded_at.isoformat())
        )
        await db.commit()

async def get_source(source_id: str) -> Optional[SourceDocument]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT source_id, source_type, file_path, filename, uploaded_at FROM sources WHERE source_id = ?", (source_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return SourceDocument(
                    source_id=row[0],
                    source_type=row[1],
                    file_path=row[2],
                    filename=row[3],
                    uploaded_at=row[4]
                )
    return None

async def save_product(product: ProductRecord):
    async with aiosqlite.connect(DB_PATH) as db:
        record_json = product.model_dump_json()
        await db.execute(
            """INSERT OR REPLACE INTO products 
               (product_id, product_name, category, overall_confidence, review_status, record_json, created_at, updated_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                product.product_id,
                str(product.product_name.value) if product.product_name.value else "Unnamed Product",
                str(product.category.value) if product.category.value else "Uncategorized",
                product.overall_confidence,
                product.review_status,
                record_json,
                product.created_at.isoformat(),
                product.updated_at.isoformat()
            )
        )
        await db.commit()

async def get_product(product_id: str) -> Optional[ProductRecord]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT record_json FROM products WHERE product_id = ?", (product_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                data = json.loads(row[0])
                return ProductRecord.model_validate(data)
    return None

async def list_products() -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT product_id, product_name, category, overall_confidence, review_status, updated_at FROM products ORDER BY updated_at DESC") as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "product_id": r[0],
                    "product_name": r[1],
                    "category": r[2],
                    "overall_confidence": r[3],
                    "review_status": r[4],
                    "updated_at": r[5]
                }
                for r in rows
            ]

async def log_edit(product_id: str, field_name: str, old_value: Any, new_value: Any, reviewer: str, timestamp: str, reason: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO human_edits (product_id, field_name, old_value, new_value, reviewer, timestamp, reason)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (product_id, field_name, json.dumps(old_value), json.dumps(new_value), reviewer, timestamp, reason)
        )
        await db.commit()

async def get_product_edits(product_id: str) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT field_name, old_value, new_value, reviewer, timestamp, reason FROM human_edits WHERE product_id = ? ORDER BY timestamp DESC", (product_id,)) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "field_name": r[0],
                    "old_value": json.loads(r[1]) if r[1] else None,
                    "new_value": json.loads(r[2]) if r[2] else None,
                    "reviewer": r[3],
                    "timestamp": r[4],
                    "reason": r[5]
                }
                for r in rows
            ]

async def get_catalog_counts() -> Dict[str, int]:
    """Retrieve aggregate counts for diagnostics reporting."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM products") as c:
            total_products = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM products WHERE review_status != 'approved'") as c:
            pending_review = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM products WHERE review_status = 'approved'") as c:
            approved = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM human_edits") as c:
            total_edits = (await c.fetchone())[0]
        return {
            "total_products": total_products,
            "pending_review": pending_review,
            "approved": approved,
            "total_edits": total_edits
        }
