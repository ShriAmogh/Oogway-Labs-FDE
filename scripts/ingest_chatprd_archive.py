import asyncio
import os
import sys
import glob
import uuid
import time
from typing import List

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from sqlalchemy import select, func, text
from app.core.database import AsyncSessionLocal, engine, init_db
from app.models.database import TranscriptChunkModel
from app.rag.chunker import chunk_transcript
from app.rag.embedder import get_local_embedder

async def ingest_chatprd_archive(batch_limit: int = None):
    print("🚀 Starting Ingestion of Full ChatPRD Lenny's Podcast Archive...")
    start_time = time.time()
    
    # Initialize DB tables & extensions
    await init_db()
    
    episodes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "transcripts_data", "episodes")
    if not os.path.exists(episodes_dir):
        print(f"❌ Error: {episodes_dir} does not exist.")
        return

    files = glob.glob(os.path.join(episodes_dir, "**/*.md"), recursive=True)
    files = [f for f in files if not os.path.basename(f).upper().startswith("README") and not os.path.basename(f).upper().startswith("CLAUDE")]
    
    print(f"📁 Found {len(files)} transcript files in ChatPRD archive.")
    if batch_limit:
        files = files[:batch_limit]
        print(f"⚡ Ingesting first {batch_limit} episodes in this run...")

    embedder = get_local_embedder()
    total_chunks = 0

    async with AsyncSessionLocal() as db:
        # Check current count
        count_res = await db.execute(select(func.count(TranscriptChunkModel.id)))
        initial_count = count_res.scalar() or 0
        print(f"📊 Current database chunks: {initial_count}")

        for idx, file_path in enumerate(files, 1):
            file_start = time.time()
            with open(file_path, "r", encoding="utf-8") as f:
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

if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    asyncio.run(ingest_chatprd_archive(limit))
