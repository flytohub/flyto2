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

                # Debug: Print workflow modules
                if workflow and "steps" in workflow:
                    print(f"\n📋 Workflow steps:")
                    for step in workflow["steps"]:
                        print(f"  - {step.get('id', '?')}: {step.get('module', '?')}")

                # Step 1.5: Check for missing modules BEFORE execution
                missing_modules = self._check_missing_modules(workflow)
                if missing_modules:
                    await self._notify(notify_callback, f"🔍 Detected {len(missing_modules)} missing module(s)")
                    for module in missing_modules:
                        await self._notify(notify_callback, f"  - {module['name']}")

                    # Trigger module generation
                    for module_info in missing_modules:
                        await self._notify(notify_callback, f"\n🤖 Generating module: {module_info['name']}")
                        gen_result = await self._generate_module(module_info)

                        if gen_result.get("status") == "success":
                            result["generated_modules"].append(gen_result)
                            await self._notify(notify_callback, f"✅ Module generated successfully!")
                        else:
                            raise Exception(f"Failed to generate module {module_info['name']}: {gen_result.get('error')}")

                # Step 2: Execute workflow
                await self._notify(notify_callback, "▶️ Executing workflow...")
                exec_result = await self._execute_workflow(workflow)

                # Clean exec_result for JSON serialization (remove non-serializable objects)
                clean_result = self._clean_result_for_json(exec_result)
                attempt_result["steps"].append({"step": "execute_workflow", "status": "success", "result": clean_result})

                # Success!
                result["status"] = "success"
                result["final_result"] = clean_result
                result["attempts"].append(attempt_result)

                await self._notify(notify_callback, f"\n✅ Task completed successfully!")
                await self._notify(notify_callback, f"\n📊 Results:\n{self._format_result(clean_result)}")

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
                    # USE AI ERROR SOLVER
                    await self._notify(notify_callback, "\n🤖 Consulting AI for solution...")

                    from src.core.healing.ai_error_solver import AIErrorSolver

                    solver = AIErrorSolver(project_root=self.project_root)

                    error_context = {
                        "operation": "workflow_generation" if not attempt_result["workflow_generated"] else "workflow_execution",
                        "task_description": task_description,
                        "attempt": attempt,
                        "workflow": workflow if workflow else None
                    }

                    solution_result = await solver.solve_error(
                        Exception(error_msg),
                        error_context,
                        notify_callback
                    )

                    if solution_result.get("success"):
                        await self._notify(notify_callback, "✅ AI solved it, retrying...")
                        continue

                    # Fallback: Step 3: Analyze error and prepare solution
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

            connector = VectorDBConnector()
            connector.connect()

            # Create KnowledgeStore first
            store = KnowledgeStore(
                connector=connector,
                collection_name="flyto2_project_knowledge",
                embedding_provider="openai"
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
            # Use OpenAI to generate workflow for any other task
            print(f"🤖 Using OpenAI to generate workflow for: {task_description}")
            try:
                from openai import OpenAI
                import os
                from src.core.modules.registry import ModuleRegistry

                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                # Get available modules
                available_modules = list(ModuleRegistry.list_all().keys())
                modules_list = ", ".join(sorted(available_modules)[:30])  # First 30 for brevity

                prompt = f"""Generate a workflow to: {task_description}

AVAILABLE MODULES (commonly used):
Browser: core.browser.launch, core.browser.goto, core.browser.click, core.browser.type, core.browser.extract, core.browser.screenshot
API: core.api.http_get, core.api.http_post
File: file.write, file.read, file.copy, file.delete
Data: data.json.parse, data.json.stringify
Image: image.compress, image.convert, image.resize

IMPORTANT RULES FOR AUTO-EVOLUTION:
1. You CAN use modules that don't exist yet! If you need functionality not in the list, define the module name you need.
2. Use descriptive module names like: image.svg_convert, image.download, pdf.extract, etc.
3. The system will AUTO-GENERATE any missing modules for you!
4. Reference previous step results using: ${{step_id.result}} or ${{step_id.field_name}}
5. For browser tasks, always start with core.browser.launch
6. Design workflows that FULLY solve the task, even if it requires new modules

Example for image conversion task:
{{
  "workflow_name": "Download and Convert Image",
  "steps": [
    {{
      "step_id": "download",
      "module": "image.download",
      "params": {{
        "query": "dog",
        "count": 1
      }}
    }},
    {{
      "step_id": "convert",
      "module": "image.svg_convert",
      "params": {{
        "input_path": "${{download.image_path}}",
        "output_path": "dog.svg"
      }}
    }}
  ]
}}

CRITICAL: Design the BEST workflow to fully solve the task. If you need a module that doesn't exist (like image.svg_convert), USE IT ANYWAY - the system will generate it!

Now generate the workflow for: {task_description}
Return ONLY valid JSON, no markdown or explanations."""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )

                workflow_text = response.choices[0].message.content.strip()

                # Extract JSON from markdown code blocks if present
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', workflow_text, re.DOTALL)
                if json_match:
                    workflow_text = json_match.group(1)

                workflow = json.loads(workflow_text)
                print(f"✅ Generated workflow with {len(workflow.get('steps', []))} steps")
                return workflow

            except Exception as e:
                print(f"❌ OpenAI workflow generation failed: {e}")
                raise ValueError(f"Unable to generate workflow: {str(e)}")

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

        # PROACTIVE: Scan workflow for unregistered modules
        if workflow and isinstance(workflow, dict) and "steps" in workflow:
            from src.core.modules.registry import ModuleRegistry

            for step in workflow["steps"]:
                if "module" in step:
                    module_name = step["module"]

                    # Check if module is registered
                    if not ModuleRegistry.has(module_name):
                        # Module is NOT registered - needs to be generated
                        analysis["missing_modules"].append({
                            "name": module_name,
                            "reason": f"Module '{module_name}' used in workflow but not registered",
                            "step_id": step.get("id", "unknown")
                        })

        # Pattern matching for common errors
        error_lower = error_msg.lower()

        # 1. Module errors
        if "module not found" in error_lower or "no module" in error_lower:
            import re
            match = re.search(r"module[:\s]+['\"]?([a-z._]+)['\"]?", error_lower)
            if match:
                module_name = match.group(1)
                # Only add if not already found by workflow scan
                if not any(m["name"] == module_name for m in analysis["missing_modules"]):
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

            if any(word in task_lower for word in ['crawl', 'scrape', 'fetch']):
                analysis["recommendations"].append("Task detected as: web crawling")
                analysis["recommendations"].append("Please include a URL in your request")
            elif any(word in task_lower for word in ['search', 'find']):
                analysis["recommendations"].append("Task detected as: search")
                analysis["recommendations"].append("Please specify where to search (e.g., 'search amazon.com for laptops')")
            else:
                analysis["recommendations"].append("Unable to understand task type")
                analysis["recommendations"].append("Try: /crawl <url> or natural language with clear URL")

        return analysis

    def _check_missing_modules(self, workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check workflow for unregistered modules BEFORE execution

        Returns:
            List of missing module info dicts
        """
        missing = []

        if not workflow or not isinstance(workflow, dict) or "steps" not in workflow:
            return missing

        from src.core.modules.registry import ModuleRegistry

        for step in workflow["steps"]:
            if "module" in step:
                module_name = step["module"]

                # Check if module is registered
                if not ModuleRegistry.has(module_name):
                    missing.append({
                        "name": module_name,
                        "reason": f"Module '{module_name}' used in workflow but not registered",
                        "step_id": step.get("id", "unknown")
                    })

        return missing

    async def _generate_module(self, module_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate missing module using AI

        Steps:
        1. Use LLM to generate intelligent implementation
        2. Use ModuleGenerator to create files
        3. Test the generated module
        4. If successful, commit and create PR
        5. Store solution to vector DB
        """
        from src.core.meta.module_generator import ModuleGenerator
        import os

        module_name = module_spec["name"]

        try:
            # Step 1: Use LLM to design the module
            print(f"🤖 Designing module: {module_name}")
            spec = await self._design_module_with_llm(module_spec)

            if not spec:
                return {
                    "name": module_name,
                    "status": "failed",
                    "error": "Failed to design module with LLM"
                }

            # Step 2: Generate module files
            print(f"📝 Generating files for: {module_name}")
            generator = ModuleGenerator(self.project_root)
            result = generator.generate_module(spec)

            if not result["success"]:
                return {
                    "name": module_name,
                    "status": "failed",
                    "errors": result["errors"]
                }

            # Step 3: Test the generated module
            print(f"🧪 Testing module: {module_name}")
            test_result = await self._test_generated_module(result["test_path"])

            if not test_result["success"]:
                return {
                    "name": module_name,
                    "status": "generated_but_test_failed",
                    "module_path": result["module_path"],
                    "test_path": result["test_path"],
                    "test_error": test_result.get("error")
                }

            # Step 4: Create branch and PR
            print(f"🌿 Creating branch and PR for: {module_name}")
            pr_result = await self._create_module_pr(module_name, result, test_result)

            # Step 5: Store solution to vector DB
            print(f"💾 Storing solution to vector DB: {module_name}")
            await self._store_solution_to_vector_db(module_spec, spec, result, test_result)

            return {
                "name": module_name,
                "status": "success",
                "module_path": result["module_path"],
                "test_path": result["test_path"],
                "pr_branch": pr_result.get("branch"),
                "pr_url": pr_result.get("pr_url")
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "name": module_name,
                "status": "error",
                "error": str(e)
            }

    def _clean_result_for_json(self, result: Any) -> Any:
        """
        Clean result to make it JSON serializable
        Removes non-serializable objects like BrowserDriver
        """
        if result is None:
            return None

        if isinstance(result, (str, int, float, bool)):
            return result

        if isinstance(result, dict):
            cleaned = {}
            for key, value in result.items():
                # Skip browser driver and other non-serializable objects
                if key == "browser" or hasattr(value, '__class__') and 'Driver' in value.__class__.__name__:
                    continue
                cleaned[key] = self._clean_result_for_json(value)
            return cleaned

        if isinstance(result, (list, tuple)):
            return [self._clean_result_for_json(item) for item in result]

        # For other objects, try to convert to string
        try:
            json.dumps(result)
            return result
        except (TypeError, ValueError):
            return str(result)

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

    async def _design_module_with_llm(self, module_spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Use OpenAI GPT-4o to design high-quality module implementation

        Args:
            module_spec: Basic spec with name and reason

        Returns:
            Complete module specification for ModuleGenerator with implementation code
        """
        import os
        import json
        from openai import OpenAI

        module_name = module_spec["name"]
        reason = module_spec.get("reason", "")

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            print(f"❌ No OPENAI_API_KEY found")
            return self._create_fallback_spec(module_name, reason)

        print(f"🤖 Using GPT-4o to generate high-quality module: {module_name}")

        # Retry up to 3 times if validation fails
        for attempt in range(3):
            if attempt > 0:
                print(f"🔄 Retry #{attempt + 1} for {module_name}")

            spec = await self._try_design_module_with_gpt4o(module_name, reason)
            if spec:  # Validation passed
                return spec

        print(f"❌ Failed after 3 attempts, using fallback")
        return self._create_fallback_spec(module_name, reason)

    async def _try_design_module_with_gpt4o(self, module_name: str, reason: str) -> Optional[Dict[str, Any]]:
        """Single attempt to design module with GPT-4o"""
        from openai import OpenAI
        import os
        import json

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return None

        prompt = f"""You are a SENIOR Python developer creating PRODUCTION-READY code for the Flyto2 automation system.

Task: Create module '{module_name}'
Reason: {reason}

CRITICAL REQUIREMENTS:
1. implementation_code must contain ACTUAL WORKING PYTHON CODE
2. NO placeholders like "# TODO", "# Implementation here", or generic descriptions
3. NO nested function definitions (no 'def' or 'async def' inside implementation_code)
4. NO text descriptions - ONLY executable Python code
5. Use proper async/await syntax
6. Include all necessary error handling
7. MUST return UNIFIED format: {{"ok": bool, "output": dict, "error": None/dict, "meta": dict}}

❌ WRONG - Nested function definition (THIS WILL BE REJECTED):
```python
async def execute():  # ❌ NO! This is a nested function definition
    result = await do_something()
    return {{"status": "success"}}
```

✅ CORRECT - Direct implementation code (NO nested function):
```python
import httpx
from pathlib import Path

async with httpx.AsyncClient() as client:
    response = await client.get(self.url, timeout=30.0)
    response.raise_for_status()

    path = Path(self.save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)

    return {{
        "ok": True,
        "output": {{
            "path": str(path),
            "size": len(response.content),
            "url": self.url
        }},
        "error": None,
        "meta": {{}}
    }}
```

EXAMPLES OF WHAT TO GENERATE:

Good example for image.download:
```python
import httpx
from pathlib import Path

async with httpx.AsyncClient() as client:
    response = await client.get(self.url, timeout=30.0)
    response.raise_for_status()

    path = Path(self.save_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_bytes(response.content)

    return {{
        "ok": True,
        "output": {{
            "path": str(path),
            "size": len(response.content),
            "url": self.url
        }},
        "error": None,
        "meta": {{}}
    }}
```

Good example for file.read:
```python
from pathlib import Path

path = Path(self.file_path)
if not path.exists():
    raise FileNotFoundError(f"File not found: {{self.file_path}}")

content = path.read_text(encoding='utf-8')

return {{
    "ok": True,
    "output": {{
        "content": content,
        "size": len(content)
    }},
    "error": None,
    "meta": {{}}
}}
```

Return JSON specification:
{{
  "module_id": "{module_name}",
  "category": "image|file|string|array|utility|data|browser|api|ai",
  "description": "One clear sentence",
  "params": {{
    "param_name": "type - description"
  }},
  "returns": "Dict structure description",
  "suggested_imports": ["import httpx", "from pathlib import Path"],
  "implementation_code": "COMPLETE EXECUTABLE PYTHON CODE - NO PLACEHOLDERS OR NESTED FUNCTIONS"
}}

VALIDATION RULES:
- implementation_code must NOT contain: "TODO", "placeholder", "implement", nested "def/async def"
- implementation_code MUST contain: actual library calls, error handling, return statement
- Code must be indented correctly for method body (will be indented by 12 spaces)
- Must use self.param_name to access validated parameters

Generate PRODUCTION-READY code NOW."""

        try:
            client = OpenAI(api_key=openai_api_key)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a senior Python developer. Generate COMPLETE working code with NO nested functions (no 'def' or 'async def' inside implementation_code), NO placeholders, NO TODOs. The implementation_code field must contain ONLY the method body code that will be directly placed inside an execute() method. Do NOT write the entire execute() function definition - only the code that goes INSIDE it."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Lower for consistency
                timeout=60
            )

            spec = json.loads(response.choices[0].message.content)

            # Validate required fields
            required = ["module_id", "category", "description", "params", "returns"]
            if not all(k in spec for k in required):
                print(f"⚠️ GPT-4o response missing required fields")
                return None  # Return None to trigger retry

            # Validate implementation_code quality
            impl_code = spec.get("implementation_code", "")
            if not impl_code or len(impl_code.strip()) < 50:
                print(f"❌ implementation_code too short or missing")
                return None  # Return None to trigger retry

            # Check for bad patterns
            bad_patterns = ["TODO", "placeholder", "implement here", "Complete working", "nested def"]
            impl_lower = impl_code.lower()
            for pattern in bad_patterns:
                if pattern.lower() in impl_lower:
                    print(f"❌ Found bad pattern in code: {pattern}")
                    return None  # Return None to trigger retry

            # Check for nested function definitions
            if "async def " in impl_code or "\ndef " in impl_code or "\n    def " in impl_code:
                print(f"❌ Found nested function definition in implementation_code")
                return None  # Return None to trigger retry

            # Check for return statement
            if "return " not in impl_code:
                print(f"❌ No return statement in implementation_code")
                return None  # Return None to trigger retry

            print(f"✅ GPT-4o designed high-quality module: {spec['module_id']}")
            return spec

        except Exception as e:
            print(f"❌ GPT-4o failed: {e}")
            return None  # Return None to trigger retry

    def _create_fallback_spec(self, module_name: str, reason: str) -> Dict[str, Any]:
        """Create a basic spec when LLM fails"""
        # Try to parse module_name as category.function
        parts = module_name.split(".")
        if len(parts) >= 2:
            category = parts[0]
            func_name = parts[1]
        else:
            category = "utility"
            func_name = module_name.replace(".", "_")

        return {
            "module_id": f"{category}.{func_name}",
            "category": category,
            "description": f"Auto-generated module: {reason}",
            "params": {"input": "any"},
            "returns": "Processing result",
            "implementation_hint": "Basic implementation placeholder"
        }

    async def _test_generated_module(self, test_path: str) -> Dict[str, Any]:
        """
        Test the generated module

        Args:
            test_path: Path to the test YAML file

        Returns:
            Test result
        """
        import subprocess
        from pathlib import Path

        test_file = Path(test_path)

        if not test_file.exists():
            return {
                "success": False,
                "error": f"Test file not found: {test_path}"
            }

        try:
            # Run the test using workflow engine
            result = subprocess.run(
                ["python", "-m", "src.cli.main", str(test_file)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout + result.stderr

            # Check for success indicators
            success = (
                result.returncode == 0 and
                "error" not in output.lower() and
                ("success" in output.lower() or "✅" in output)
            )

            return {
                "success": success,
                "output": output[:500],
                "returncode": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Test timeout (30s)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _create_module_pr(self, module_name: str, gen_result: Dict[str, Any], test_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create branch, commit, push, and PR for generated module

        Args:
            module_name: Module name
            gen_result: Generation result
            test_result: Test result

        Returns:
            PR creation result
        """
        import subprocess
        from datetime import datetime

        branch_name = f"auto-gen-{module_name.replace('.', '-')}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        try:
            # Check if there are changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if not result.stdout.strip():
                return {
                    "success": False,
                    "message": "No changes to commit"
                }

            # Create branch
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )

            # Stage files
            subprocess.run(
                ["git", "add", gen_result["module_path"], gen_result["test_path"]],
                cwd=self.project_root,
                check=True
            )

            # Commit
            commit_msg = f"""feat: Auto-generate {module_name} module

Generated by SmartExecutor AI Agent

- Module: {gen_result['module_path']}
- Test: {gen_result['test_path']}
- Test result: {'✅ PASS' if test_result['success'] else '❌ FAIL'}

🤖 Generated with AI-powered self-healing system
"""

            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.project_root,
                check=True,
                capture_output=True
            )

            # Push
            push_result = subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if push_result.returncode != 0:
                return {
                    "success": False,
                    "branch": branch_name,
                    "error": "Push failed",
                    "message": "Branch created locally, push manually to create PR"
                }

            # Create PR using gh CLI
            pr_title = f"feat: Auto-generate {module_name} module"
            pr_body = f"""## AI-Generated Module

**Module**: `{module_name}`
**Reason**: Missing module detected during task execution

### Files
- Module: `{gen_result['module_path']}`
- Test: `{gen_result['test_path']}`

### Test Results
{'✅ All tests passed' if test_result['success'] else '⚠️ Tests need review'}

### Generated By
SmartExecutor AI Agent - Self-healing task execution system

---
🤖 This PR was automatically generated by the AI evolution system.
"""

            pr_result = subprocess.run(
                ["gh", "pr", "create", "--title", pr_title, "--body", pr_body],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if pr_result.returncode == 0:
                # Extract PR URL from output
                pr_url = pr_result.stdout.strip().split('\n')[-1]

                return {
                    "success": True,
                    "branch": branch_name,
                    "pr_url": pr_url,
                    "message": "PR created successfully"
                }
            else:
                return {
                    "success": False,
                    "branch": branch_name,
                    "error": pr_result.stderr,
                    "message": "Branch pushed, but PR creation failed (use gh CLI manually)"
                }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "branch": branch_name,
                "error": str(e),
                "message": "Git operation failed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _store_solution_to_vector_db(
        self,
        module_spec: Dict[str, Any],
        designed_spec: Dict[str, Any],
        gen_result: Dict[str, Any],
        test_result: Dict[str, Any]
    ):
        """
        Store successful solution to vector database (in English)

        Args:
            module_spec: Original module spec
            designed_spec: LLM-designed spec
            gen_result: Generation result
            test_result: Test result
        """
        try:
            from src.core.modules.atomic.vector import VectorDBConnector, KnowledgeStore
            from src.core.utils.translator import translate_to_english
            from datetime import datetime

            print("🌐 Translating to English for vector DB...")

            # Translate content to English
            problem_en = await translate_to_english(
                module_spec.get('reason', 'Module not found'),
                context="error"
            )
            description_en = await translate_to_english(
                designed_spec['description'],
                context="solution"
            )
            implementation_en = await translate_to_english(
                designed_spec.get('implementation_hint', 'N/A'),
                context="code"
            )

            connector = VectorDBConnector()
            connector.connect()

            store = KnowledgeStore(
                connector=connector,
                collection_name="flyto2_project_knowledge",
                embedding_provider="openai"
            )

            # Create comprehensive knowledge entry (ALL IN ENGLISH)
            content = f"""
Module Generation Solution

Problem: {problem_en}
Module: {designed_spec['module_id']}
Category: {designed_spec['category']}
Description: {description_en}

Parameters:
{self._format_params(designed_spec['params'])}

Implementation Approach:
{implementation_en}

Test Result: {'PASS' if test_result['success'] else 'FAIL'}

Files Generated:
- Module: {gen_result['module_path']}
- Test: {gen_result['test_path']}

This solution was automatically generated and tested by the SmartExecutor AI Agent.
""".strip()

            store.add_entry(
                content=content,
                metadata={
                    "source": "smart_executor_auto_generation",
                    "category": "module_generation_solution",
                    "module_id": designed_spec['module_id'],
                    "module_category": designed_spec['category'],
                    "test_passed": test_result['success'],
                    "original_problem": module_spec.get('reason', ''),  # Keep original
                    "timestamp": datetime.now().isoformat()
                }
            )

            connector.disconnect()
            print(f"✅ Solution stored to vector DB (English): {designed_spec['module_id']}")

        except Exception as e:
            print(f"⚠️ Failed to store solution to vector DB: {e}")

    def _format_params(self, params: Dict[str, str]) -> str:
        """Format parameters for documentation"""
        lines = []
        for name, type_desc in params.items():
            lines.append(f"  - {name}: {type_desc}")
        return "\n".join(lines) if lines else "  (none)"
