import os
import glob
import asyncio
import httpx
import yaml
from typing import List, Dict, Any, Optional
from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import logger
from app.models.database import TranscriptChunkModel
from app.rag.chunker import chunk_transcript
from app.rag.embedder import generate_embeddings

# High-value sample transcripts bundled for instant offline evaluation
SAMPLE_EPISODES = [
    {
        "slug": "brian-chesky-founder-mode",
        "title": "Brian Chesky on Founder Mode, Product Design, and Scaling Airbnb",
        "guest": "Brian Chesky",
        "date": "2024-09-08",
        "url": "https://www.lennyspodcast.com/brian-chesky-founder-mode/",
        "content": """---
title: Brian Chesky on Founder Mode, Product Design, and Scaling Airbnb
guest: Brian Chesky
date: 2024-09-08
url: https://www.lennyspodcast.com/brian-chesky-founder-mode/
---

# Brian Chesky on Founder Mode, Product Design, and Scaling Airbnb

## Introduction
Lenny: Welcome to Lenny's Podcast. Today my guest is Brian Chesky, co-founder and CEO of Airbnb. Brian, welcome.
Brian Chesky: Thanks Lenny, great to be here.

## What is Founder Mode?
Lenny: Everyone in Silicon Valley is talking about "Founder Mode" after your talk at YC. What does Founder Mode actually mean in practice?
Brian Chesky: Founder Mode is the realization that the conventional advice on how to run a large company—which is hire great executives, delegate everything to them, and step back—is completely broken for founders. When you do that, you get a bureaucratic layer of professional managers who optimize for their own fiefdoms instead of the holistic product. In Founder Mode, you stay in the details. You review the work. You run the company like an orchestra where every instrument is tuned to a single coherent product vision.

## The Problem with Traditional Product Management
Lenny: You famously eliminated traditional product management at Airbnb and combined it with product marketing. Why did you make that radical change?
Brian Chesky: We had classic product managers who were essentially project coordinators writing specs and moving tickets in Jira. Nobody was obsessing over the customer experience or whether the feature was actually beautiful. We merged product management with product marketing. If you build a feature, you have to be able to explain the story to the customer. We also put designers at the center of every single product decision. We don't ship anything unless design and product are completely aligned.

## How Airbnb Plans Products: The Two Release Cycles
Lenny: Tell us about your two-release cycle per year. How does Airbnb plan its roadmap?
Brian Chesky: We stopped doing rolling, disjointed feature launches. Instead, we have two major releases a year: Summer Release and Winter Release. Every single team aligns toward these two milestones. It creates an incredible forcing function. It forces simplicity because you cannot present 50 fragmented features to users; you have to package them into 3 to 5 coherent story arcs. It builds massive external marketing momentum and internal accountability.
"""
    },
    {
        "slug": "shreyas-doshi-high-agency-pm",
        "title": "Shreyas Doshi on High Agency, Good PM vs Bad PM, and LNO Framework",
        "guest": "Shreyas Doshi",
        "date": "2023-06-15",
        "url": "https://www.lennyspodcast.com/shreyas-doshi/",
        "content": """---
title: Shreyas Doshi on High Agency, Good PM vs Bad PM, and LNO Framework
guest: Shreyas Doshi
date: 2023-06-15
url: https://www.lennyspodcast.com/shreyas-doshi/
---

# Shreyas Doshi on High Agency, Good PM vs Bad PM, and LNO Framework

## Introduction
Lenny: Welcome back to Lenny's Podcast. Today we have Shreyas Doshi, former product leader at Stripe, Twitter, Google, and Yahoo.

## The LNO Framework for Productive Work
Lenny: Shreyas, your LNO framework has transformed how thousands of product leaders manage their calendar. Walk us through it.
Shreyas Doshi: The LNO Framework categorizes all your tasks into three buckets:
- **L (Leverage tasks):** These are high-leverage tasks where exceptional quality yields massive asymmetric upside. Examples: core product strategy, PRDs for tier-1 initiatives, hiring key leaders. You should give these 100% effort and polish.
- **N (Neutral tasks):** Doing these exceptionally well does not produce exponential returns; doing them decently is good enough. Examples: routine status reports, weekly sprint planning. Aim for 80% quality.
- **O (Overhead tasks):** Mandatory administrative tasks where extra effort is wasted. Examples: expense reports, scheduling, basic email hygiene. Do them quickly at 50-60% quality or automate/delegate.
Most PMs burn out because they treat every task as Leverage (L), which leads to exhaustion and mediocre strategy.

## High Agency vs Low Agency
Lenny: You talk frequently about "High Agency". What does high agency look like in a product manager?
Shreyas Doshi: High agency is the refusal to accept that the world is fixed and that you are bound by current constraints. A low-agency PM blames external factors: "Legal didn't approve it", "Engineering has tech debt", "Marketing didn't run the campaign". A high-agency PM finds a third path when doors are closed. They understand the underlying incentives, build trust, reframe the problem, and create momentum out of thin air.
"""
    },
    {
        "slug": "elena-verna-plg-growth-loops",
        "title": "Elena Verna on Product-Led Growth, B2B Growth Loops, and Monetization",
        "guest": "Elena Verna",
        "date": "2023-11-20",
        "url": "https://www.lennyspodcast.com/elena-verna-growth/",
        "content": """---
title: Elena Verna on Product-Led Growth, B2B Growth Loops, and Monetization
guest: Elena Verna
date: 2023-11-20
url: https://www.lennyspodcast.com/elena-verna-growth/
---

# Elena Verna on Product-Led Growth, B2B Growth Loops, and Monetization

## Product-Led Growth vs Sales-Led
Lenny: Elena, you've advised Miro, Amplitude, SurveyMonkey, and Dropbox. How should founders think about PLG vs Sales-Led growth?
Elena Verna: PLG is not a replacement for sales; PLG is an acquisition and distribution engine that creates qualified demand for sales to close. If your product doesn't deliver immediate time-to-value within the first 5 minutes of sign-up, PLG will fail. The product must sell itself to the end user before the enterprise contract is signed.

## The Anatomy of a High-Converting Growth Loop
Lenny: What makes a growth loop defensible and scalable?
Elena Verna: Funnels end, but loops reinvest their output back into new inputs. The three classic loops are:
1. **Viral / Collaborative Loops:** Users invite other users to collaborate (e.g. Miro boards, Figma files).
2. **Content / SEO Loops:** User activity generates public content indexed by search engines (e.g. Canva templates, Yelp reviews).
3. **Paid Reinvestment Loops:** Customer revenue directly funds paid acquisition with positive unit economics.
"""
    },
    {
        "slug": "nikita-bier-viral-consumer-apps",
        "title": "Nikita Bier on Building #1 Viral Apps, Retention, and Growth Playbooks",
        "guest": "Nikita Bier",
        "date": "2023-04-10",
        "url": "https://www.lennyspodcast.com/nikita-bier/",
        "content": """---
title: Nikita Bier on Building #1 Viral Apps, Retention, and Growth Playbooks
guest: Nikita Bier
date: 2023-04-10
url: https://www.lennyspodcast.com/nikita-bier/
---

# Nikita Bier on Building #1 Viral Apps, Retention, and Growth Playbooks

## The Mathematics of Virality
Lenny: Nikita, you created TBH (acquired by Meta) and Gas (acquired by Discord), reaching #1 on the App Store twice. How do you engineer viral growth?
Nikita Bier: Virality is pure math and behavioral psychology. You have to optimize for K-factor:
K = (Invites sent per user) × (Conversion rate of invited users).
If K is greater than 1.0, you have exponential viral growth. To make invites high-converting, the invitation must confer social status or compliment the recipient. People don't share apps because the app is cool; they share because the app makes them look cool or feel appreciated.

## Testing Value Propositions with Smoke Tests
Lenny: Before building the full app, how do you validate whether people will care?
Nikita Bier: Never spend 6 months building an app without testing the value proposition. We create short video ads or mockup landing pages and test them with $500 in ad spend. If click-through rate and install intent is not in the top 5% of industry benchmarks, we kill the concept immediately.
"""
    }
]

