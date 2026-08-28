import asyncio
import os
import sys
import uuid

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from sqlalchemy import delete, text
from app.core.database import AsyncSessionLocal
from app.models.database import TranscriptChunkModel
from app.agents.tools.rag_search_tool import execute_rag_search
from app.agents.gemini_agent import GeminiAgent
from app.rag.chunker import chunk_transcript
from app.rag.embedder import get_local_embedder

async def verify_elena():
    print("=" * 80)
    print("🧪 END-TO-END VERIFICATION: 'Elena Verna B2B Growth Loops and PLG'")
    print("=" * 80)

    # 1. Update Elena Verna chunks in database with fixed chunker
    elena_file = "transcripts_data/episodes/elena-verna/transcript.md"
    with open(elena_file, "r", encoding="utf-8") as f:
        content = f.read()
    chunks = chunk_transcript(content, "elena-verna")
    print(f"📦 Generated {len(chunks)} rich chunks for Elena Verna.")

    embedder = get_local_embedder()
    texts_to_embed = [c.content for c in chunks]
    embeddings = embedder.encode(texts_to_embed, batch_size=64, normalize_embeddings=True)

    async with AsyncSessionLocal() as db:
        # Delete old fragmented chunks for elena-verna
        await db.execute(delete(TranscriptChunkModel).where(TranscriptChunkModel.episode_slug == "elena-verna"))
        await db.commit()

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
        print("💾 Stored clean, dense Elena Verna chunks into PostgreSQL.")

        # 2. Run Retrieval
        query = "Elena Verna B2B Growth Loops and PLG"
        print(f"\n🔍 Searching for: '{query}'...")
        context_str, citations = await execute_rag_search(db, query, top_k=5)

        print(f"\n📊 Retrieved {len(citations)} citations:")
        for idx, cit in enumerate(citations, 1):
            print(f"   [{idx}] Guest: {cit['guest']} | Title: {cit['episode_title'][:40]}... (Score: {cit['relevance_score']})")
            print(f"       Quote: {cit['quote'][:150]}...\n")

        # 3. Stream Synthesis
        print("🤖 Synthesizing response with Gemini...")
        agent = GeminiAgent(db)
        collected_tokens = []
        async for event in agent.chat_stream(
            messages=[],
            query=query,
            session_id="test-session-elena-fixed",
            enable_ship30=False
        ):
            if event.event == "token":
                delta = event.data.get("delta", "")
                collected_tokens.append(delta)
                print(delta, end="", flush=True)

        full_text = "".join(collected_tokens)
        refusal_found = "I don't have sufficient evidence" in full_text
        print("\n\n" + "=" * 80)
        print("✅ VERIFICATION RESULTS:")
        print(f"   • Total Response Length: {len(full_text)} characters")
        print(f"   • Refusal Triggered: {'YES (FAIL)' if refusal_found else 'NO (PASS)'}")
        print(f"   • Citations Count: {len(citations)}")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(verify_elena())
