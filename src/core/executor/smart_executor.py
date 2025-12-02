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
                "steps": []
            }

            try:
                # Step 1: Generate workflow from task description
                await self._notify(notify_callback, "📝 Generating workflow...")
                workflow = await self._generate_workflow(task_description)
                attempt_result["steps"].append({"step": "generate_workflow", "status": "success"})

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
                attempt_result["steps"].append({"step": "execute_workflow", "status": "error", "error": error_msg})
                result["attempts"].append(attempt_result)

                await self._notify(notify_callback, f"❌ Error: {error_msg}")

                if attempt < self.max_retries:
                    # Step 3: Analyze error and generate solution
                    await self._notify(notify_callback, "\n🔍 Analyzing error...")
                    analysis = await self._analyze_error(error_msg, workflow)

                    if analysis.get("missing_modules"):
                        await self._notify(notify_callback, f"📦 Missing modules detected: {len(analysis['missing_modules'])}")

                        # Step 4: Generate missing modules
                        for module_spec in analysis["missing_modules"]:
                            await self._notify(notify_callback, f"⚙️ Generating module: {module_spec['name']}")
                            module = await self._generate_module(module_spec)
                            result["generated_modules"].append(module)
                            await self._notify(notify_callback, f"✅ Module generated: {module_spec['name']}")

                        await self._notify(notify_callback, "\n🔄 Retrying with new modules...")
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
            from src.core.modules.atomic.vector import VectorDBConnector, KnowledgeSearch

            connector = VectorDBConnector(mode="local")
            connector.connect()

            search = KnowledgeSearch(
                connector=connector,
                collection_name="flyto2_project_knowledge",
                embedding_provider="local"
            )

            # Search for relevant modules and workflows
            results = search.search(query, top_k=5)

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
            print(f"Knowledge base query error: {e}")
            return {"available_modules": [], "knowledge": []}

    async def _generate_workflow(self, task_description: str) -> Dict[str, Any]:
        """Generate workflow from natural language description with RAG"""
        # Step 1: Query knowledge base for available modules
        kb_query = f"browser crawling modules workflow {task_description}"
        knowledge = await self._query_knowledge_base(kb_query)

        task_lower = task_description.lower()

        if "crawl" in task_lower or "scrape" in task_lower:
            # Extract URL
            import re
            urls = re.findall(r'https?://[^\s]+', task_description)

            if not urls:
                raise ValueError("No URL found in task description")

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
            # Search workflow
            raise NotImplementedError("Search workflow not yet implemented")

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

    async def _analyze_error(self, error_msg: str, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze error and suggest solutions"""
        analysis = {
            "error": error_msg,
            "missing_modules": [],
            "recommendations": []
        }

        # Pattern matching for common errors
        error_lower = error_msg.lower()

        if "module not found" in error_lower or "no module" in error_lower:
            # Extract module name
            import re
            match = re.search(r"module[:\s]+['\"]?([a-z._]+)['\"]?", error_lower)
            if match:
                module_name = match.group(1)
                analysis["missing_modules"].append({
                    "name": module_name,
                    "reason": "Module not found in registry"
                })

        if "selector" in error_lower or "element not found" in error_lower:
            analysis["recommendations"].append("Add more robust element detection")

        if "timeout" in error_lower:
            analysis["recommendations"].append("Increase timeout or add retry logic")

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