import uuid
from app.models.database import TranscriptChunkModel

async def seed_sample_transcripts_if_empty(db: AsyncSession) -> int:
    """
    Seeds transcripts into PostgreSQL.
    Checks existing episode slugs and ingests any missing episodes from ChatPRD archive.
    """
    count_query = select(func.count(TranscriptChunkModel.id))
    res = await db.execute(count_query)
    current_count = res.scalar() or 0
    
    # Get existing indexed episode slugs
    existing_slugs_res = await db.execute(select(func.distinct(TranscriptChunkModel.episode_slug)))
    existing_slugs = set(existing_slugs_res.scalars().all())
    
    # Check if local transcripts_data/episodes directory exists
    repo_dirs = [
        "/transcripts_data/episodes",
        "/transcripts_data",
        settings.TRANSCRIPTS_DIR,
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "transcripts_data", "episodes"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "transcripts_data")
    ]
    
    target_data_dir = None
    for r_dir in repo_dirs:
        if os.path.exists(r_dir) and os.path.isdir(r_dir):
            files = glob.glob(os.path.join(r_dir, "**/*.md"), recursive=True)
            files = [f for f in files if not os.path.basename(f).upper().startswith("README") and not os.path.basename(f).upper().startswith("CLAUDE")]
            if files:
                target_data_dir = r_dir
                break

    # If transcripts archive does not exist locally, attempt automatic shallow clone
    if not target_data_dir:
        clone_dest = "/transcripts_data" if os.path.exists("/transcripts_data") else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "transcripts_data")
        logger.info(f"Transcripts directory not found or empty. Auto-cloning ChatPRD archive into {clone_dest}...")
        try:
            import subprocess
            temp_clone = "/tmp/transcripts_clone"
            if os.path.exists(temp_clone):
                import shutil
                shutil.rmtree(temp_clone, ignore_errors=True)
                
            subprocess.run(
                ["git", "clone", "--depth", "1", "https://github.com/ChatPRD/lennys-podcast-transcripts.git", temp_clone],
                check=True,
                capture_output=True,
                timeout=120
            )
            
            # Copy cloned content into destination
            import shutil
            os.makedirs(clone_dest, exist_ok=True)
            for item in os.listdir(temp_clone):
                s = os.path.join(temp_clone, item)
                d = os.path.join(clone_dest, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
                    
            shutil.rmtree(temp_clone, ignore_errors=True)
            target_data_dir = os.path.join(clone_dest, "episodes") if os.path.exists(os.path.join(clone_dest, "episodes")) else clone_dest
            logger.info("Transcripts archive successfully downloaded.")
        except Exception as e:
            logger.warning(f"Auto-clone skipped or encountered notice: {e}. Proceeding with bundled sample seed.")

    if target_data_dir and os.path.exists(target_data_dir):
        files = glob.glob(os.path.join(target_data_dir, "**/*.md"), recursive=True)
        files = [f for f in files if not os.path.basename(f).upper().startswith("README") and not os.path.basename(f).upper().startswith("CLAUDE")]
        if files:
            remaining_files = []
            for f in files:
                parent_dir = os.path.basename(os.path.dirname(f))
                slug = parent_dir if os.path.basename(f).startswith("transcript") else os.path.splitext(os.path.basename(f))[0]
                if slug not in existing_slugs:
                    remaining_files.append(f)
                    
            if remaining_files:
                logger.info(f"Found {len(existing_slugs)} indexed episodes. Ingesting {len(remaining_files)} episodes from {target_data_dir}...")
                return await ingest_transcripts_from_directory(db, directory_path=target_data_dir, limit=None)
            else:
                logger.info(f"Database already contains all {len(existing_slugs)} episodes ({current_count} indexed chunks).")
                return current_count

    if current_count > 0:
        logger.info(f"Database already contains {current_count} indexed chunks.")
        return current_count

    logger.info("Database is empty. Seeding bundled sample transcripts...")
    all_chunks: List[Any] = []
    
    for episode in SAMPLE_EPISODES:
        chunks = chunk_transcript(
            file_content=episode["content"],
            episode_slug=episode["slug"]
        )
        all_chunks.extend(chunks)
        
    logger.info(f"Generated {len(all_chunks)} chunks from sample episodes. Generating embeddings...")
    
    # Generate embeddings in batch
    texts_to_embed = [c.content for c in all_chunks]
    embeddings = await generate_embeddings(texts_to_embed)
    
    # Insert chunks into PostgreSQL using ORM
    for chunk, emb in zip(all_chunks, embeddings):
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
            embedding=emb
        )
        db.add(record)
        
    await db.commit()
    logger.info(f"Successfully seeded {len(all_chunks)} chunks into pgvector.")
    return len(all_chunks)

