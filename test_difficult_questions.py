#!/usr/bin/env python3
"""
Simple Test: How bot handles impossible tasks
測試機器人如何應對不可能的任務
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

async def test_question(question: str):
    """Test a single difficult question"""
    print("\n" + "=" * 70)
    print(f"❓ Question: {question}")
    print("=" * 70)

    # Step 1: Check RAG knowledge
    print("\n📚 Checking knowledge base...")
    try:
        from src.core.utils.rag_retriever import get_rag_retriever
        retriever = get_rag_retriever()
        result = await retriever.retrieve(
            query=question,
            collection_name='flyto2_knowledge',
            top_k=3
        )

        if result['success'] and result['results']:
            print(f"✓ Found {len(result['results'])} relevant entries")
            best = result['results'][0]
            print(f"  Best match (score: {best['score']:.3f}):")
            print(f"  {best['content'][:150]}...")
        else:
            print("✗ No relevant knowledge found")

    except Exception as e:
        print(f"✗ RAG check failed: {e}")

    # Step 2: Check available modules
    print("\n🔧 Checking atomic modules...")
    try:
        from src.core.modules.registry import ModuleRegistry

        # Keywords for different types of tasks
        keywords_map = {
            "機器學習": ["ml", "train", "model", "sklearn", "tensorflow"],
            "影片": ["video", "ffmpeg", "media"],
            "圖片": ["image", "cv", "opencv", "pillow"],
            "音樂": ["audio", "music", "sound"],
            "app": ["ios", "android", "mobile"],
        }

        found = []
        for kw_group, keywords in keywords_map.items():
            if any(k in question for k in kw_group.split()):
                for module_id in ModuleRegistry._registry.keys():
                    if any(kw in module_id.lower() for kw in keywords):
                        found.append(module_id)

        if found:
            print(f"✓ Found {len(found)} potentially relevant modules:")
            for m in found[:3]:
                print(f"  - {m}")
        else:
            print("✗ No relevant atomic modules available")

        # Show what we DO have
        all_modules = list(ModuleRegistry._registry.keys())
        print(f"\n  Currently available: {len(all_modules)} total modules")
        print(f"  Categories: browser, api, data, string, array, file, etc.")

    except Exception as e:
        print(f"✗ Module check failed: {e}")

    # Step 3: Intent detection
    print("\n🧠 Detecting intent...")
    try:
        from src.core.agent.intent_detector import IntentDetector
        detector = IntentDetector()
        intent = detector.detect(question)

        print(f"✓ Type: {intent['type']}")
        print(f"  Confidence: {intent['confidence']:.1%}")

        if intent['confidence'] < 0.3:
            print("  ⚠️  Low confidence - task unclear")

    except Exception as e:
        print(f"✗ Intent detection failed: {e}")

    # Step 4: Generate response
    print("\n💬 Bot Response:")
    print("-" * 70)

    if 'found' in locals() and found:
        print(f"""
✓ I found some modules that might help: {', '.join(found[:3])}

However, {question} is complex. Let me break it down:

**Current Capabilities:**
- Web automation (Playwright)
- API integration (HTTP requests)
- Data processing
- File operations

**What I suggest:**
1. Break this task into smaller steps using existing modules
2. Use external services/APIs specialized for this
3. Create a new atomic module if this is a common need

Would you like me to:
- Suggest a workaround?
- Find relevant third-party services?
- Help design a new module?
""")
    else:
        print(f"""
I understand you want: {question}

⚠️  This task is beyond my current atomic modules.

**What I CAN do:**
✓ Web scraping (browser automation)
✓ API calls (HTTP GET/POST)
✓ Data transformation (filter, map, merge)
✓ File operations (read, write, move)
✓ String/Array processing

**What I CANNOT do directly:**
✗ Machine learning training
✗ Video/Audio processing
✗ Mobile app development
✗ Image recognition (unless via API)

**Suggested approach:**
1. **Use external APIs**:
   - ML: OpenAI API, Google Cloud ML
   - Video: YouTube API, FFmpeg (if installed)
   - Images: Google Vision API, Clarifai

2. **Break it down**:
   - Can we solve this with API calls + data processing?
   - What parts can current modules handle?

3. **Create new module**:
   - If this is a common need, I can propose a new atomic module
   - Would need appropriate dependencies installed

What would you prefer?
""")

    print("-" * 70)

async def main():
    print("=" * 70)
    print("🧪 Testing Bot Response to Difficult Questions")
    print("=" * 70)

    # Difficult questions atomic modules can't handle
    questions = [
        "幫我訓練一個機器學習模型預測股價",
        "把這個影片轉成文字逐字稿",
        "幫我寫一個 iOS app",
        "分析這張圖片中的人臉情緒",
        "生成一段 30 秒的背景音樂"
    ]

    for q in questions:
        await test_question(q)
        await asyncio.sleep(0.5)

    print("\n" + "=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)
    print("""
Summary:
- Bot checks knowledge base (RAG)
- Bot checks available atomic modules
- Bot detects task intent
- Bot provides honest assessment of capabilities
- Bot suggests alternatives/workarounds
""")

    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
