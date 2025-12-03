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

AVAILABLE MODULES (use these ONLY):
Browser: core.browser.launch, core.browser.goto, core.browser.click, core.browser.type, core.browser.extract, core.browser.screenshot
API: core.api.http_get, core.api.http_post
File: file.write, file.read, file.copy, file.delete
Data: data.json.parse, data.json.stringify

IMPORTANT RULES:
1. ONLY use modules from the list above
2. Reference previous step results using: ${{step_id.result}} or ${{step_id.field_name}}
3. For browser tasks, always start with core.browser.launch
4. Use browser automation (not API) for web scraping and image downloads
5. Keep workflows simple and practical

Example for image download task:
{{
  "workflow_name": "Download Images",
  "steps": [
    {{
      "step_id": "launch",
      "module": "core.browser.launch",
      "params": {{}}
    }},
    {{
      "step_id": "search",
      "module": "core.browser.goto",
      "params": {{
        "url": "https://www.google.com/search?tbm=isch&q=dogs",
        "wait_until": "networkidle"
      }}
    }},
    {{
      "step_id": "screenshot",
      "module": "core.browser.screenshot",
      "params": {{
        "path": "dog_images_search.png",
        "full_page": false
      }}
    }}
  ]
}}

IMPORTANT: For tasks involving "download images and convert to SVG" - SVG conversion is complex image vectorization. A simple workflow can:
1. Take a screenshot of image search results
2. Or download one image via HTTP
But cannot do actual SVG conversion (requires specialized tools). Keep it simple and practical.

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
        Use LLM to design intelligent module implementation

        Args:
            module_spec: Basic spec with name and reason

        Returns:
            Complete module specification for ModuleGenerator
        """
        import requests
        import os
        import re

        module_name = module_spec["name"]
        reason = module_spec.get("reason", "")

        # Try Ollama first (free)
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

        prompt = f"""Design a Python module for the Flyto2 workflow automation system.

Module name: {module_name}
Reason needed: {reason}

Please provide:
1. module_id (format: category.function_name, e.g., "string.reverse", "browser.wait")
2. category (one of: string, array, math, object, file, datetime, data, browser, utility, test)
3. description (concise, one sentence)
4. params (dict of parameter_name: type_description)
5. returns (description of return type)
6. implementation_hint (pseudo-code or description of the logic)

Respond in JSON format:
{{
  "module_id": "category.name",
  "category": "category",
  "description": "What this module does",
  "params": {{"param1": "string", "param2": "int"}},
  "returns": "Description of return value",
  "implementation_hint": "Step by step logic"
}}
"""

        try:
            response = requests.post(
                f"{ollama_url}/api/chat",
                json={
                    "model": "llama3.2",
                    "messages": [
                        {"role": "system", "content": "You are an expert Python developer. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                },
                timeout=60
            )

            if response.status_code == 200:
                content = response.json()['message']['content']

                # Extract JSON from response
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    import json
                    spec = json.loads(json_match.group())

                    # Validate required fields
                    required = ["module_id", "category", "description", "params", "returns"]
                    if all(k in spec for k in required):
                        print(f"✅ LLM designed module: {spec['module_id']}")
                        return spec

        except Exception as e:
            print(f"⚠️ Ollama failed: {e}")

        # Fallback: create basic spec
        print(f"⚠️ Using fallback basic spec for {module_name}")
        return self._create_fallback_spec(module_name, reason)

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

            connector = VectorDBConnector(mode="local")
            connector.connect()

            store = KnowledgeStore(
                connector=connector,
                collection_name="flyto2_project_knowledge",
                embedding_provider="local"
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
