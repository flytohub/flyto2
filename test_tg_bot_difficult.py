#!/usr/bin/env python3
"""
Test TG Bot with Difficult Questions
測試機器人如何應對原子組件做不到的難題
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from src.core.agent.task_orchestrator import TaskOrchestrator
from src.core.utils.rag_retriever import get_rag_retriever

async def test_difficult_question(question: str):
    """Test bot response to difficult question"""
    print("=" * 70)
    print(f"🤔 Difficult Question: {question}")
    print("=" * 70)

    # Initialize orchestrator
    orchestrator = TaskOrchestrator()

    # Step 1: Check if RAG can help
    print("\n📚 Step 1: Checking knowledge base...")
    retriever = get_rag_retriever()
    rag_result = await retriever.retrieve(
        query=question,
        collection_name='flyto2_knowledge',
        top_k=3
    )

    if rag_result['success'] and rag_result['results']:
        print(f"   Found {len(rag_result['results'])} relevant knowledge entries:")
        for i, r in enumerate(rag_result['results'][:2], 1):
            print(f"   {i}. Score: {r['score']:.3f}")
            print(f"      {r['content'][:100]}...")
    else:
        print("   No relevant knowledge found")

    # Step 2: Try to understand the task
    print("\n🧠 Step 2: Understanding task intent...")
    from src.core.agent.intent_detector import IntentDetector
    detector = IntentDetector()
    intent = detector.detect(question)

    print(f"   Type: {intent['type']}")
    print(f"   Confidence: {intent['confidence']:.1%}")
    if intent.get('task_type'):
        print(f"   Task Type: {intent['task_type']}")

    # Step 3: Check available modules
    print("\n🔧 Step 3: Checking available atomic modules...")
    from src.core.modules.registry import ModuleRegistry

    # Search for relevant modules
    keywords = ["video", "audio", "ml", "ai", "model", "train"]
    found_modules = []

    for module_id, module_class in ModuleRegistry._registry.items():
        module_name = module_class.module_name.lower() if hasattr(module_class, 'module_name') else ''
        if any(kw in module_id.lower() or kw in module_name for kw in keywords):
            found_modules.append(module_id)

    if found_modules:
        print(f"   Found {len(found_modules)} potentially relevant modules:")
        for mod in found_modules[:5]:
            print(f"   - {mod}")
    else:
        print("   ⚠️  No relevant atomic modules found for this task")

    # Step 4: Bot's response strategy
    print("\n💡 Step 4: Bot Response Strategy:")

    if intent['confidence'] < 0.3:
        print("   Strategy: ASK_FOR_CLARIFICATION")
        response = f"""
I'm not entirely sure what you're asking for. Could you clarify?

Based on what I understand, you might be asking about: {question}

Current available capabilities:
- Web scraping (browser automation)
- API integration (HTTP requests)
- Data processing (transform, filter, merge)
- File operations (read, write, move)

If you need something beyond these, I can:
1. Help break down your request into smaller tasks
2. Suggest alternative approaches using existing modules
3. Create a new atomic module if it's a common pattern

What would you like to do?
"""
    elif not found_modules:
        print("   Strategy: SUGGEST_ALTERNATIVES")
        response = f"""
I understand you want: {question}

However, I don't currently have atomic modules that can directly handle this task.

🛠️ **What I can offer:**

1. **Break it down**: We could split this into smaller tasks using existing modules
   - Browser automation (Playwright)
   - API calls (HTTP requests)
   - Data processing

2. **Create new module**: If this is a common need, I can propose adding a new atomic module

3. **External integration**: Use third-party APIs/services that specialize in this

Would you like me to:
- Suggest a workaround using current modules?
- Design a new atomic module for this?
- Find relevant external services/APIs?
"""
    else:
        print("   Strategy: ATTEMPT_WITH_AVAILABLE_MODULES")
        response = f"""
I found {len(found_modules)} potentially relevant modules:

{chr(10).join(f"- {m}" for m in found_modules[:5])}

Let me try to create a workflow using these modules.

⚠️  Note: This might not be exactly what you need, but it's a starting point.

Would you like me to proceed with generating a workflow?
"""

    print("\n" + "=" * 70)
    print("🤖 Bot Response:")
    print("=" * 70)
    print(response)

    return {
        'question': question,
        'intent': intent,
        'rag_results': len(rag_result['results']) if rag_result['success'] else 0,
        'found_modules': len(found_modules),
        'strategy': 'CLARIFY' if intent['confidence'] < 0.3 else ('SUGGEST_ALT' if not found_modules else 'ATTEMPT')
    }

async def main():
    print("\n" + "=" * 70)
    print("🧪 Testing TG Bot with Difficult Questions")
    print("=" * 70)

    # Test cases: Questions that atomic modules can't handle
    difficult_questions = [
        "幫我訓練一個機器學習模型預測股價",
        "把這個影片轉成文字逐字稿",
        "幫我寫一個 iOS app",
        "分析這張圖片中的人臉情緒",
        "生成一段 30 秒的背景音樂",
    ]

    results = []

    for i, question in enumerate(difficult_questions, 1):
        print(f"\n\n{'='*70}")
        print(f"Test {i}/{len(difficult_questions)}")
        print(f"{'='*70}")

        result = await test_difficult_question(question)
        results.append(result)

        await asyncio.sleep(1)  # Pause between tests

    # Summary
    print("\n\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)

    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r['question']}")
        print(f"   Intent confidence: {r['intent']['confidence']:.1%}")
        print(f"   RAG results: {r['rag_results']}")
        print(f"   Found modules: {r['found_modules']}")
        print(f"   Strategy: {r['strategy']}")

    print("\n" + "=" * 70)
    print("✅ Testing Complete!")
    print("=" * 70)

    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
