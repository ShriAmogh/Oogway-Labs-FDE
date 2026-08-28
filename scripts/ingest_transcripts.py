#!/usr/bin/env python3
"""
CLI script to download transcripts from ChatPRD/lennys-podcast-transcripts and index them into pgvector.
Usage:
    python scripts/ingest_transcripts.py --sample
    python scripts/ingest_transcripts.py --download --limit 20
"""

import os
import sys
import argparse
import asyncio
import subprocess

# Add backend to python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from app.core.database import AsyncSessionLocal, init_db
from app.rag.ingest import seed_sample_transcripts_if_empty, ingest_transcripts_from_directory
from app.core.logging import logger

async def main():
    parser = argparse.ArgumentParser(description="Ingest Lenny's Podcast transcripts into pgvector")
    parser.add_argument("--sample", action="store_true", help="Ingest high-value bundled sample transcripts")
    parser.add_argument("--dir", type=str, default="transcripts_data", help="Directory containing markdown transcripts")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files to ingest")
    args = parser.parse_args()

    print("🚀 Initializing Database and pgvector...")
    await init_db()

    async with AsyncSessionLocal() as db:
        if args.sample:
            print("📦 Seeding bundled high-value sample transcripts...")
            count = await seed_sample_transcripts_if_empty(db)
            print(f"✅ Successfully seeded {count} chunks into pgvector.")
        else:
            target_dir = os.path.abspath(args.dir)
            print(f"📂 Ingesting transcripts from {target_dir} (limit={args.limit})...")
            count = await ingest_transcripts_from_directory(db, directory_path=target_dir, limit=args.limit)
            print(f"✅ Successfully indexed {count} chunks into pgvector.")

if __name__ == "__main__":
    asyncio.run(main())
