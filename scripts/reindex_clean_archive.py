import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.rag.ingest import ingest_transcripts_from_directory
from app.core.config import settings

async def reindex_clean():
    print("=" * 70)
    print("🧹 PURGING OLD 1-WORD CORRUPTED CHUNKS & RE-INDEXING CLEAN ARCHIVE")
    print("=" * 70)
    
    start = time.time()
    async with AsyncSessionLocal() as db:
        # Delete old chunks
        print("1. Deleting old fragmented chunks...")
        await db.execute(text("TRUNCATE TABLE transcript_chunks RESTART IDENTITY;"))
        await db.commit()
        print("   ✅ Old chunks cleared.")

        # Re-index clean chunks with fixed stride
        print("2. Indexing clean archive with fixed 450-word stride...")
        transcripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "transcripts_data", "episodes")
        if not os.path.exists(transcripts_dir):
            transcripts_dir = "/transcripts_data/episodes"
            
        total_chunks = await ingest_transcripts_from_directory(db, directory_path=transcripts_dir)
        print(f"   ✅ Clean indexing complete! Total Chunks: {total_chunks} in {time.time() - start:.1f}s")

if __name__ == "__main__":
    asyncio.run(reindex_clean())