_INGESTION_PROGRESS: Dict[str, Any] = {
    "is_ingesting": False,
    "current_file": 0,
    "total_files": 0,
    "current_guest": "",
    "total_chunks": 0
}

async def ingest_transcripts_from_directory(
    db: AsyncSession,
    directory_path: str = settings.TRANSCRIPTS_DIR,
    limit: Optional[int] = None
) -> int:
    """
    Ingests all markdown transcript files from a local directory into PostgreSQL.
    """
    global _INGESTION_PROGRESS
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        
    files = glob.glob(os.path.join(directory_path, "**/*.md"), recursive=True)
    # Prioritize flagship masterclasses so quick queries are instantly available in the first minute
    priority_slugs = [
        "shreyas-doshi", "brian-chesky", "sean-ellis", "elena-verna", 
        "nikita-bier", "casey-winters", "dylan-field", "shishir-mehrotra",
        "dan-hockenmaier", "adam-fishman", "gustav-söderström"
    ]
    def get_priority_key(f: str):
        f_lower = f.lower()
        for p_idx, slug in enumerate(priority_slugs):
            if slug in f_lower:
                return (0, p_idx)
        return (1, f)
        
    files.sort(key=get_priority_key)
    
    # Filter out episodes that are already indexed into PostgreSQL
    existing_slugs_res = await db.execute(select(func.distinct(TranscriptChunkModel.episode_slug)))
    existing_slugs = set(existing_slugs_res.scalars().all())
    
    unindexed_files = []
    for f in files:
        parent_dir = os.path.basename(os.path.dirname(f))
        slug = parent_dir if os.path.basename(f).startswith("transcript") else os.path.splitext(os.path.basename(f))[0]
        if slug not in existing_slugs:
            unindexed_files.append(f)
            
    files = unindexed_files
    if not files:
        logger.info(f"✅ All {len(existing_slugs)} podcast episodes are already fully indexed in pgvector. Skipping ingestion.")
        _INGESTION_PROGRESS["is_ingesting"] = False
        return 0
    
    if limit:
        files = files[:limit]
        
    logger.info(f"Found {len(existing_slugs)} already indexed episodes. Ingesting {len(files)} remaining episodes from {directory_path}...")
    total_chunks_inserted = 0
    _INGESTION_PROGRESS["is_ingesting"] = True
    _INGESTION_PROGRESS["total_files"] = len(files)
    
    try:
        for idx, file_path in enumerate(files, start=1):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                parent_dir = os.path.basename(os.path.dirname(file_path))
                slug = parent_dir if os.path.basename(file_path).startswith("transcript") else os.path.splitext(os.path.basename(file_path))[0]
                
                chunks = chunk_transcript(content, episode_slug=slug)
                if not chunks:
                    continue
                    
                texts_to_embed = [c.content for c in chunks]
                embeddings = await generate_embeddings(texts_to_embed)
                
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
                        embedding=emb
                    )
                    db.add(record)
                    total_chunks_inserted += 1
                    
                await db.commit()
                guest_name = chunks[0].guest or slug
                _INGESTION_PROGRESS["current_file"] = idx
                _INGESTION_PROGRESS["current_guest"] = guest_name
                _INGESTION_PROGRESS["total_chunks"] = total_chunks_inserted
                
                if idx % 5 == 0 or idx == len(files):
                    logger.info(f"[{idx}/{len(files)}] Ingested {len(chunks)} chunks for {guest_name} | Total indexed: {total_chunks_inserted}")
            except Exception as err:
                logger.error(f"Error ingesting {file_path}: {err}")
                await db.rollback()
                continue
    finally:
        _INGESTION_PROGRESS["is_ingesting"] = False
            
    logger.info(f"🎉 Full ChatPRD ingestion complete: {total_chunks_inserted} chunks successfully stored in pgvector.")
    return total_chunks_inserted
