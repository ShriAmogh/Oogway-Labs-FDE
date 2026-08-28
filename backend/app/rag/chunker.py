import re
import yaml
from typing import List, Dict, Any, Optional, Tuple
import tiktoken
from app.core.config import settings
from app.core.logging import logger

tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))

def parse_transcript_markdown(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Extracts YAML frontmatter metadata and markdown body from transcript.
    """
    frontmatter = {}
    body = content
    
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if match:
        yaml_text, body = match.groups()
        try:
            frontmatter = yaml.safe_load(yaml_text) or {}
        except Exception as e:
            logger.warning(f"Error parsing frontmatter YAML: {e}")
            frontmatter = {}
            
    return frontmatter, body.strip()

class TranscriptChunk:
    def __init__(
        self,
        episode_slug: str,
        episode_title: str,
        guest: Optional[str],
        publish_date: Optional[str],
        url: Optional[str],
        chunk_index: int,
        speaker: Optional[str],
        header_section: Optional[str],
        content: str,
        token_count: int
    ):
        self.episode_slug = episode_slug
        self.episode_title = episode_title
        self.guest = guest
        self.publish_date = publish_date
        self.url = url
        self.chunk_index = chunk_index
        self.speaker = speaker
        self.header_section = header_section
        self.content = content
        self.token_count = token_count

def chunk_transcript(
    file_content: str,
    episode_slug: str,
    target_chunk_tokens: int = settings.CHUNK_SIZE_TOKENS,
    overlap_tokens: int = settings.CHUNK_OVERLAP_TOKENS
) -> List[TranscriptChunk]:
    """
    Chunks transcript using speaker-aware turns, section headers, and sliding token overlap.
    Preserves speaker metadata and header context in each chunk.
    """
    frontmatter, body = parse_transcript_markdown(file_content)
    
    episode_title = frontmatter.get("title") or frontmatter.get("episode_title") or episode_slug.replace("-", " ").title()
    guest = frontmatter.get("guest") or frontmatter.get("guests")
    if isinstance(guest, list):
        guest = ", ".join(guest)
    publish_date = str(frontmatter.get("date") or frontmatter.get("publish_date") or "")
    url = frontmatter.get("url") or frontmatter.get("youtube_url") or f"https://www.lennyspodcast.com/{episode_slug}"
    
    # Split body into sections and speaker turns
    lines = body.split("\n")
    sections: List[Dict[str, Any]] = []
    
    current_header = "Introduction"
    current_speaker = guest or "Host"
    current_turn_lines = []
    
    # Pattern to match Speaker labels: "Lenny (00:01:23):" or "**Lenny:**" or "Brian Chesky:"
    speaker_pattern = re.compile(r"^(?:\*\*)?([A-Za-z\s\.\-]{2,40})(?:\*\*)?\s*(?:\([0-9:]+\))?:\s*(.*)$")
    header_pattern = re.compile(r"^(?:#{1,4})\s+(.+)$")
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        header_match = header_pattern.match(line_clean)
        if header_match:
            if current_turn_lines:
                turn_text = "\n".join(current_turn_lines).strip()
                if turn_text:
                    sections.append({
                        "header": current_header,
                        "speaker": current_speaker,
                        "text": turn_text
                    })
                current_turn_lines = []
            current_header = header_match.group(1).strip()
            continue
            
        speaker_match = speaker_pattern.match(line_clean)
        if speaker_match:
            if current_turn_lines:
                turn_text = "\n".join(current_turn_lines).strip()
                if turn_text:
                    sections.append({
                        "header": current_header,
                        "speaker": current_speaker,
                        "text": turn_text
                    })
                current_turn_lines = []
            current_speaker = speaker_match.group(1).strip()
            content_part = speaker_match.group(2).strip()
            if content_part:
                current_turn_lines.append(f"{current_speaker}: {content_part}")
            else:
                current_turn_lines.append(f"{current_speaker}:")
        else:
            current_turn_lines.append(line_clean)
            
    if current_turn_lines:
        turn_text = "\n".join(current_turn_lines).strip()
        if turn_text:
            sections.append({
                "header": current_header,
                "speaker": current_speaker,
                "text": turn_text
            })
            
    if not sections:
        # Fallback if no structured turns found
        sections.append({
            "header": "Full Transcript",
            "speaker": guest or "Speaker",
            "text": body
        })

    # Now create overlapping chunks
    chunks: List[TranscriptChunk] = []
    current_chunk_blocks = []
    current_chunk_tokens = 0
    chunk_index = 0
    
    for section in sections:
        sec_text = f"[{section['header']}]\n{section['text']}" if section['header'] else section['text']
        sec_tokens = count_tokens(sec_text)
        
        # If a single section is larger than target_chunk_tokens, slice it with standard sliding window
        if sec_tokens > target_chunk_tokens:
            words = sec_text.split()
            chunk_size_words = 450
            overlap_words = 100
            stride = max(50, chunk_size_words - overlap_words) # 350 words
            
            for w_idx in range(0, len(words), stride):
                window = words[w_idx:w_idx + chunk_size_words]
                if not window or (w_idx > 0 and len(window) < 30):
                    continue
                sub_text = " ".join(window)
                
                header_prefix = f"### Episode: {episode_title} (Guest: {guest or 'Lenny'})\n"
                full_chunk_text = header_prefix + sub_text
                
                chunks.append(TranscriptChunk(
                    episode_slug=episode_slug,
                    episode_title=episode_title,
                    guest=guest,
                    publish_date=publish_date,
                    url=url,
                    chunk_index=chunk_index,
                    speaker=section['speaker'],
                    header_section=section['header'],
                    content=full_chunk_text,
                    token_count=count_tokens(full_chunk_text)
                ))
                chunk_index += 1
            continue
            
        if current_chunk_tokens + sec_tokens > target_chunk_tokens and current_chunk_blocks:
            # Emit current chunk
            combined_body = "\n\n".join([b['text'] for b in current_chunk_blocks])
            header_prefix = f"### Episode: {episode_title} (Guest: {guest or 'Lenny'})\n"
            full_chunk_text = header_prefix + combined_body
            
            chunks.append(TranscriptChunk(
                episode_slug=episode_slug,
                episode_title=episode_title,
                guest=guest,
                publish_date=publish_date,
                url=url,
                chunk_index=chunk_index,
                speaker=current_chunk_blocks[0]['speaker'],
                header_section=current_chunk_blocks[0]['header'],
                content=full_chunk_text,
                token_count=count_tokens(full_chunk_text)
            ))
            chunk_index += 1
            
            # Keep overlap blocks
            retained_blocks = []
            retained_tokens = 0
            for b in reversed(current_chunk_blocks):
                b_toks = count_tokens(b['text'])
                if retained_tokens + b_toks <= overlap_tokens:
                    retained_blocks.insert(0, b)
                    retained_tokens += b_toks
                else:
                    break
            current_chunk_blocks = retained_blocks
            current_chunk_tokens = retained_tokens
            
        current_chunk_blocks.append(section)
        current_chunk_tokens += sec_tokens
        
    if current_chunk_blocks:
        combined_body = "\n\n".join([b['text'] for b in current_chunk_blocks])
        header_prefix = f"### Episode: {episode_title} (Guest: {guest or 'Lenny'})\n"
        full_chunk_text = header_prefix + combined_body
        chunks.append(TranscriptChunk(
            episode_slug=episode_slug,
            episode_title=episode_title,
            guest=guest,
            publish_date=publish_date,
            url=url,
            chunk_index=chunk_index,
            speaker=current_chunk_blocks[0]['speaker'],
            header_section=current_chunk_blocks[0]['header'],
            content=full_chunk_text,
            token_count=count_tokens(full_chunk_text)
        ))
        
    return chunks
