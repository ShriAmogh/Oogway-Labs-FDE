import re
import uuid
from typing import Dict, Any, Optional, Tuple, List
from app.core.security import sanitize_html
from app.core.logging import logger

def parse_generated_artifacts(assistant_response: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extracts structured artifact blocks from assistant text.
    Format:
    ```artifact
    title: "Airbnb 2-Release Cycle Template"
    type: "html" | "markdown" | "svg"
    ---
    <content>
    ```
    """
    artifacts = []
    
    pattern = re.compile(r"```(?:artifact|interactive_artifact)\s*\n(.*?)\n---\s*\n(.*?)```", re.DOTALL)
    
    def replacer(match):
        meta_str = match.group(1).strip()
        body = match.group(2).strip()
        
        # Parse simple metadata lines
        title = "Artifact"
        art_type = "markdown"
        
        for line in meta_str.split("\n"):
            if line.startswith("title:"):
                title = line.replace("title:", "").strip().strip('"\'')
            elif line.startswith("type:"):
                art_type = line.replace("type:", "").strip().strip('"\'').lower()
                
        if art_type not in ["html", "markdown", "svg"]:
            art_type = "markdown"
            
        if art_type == "html":
            sanitized_body = sanitize_html(body)
        else:
            sanitized_body = body
            
        art_id = str(uuid.uuid4())
        artifacts.append({
            "id": art_id,
            "title": title,
            "artifact_type": art_type,
            "content": sanitized_body
        })
        
        return f"\n> **Artifact Generated: [{title}]** *(View in Artifact Viewer panel)*\n"

    cleaned_text = pattern.sub(replacer, assistant_response)
    return cleaned_text, artifacts
