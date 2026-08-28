import asyncio
import os
import sys
import json
import httpx

async def test_platform_growth_ship30():
    url = "http://localhost:8000/api/v1/chat/stream"
    payload = {
        "message": "/30for30 What are the core strategies for platform growth and marketplace liquidity?",
        "model_provider": "gemini",
        "enable_ship30": True
    }
    
    print("=" * 75)
    print("  🚀 TESTING SHIP 30 FOR 30 SKILL: PLATFORM GROWTH QUERY")
    print("=" * 75)
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    events_received = []
    artifacts = []
    citations = []
    tokens = []
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", url, json=payload) as response:
            assert response.status_code == 200, f"Error status: {response.status_code}"
            
            current_event = None
            async for line in response.aiter_lines():
                if line.startswith("event:"):
                    current_event = line.replace("event:", "").strip()
                elif line.startswith("data:"):
                    raw_data = line.replace("data:", "").strip()
                    try:
                        data = json.loads(raw_data)
                        events_received.append((current_event, data))
                        
                        if current_event == "artifact":
                            artifacts.append(data)
                            print(f"\n✨ [ARTIFACT GENERATED]: {data.get('title')} ({data.get('type')})")
                        elif current_event == "citation":
                            citations.append(data)
                            print(f"📚 [CITATION]: {data.get('guest')} — {data.get('episode_title')}")
                        elif current_event == "token":
                            tokens.append(data.get("delta", ""))
                        elif current_event == "thinking":
                            print(f"🧠 [THINKING STAGE]: {data.get('stage')} — {data.get('message')}")
                    except Exception:
                        pass

    print("\n" + "=" * 75)
    print("  📊 VERIFICATION SUMMARY")
    print("=" * 75)
    print(f"  • Total Events Received: {len(events_received)}")
    print(f"  • Citations Gathered:    {len(citations)}")
    print(f"  • Artifacts Created:     {len(artifacts)}")
    print(f"  • Full Response Length:  {len(''.join(tokens))} chars")
    
    if artifacts:
        print("\n📝 Artifact Preview (Ship 30 for 30 Essay):")
        print("-" * 60)
        print(artifacts[0].get("content", "")[:600] + "...\n")
        print("-" * 60)
        print("✅ SUCCESS: Ship 30 for 30 skill successfully produced an interactive atomic essay artifact!")
    else:
        print("⚠️ No artifact was created.")

if __name__ == "__main__":
    asyncio.run(test_platform_growth_ship30())
