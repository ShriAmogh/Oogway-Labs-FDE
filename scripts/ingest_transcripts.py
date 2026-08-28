#!/usr/bin/env python3
"""
Automated Ingestion Pipeline for Lenny's Podcast Transcripts.
Features:
1. Automatically checks if `transcripts_data/` exists.
2. If missing, automatically clones the official ChatPRD archive (https://github.com/ChatPRD/lennys-podcast-transcripts.git).
3. Connects to PostgreSQL, ensures pgvector extension, and chunks + embeds all transcripts.
4. Provides sample or full archive ingestion modes.

Usage:
    python scripts/ingest_transcripts.py
    python scripts/ingest_transcripts.py --limit 20
    python scripts/ingest_transcripts.py --sample
"""

import os
import sys
import argparse
import asyncio
import subprocess
import glob
import time
import uuid

# Add backend to python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal, init_db
from app.models.database import TranscriptChunkModel
from app.rag.chunker import chunk_transcript
from app.rag.embedder import get_local_embedder
from app.rag.ingest import seed_sample_transcripts_if_empty
from app.core.logging import logger

TRANSCRIPTS_REPO = "https://github.com/ChatPRD/lennys-podcast-transcripts.git"

def ensure_transcripts_data_present(target_dir: str):
    """Checks if transcripts directory exists; if not, clones the ChatPRD archive automatically."""
    episodes_dir = os.path.join(target_dir, "episodes")
    if os.path.exists(episodes_dir) and len(os.listdir(episodes_dir)) > 0:
        print(f"✅ Found existing transcripts archive in: {target_dir}")
        return

    print(f"📥 Transcripts directory not found at '{target_dir}'.")
    print(f"🌐 Automatically cloning transcripts archive from {TRANSCRIPTS_REPO}...")
    
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", TRANSCRIPTS_REPO, target_dir],
            check=True,
            capture_output=False
        )
        print("✅ Clone successful!")
    except Exception as e:
        print(f"⚠️ Git clone failed: {e}. Fallback to sample seed mode.")

async def ingest_archive(target_dir: str, limit: int = None):
    print("🚀 Starting Ingestion of Lenny's Podcast Transcripts into pgvector...")
    start_time = time.time()

    await init_db()

    episodes_dir = os.path.join(target_dir, "episodes")
    if not os.path.exists(episodes_dir):
        # Fallback to sample seeding
        print(f"⚠️ Episodes dir not found at {episodes_dir}. Seeding sample transcripts...")
        async with AsyncSessionLocal() as db:
            seeded = await seed_sample_transcripts_if_empty(db)
            print(f"✅ Seeded {seeded} sample chunks.")
        return

    files = glob.glob(os.path.join(episodes_dir, "**/*.md"), recursive=True)
    files = [f for f in files if not os.path.basename(f).upper().startswith("README") and not os.path.basename(f).upper().startswith("CLAUDE")]
    
    print(f"📁 Found {len(files)} transcript files in archive.")
    if limit:
        files = files[:limit]
        print(f"⚡ Ingesting first {limit} episodes...")

    embedder = get_local_embedder()
    total_chunks = 0

    async with AsyncSessionLocal() as db:
        count_res = await db.execute(select(func.count(TranscriptChunkModel.id)))
        initial_count = count_res.scalar() or 0
        print(f"📊 Current database chunks: {initial_count}")

        for idx, file_path in enumerate(files, 1):
            file_start = time.time()
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            parent_dir = os.path.basename(os.path.dirname(file_path))
            slug = parent_dir if os.path.basename(file_path).startswith("transcript") else os.path.splitext(os.path.basename(file_path))[0]

            chunks = chunk_transcript(content, episode_slug=slug)
            if not chunks:
                continue

            texts_to_embed = [c.content for c in chunks]
            embeddings = embedder.encode(texts_to_embed, batch_size=64, show_progress_bar=False, normalize_embeddings=True)

            for chunk, emb in zip(chunks, embeddings):
                record = TranscriptChunkModel(
                    id=str(uuid.uuid4()),
                    episode_slug=chunk.episode_slug,
                    episode_title=chunk.episode_title,
                    guest=chunk.guest,
                    publish_date=chunk.publish_date,
                    url=chunk.url,
                    chunk_index=chunk.chunk_index,
                    speaker=chunk.speaker,
                    header_section=chunk.header_section,
                    content=chunk.content,
                    token_count=chunk.token_count,
                    embedding=emb.tolist()
                )
                db.add(record)

            await db.commit()
            total_chunks += len(chunks)
            file_elapsed = time.time() - file_start
            guest_name = chunks[0].guest or slug
            print(f"[{idx}/{len(files)}] Ingested {len(chunks)} chunks for {guest_name} ({file_elapsed:.2f}s) | Total: {total_chunks}")

        count_res = await db.execute(select(func.count(TranscriptChunkModel.id)))
        final_count = count_res.scalar() or 0
        total_time = time.time() - start_time
        print(f"\n🎉 INGESTION COMPLETE in {total_time:.2f}s!")
        print(f"📊 Total pgvector chunks in database: {final_count} (+{total_chunks} newly added)")

async def main():
    parser = argparse.ArgumentParser(description="Ingest Lenny's Podcast transcripts into pgvector")
    parser.add_argument("--sample", action="store_true", help="Ingest high-value bundled sample transcripts only")
    parser.add_argument("--dir", type=str, default=None, help="Directory containing markdown transcripts")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files to ingest")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.abspath(args.dir) if args.dir else os.path.join(repo_root, "transcripts_data")

    if args.sample:
        await init_db()
        async with AsyncSessionLocal() as db:
            print("📦 Seeding bundled high-value sample transcripts...")
            count = await seed_sample_transcripts_if_empty(db)
            print(f"✅ Successfully seeded {count} chunks into pgvector.")
    else:
        # Step 1: Ensure transcripts data exists (auto-clone if missing)
        ensure_transcripts_data_present(target_dir)
        # Step 2: Ingest into database
        await ingest_archive(target_dir, limit=args.limit)

if __name__ == "__main__":
    asyncio.run(main())
