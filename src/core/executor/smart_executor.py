"""
Smart Executor - Self-Healing Task Execution

When given a natural language task:
1. Generate workflow
2. Execute
3. If error -> analyze -> generate solution -> retry
4. Report results
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class SmartExecutor:
    """
    Smart executor that learns from failures and auto-generates solutions
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.max_retries = 3
        self.execution_log = []

    async def execute_task(self, task_description: str, notify_callback=None) -> Dict[str, Any]:
        """
        Execute a task described in natural language

        Args:
            task_description: Natural language task (e.g., "crawl amazon.com")
            notify_callback: Async callback for progress updates

        Returns:
            Execution result
        """
        result = {
            "task": task_description,
            "timestamp": datetime.now().isoformat(),
            "status": "running",
            "attempts": [],
            "final_result": None,
            "generated_modules": []
        }

        await self._notify(notify_callback, f"🎯 Task: {task_description}")

        for attempt in range(1, self.max_retries + 1):
            await self._notify(notify_callback, f"\n🔄 Attempt {attempt}/{self.max_retries}")

            attempt_result = {
                "attempt_number": attempt,
                "steps": [],
                "error": None,
                "workflow_generated": False
            }

            workflow = None  # Initialize to avoid UnboundLocalError

            try:
                # Step 1: Generate workflow from task description
                await self._notify(notify_callback, "📝 Generating workflow...")
                workflow = await self._generate_workflow(task_description)
                attempt_result["steps"].append({"step": "generate_workflow", "status": "success"})
                attempt_result["workflow_generated"] = True

                # Step 2: Execute workflow
                await self._notify(notify_callback, "▶️ Executing workflow...")
                exec_result = await self._execute_workflow(workflow)
                attempt_result["steps"].append({"step": "execute_workflow", "status": "success", "result": exec_result})

                # Success!
                result["status"] = "success"
                result["final_result"] = exec_result
                result["attempts"].append(attempt_result)

                await self._notify(notify_callback, f"\n✅ Task completed successfully!")
                await self._notify(notify_callback, f"\n📊 Results:\n{self._format_result(exec_result)}")

                return result

            except Exception as e:
                error_msg = str(e)

                # Record which step failed
                if not attempt_result["workflow_generated"]:
                    attempt_result["steps"].append({"step": "generate_workflow", "status": "error", "error": error_msg})
                else:
                    attempt_result["steps"].append({"step": "execute_workflow", "status": "error", "error": error_msg})

                attempt_result["error"] = error_msg
                result["attempts"].append(attempt_result)

                await self._notify(notify_callback, f"❌ Error: {error_msg}")

                if attempt < self.max_retries:
                    # Step 3: Analyze error and prepare solution
                    await self._notify(notify_callback, "\n🔍 Analyzing error...")
                    analysis = await self._analyze_error(error_msg, task_description, workflow)

                    if analysis.get("missing_modules"):
                        await self._notify(notify_callback, f"📦 Missing modules detected: {len(analysis['missing_modules'])}")

                        # Step 4: Generate missing modules
                        for module_spec in analysis["missing_modules"]:
                            await self._notify(notify_callback, f"⚙️ Generating module: {module_spec['name']}")
                            module = await self._generate_module(module_spec)
                            result["generated_modules"].append(module)
                            await self._notify(notify_callback, f"✅ Module generated: {module_spec['name']}")

                        await self._notify(notify_callback, "\n🔄 Retrying with new modules...")

                    elif analysis.get("recommendations"):
                        await self._notify(notify_callback, f"💡 Suggestions: {', '.join(analysis['recommendations'][:2])}")

                        # Try to fix the task description
                        if analysis.get("improved_task"):
                            task_description = analysis["improved_task"]
                            await self._notify(notify_callback, f"🔄 Retrying with improved understanding...")
                        else:
                            await self._notify(notify_callback, "\n⚠️ Will retry with same parameters...")
                    else:
                        await self._notify(notify_callback, "\n⚠️ No automatic solution found")
                        break

        # Max retries reached
        result["status"] = "failed"
        await self._notify(notify_callback, f"\n❌ Task failed after {self.max_retries} attempts")

        return result

    async def _query_knowledge_base(self, query: str) -> Dict[str, Any]:
        """Query vector database for available modules and knowledge"""
        try:
            from src.core.modules.atomic.vector import VectorDBConnector, KnowledgeStore, KnowledgeSearch

            connector = VectorDBConnector(mode="local")
            connector.connect()

            # Create KnowledgeStore first
            store = KnowledgeStore(
                connector=connector,
                collection_name="flyto2_project_knowledge",
                embedding_provider="local"
            )

            # Then create KnowledgeSearch with the store
            search = KnowledgeSearch(knowledge_store=store)

            # Search for relevant modules and workflows
            results = search.search_with_score_threshold(query, min_score=0.5, top_k=5)

            connector.disconnect()

            # Extract module information
            available_modules = []
            for result in results:
                content = result.get('content', '')
                if 'module' in content.lower():
                    available_modules.append(content)

            return {
                "available_modules": available_modules,
                "knowledge": results
            }

        except Exception as e:
            print(f"⚠️ Knowledge base query error: {e}")
            import traceback
            traceback.print_exc()
            return {"available_modules": [], "knowledge": []}

    async def _generate_workflow(self, task_description: str) -> Dict[str, Any]:
        """Generate workflow from natural language description with RAG"""
        # Step 1: Query knowledge base for available modules
        kb_query = f"browser crawling modules workflow {task_description}"
        knowledge = await self._query_knowledge_base(kb_query)

        task_lower = task_description.lower()

        if "crawl" in task_lower or "scrape" in task_lower:
            # Extract URL with multiple strategies
            import re

            # Strategy 1: Standard URL with protocol
            urls = re.findall(r'https?://[^\s]+', task_description)

            # Strategy 2: www. domains
            if not urls:
                www_matches = re.findall(r'www\.[^\s]+', task_description, re.IGNORECASE)
                if www_matches:
                    urls = [f"https://{match}" for match in www_matches]

            # Strategy 3: Domain-like patterns (amazon.com, google.com, etc.)
            if not urls:
                domain_matches = re.findall(r'\b([a-z0-9-]+\.)+[a-z]{2,}\b', task_description, re.IGNORECASE)
                if domain_matches:
                    # Take the first match and add https://
                    urls = [f"https://{domain_matches[0]}"]

            if not urls:
                raise ValueError("No URL found in task description. Please include a URL like 'https://example.com' or 'amazon.com'")

            url = urls[0]

            # Generate crawler workflow
            workflow = {
                "workflow_name": f"crawl_{url}",
                "steps": [
                    {
                        "step_id": "launch_browser",
                        "module": "browser.launch",
                        "params": {"headless": True}
                    },
                    {
                        "step_id": "goto_page",
                        "module": "browser.goto",
                        "params": {
                            "url": url,
                            "wait_until": "networkidle"
                        }
                    },
                    {
                        "step_id": "extract_page",
                        "module": "browser.extract",
                        "params": {
                            "fields": [
                                {"name": "title", "selector": "title"},
                                {"name": "headings", "selector": "h1, h2, h3", "multiple": True},
                                {"name": "links", "selector": "a", "attribute": "href", "multiple": True}
                            ]
                        }
                    },
                    {
                        "step_id": "close_browser",
                        "module": "browser.close",
                        "params": {}
                    }
                ],
                "outputs": {
                    "result": {
                        "source": "extract_page.result"
                    }
                }
            }

            return workflow

        elif "search" in task_lower:
            # Search workflow - treat as crawl with search query
            import re

            # Strategy 1: Standard URL with protocol
            urls = re.findall(r'https?://[^\s]+', task_description)

            # Strategy 2: www. domains
            if not urls:
                www_matches = re.findall(r'www\.[^\s]+', task_description, re.IGNORECASE)
                if www_matches:
                    urls = [f"https://{match}" for match in www_matches]

            # Strategy 3: Domain-like patterns
            if not urls:
                domain_matches = re.findall(r'\b([a-z0-9-]+\.)+[a-z]{2,}\b', task_description, re.IGNORECASE)
                if domain_matches:
                    urls = [f"https://{domain_matches[0]}"]

            if not urls:
                raise ValueError("No URL found in task description. Please specify where to search (e.g., 'search amazon.com for laptops')")

            url = urls[0]

            # Extract search query
            query_match = re.search(r'search for (.+)', task_lower)
            search_query = query_match.group(1) if query_match else ""

            # Generate search workflow
            workflow = {
                "workflow_name": f"search_{url}",
                "steps": [
                    {
                        "step_id": "launch_browser",
                        "module": "browser.launch",
                        "params": {"headless": True}
                    },
                    {
                        "step_id": "goto_page",
                        "module": "browser.goto",
                        "params": {
                            "url": url,
                            "wait_until": "networkidle"
                        }
                    },
                    {
                        "step_id": "search_input",
                        "module": "browser.type",
                        "params": {
                            "selector": "input[type='search'], input[name='q'], input[name='k']",
                            "text": search_query
                        }
                    },
                    {
                        "step_id": "submit_search",
                        "module": "browser.click",
                        "params": {
                            "selector": "button[type='submit'], input[type='submit']"
                        }
                    },
                    {
                        "step_id": "wait_results",
                        "module": "browser.wait",
                        "params": {"timeout": 5000}
                    },
                    {
                        "step_id": "extract_results",
                        "module": "browser.extract",
                        "params": {
                            "fields": [
                                {"name": "products", "selector": "[data-component-type='s-search-result']", "multiple": True},
                                {"name": "titles", "selector": "h2 a span", "multiple": True},
                                {"name": "prices", "selector": ".a-price-whole", "multiple": True}
                            ]
                        }
                    },
                    {
                        "step_id": "close_browser",
                        "module": "browser.close",
                        "params": {}
                    }
                ],
                "outputs": {
                    "result": {
                        "source": "extract_results.result"
                    }
                }
            }

            return workflow

        else:
            raise ValueError(f"Unable to understand task: {task_description}")

    async def _execute_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow using WorkflowEngine"""
        from src.core.engine.workflow_engine import WorkflowEngine

        engine = WorkflowEngine(workflow)
        result = await engine.execute()

        if result.get("status") == "error":
            raise Exception(result.get("error", "Unknown error"))

        return result

    async def _analyze_error(self, error_msg: str, task_description: str, workflow: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze error and suggest solutions

        Args:
            error_msg: The error message
            task_description: Original task description
            workflow: Generated workflow (may be None if generation failed)

        Returns:
            Analysis with missing_modules, recommendations, and improved_task
        """
        analysis = {
            "error": error_msg,
            "missing_modules": [],
            "recommendations": [],
            "improved_task": None
        }

        # Pattern matching for common errors
        error_lower = error_msg.lower()

        # 1. Module errors
        if "module not found" in error_lower or "no module" in error_lower:
            import re
            match = re.search(r"module[:\s]+['\"]?([a-z._]+)['\"]?", error_lower)
            if match:
                module_name = match.group(1)
                analysis["missing_modules"].append({
                    "name": module_name,
                    "reason": "Module not found in registry"
                })

        # 2. URL detection errors
        if "no url found" in error_lower:
            # Try to extract URL from task description more aggressively
            import re

            # Try different URL patterns
            url_patterns = [
                r'https?://[^\s]+',  # Standard URL
                r'www\.[^\s]+',  # www without protocol
                r'([a-z0-9-]+\.)+[a-z]{2,}',  # Domain without protocol
            ]

            for pattern in url_patterns:
                urls = re.findall(pattern, task_description, re.IGNORECASE)
                if urls:
                    # Found a URL-like string, suggest adding protocol
                    url = urls[0]
                    if not url.startswith('http'):
                        url = f"https://{url}"

                    # Improve task description
                    analysis["improved_task"] = f"crawl {url}"
                    analysis["recommendations"].append(f"Added missing URL: {url}")
                    break

            if not analysis["improved_task"]:
                analysis["recommendations"].append("Please provide a valid URL (e.g., https://example.com)")

        # 3. Selector/element errors
        if "selector" in error_lower or "element not found" in error_lower:
            analysis["recommendations"].append("Add more robust element detection")
            analysis["recommendations"].append("Try alternative selectors")

        # 4. Timeout errors
        if "timeout" in error_lower:
            analysis["recommendations"].append("Increase timeout or add retry logic")

        # 5. Workflow generation errors
        if workflow is None and "unable to understand" in error_lower:
            # Try to infer intent from task description
            task_lower = task_description.lower()

            if any(word in task_lower for word in ['爬', '抓', 'crawl', 'scrape', 'fetch']):
                analysis["recommendations"].append("Task detected as: web crawling")
                analysis["recommendations"].append("Please include a URL in your request")
            elif any(word in task_lower for word in ['搜', '找', 'search', 'find']):
                analysis["recommendations"].append("Task detected as: search")
                analysis["recommendations"].append("Please specify where to search (e.g., 'search amazon.com for laptops')")
            else:
                analysis["recommendations"].append("Unable to understand task type")
                analysis["recommendations"].append("Try: /crawl <url> or natural language with clear URL")

        return analysis

    async def _generate_module(self, module_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate missing module"""
        # For now, just log
        # In real implementation, use AI to generate module code

        module_info = {
            "name": module_spec["name"],
            "status": "generated",
            "path": f"src/core/modules/atomic/{module_spec['name'].replace('.', '/')}.py"
        }

        return module_info

    def _format_result(self, result: Dict[str, Any]) -> str:
        """Format result for display"""
        if not result:
            return "No result"

        # Extract meaningful data
        output = []

        if "outputs" in result:
            outputs = result["outputs"]
            if "result" in outputs:
                data = outputs["result"]

                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            output.append(f"{key}: {len(value)} items")
                        else:
                            output.append(f"{key}: {value}")
                else:
                    output.append(str(data))

        return "\n".join(output) if output else json.dumps(result, indent=2)[:500]

    async def _notify(self, callback, message: str):
        """Send notification via callback"""
        if callback:
            await callback(message)
