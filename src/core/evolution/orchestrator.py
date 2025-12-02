"""
Evolution Orchestrator

Complete evolution pipeline:
1. ErrorCenter triggers ticket
2. Planner analyzes with RAG + Module Catalog
3. Designer creates solution plan (JSON)
4. Implementation generates patches
5. Validator checks patches
6. PR Engine creates pull request
7. Human reviews and merges
8. Webhook updates VectorDB
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .ticket import EvolutionTicket, TicketStatus
from .auto_evolution_engine import EvolutionPlanner, EvolutionDesigner, ImplementationAgent
from .reporter import get_error_center
from src.core.ai.llm_orchestrator import get_llm_orchestrator

logger = logging.getLogger(__name__)


class EvolutionOrchestrator:
    """Orchestrate complete evolution process"""

    def __init__(self):
        self.tickets_dir = Path("metrics/evolution_tickets")
        self.tickets_dir.mkdir(parents=True, exist_ok=True)

        self.history_file = Path("metrics/evolution_history.jsonl")

        self.planner = EvolutionPlanner()
        self.designer = EvolutionDesigner()
        self.implementation = ImplementationAgent()
        self.llm_orchestrator = get_llm_orchestrator()
        self.error_center = get_error_center()

    async def trigger_from_error_signature(
        self,
        error_signature: str
    ) -> EvolutionTicket:
        """
        Trigger evolution from error signature

        Args:
            error_signature: Error signature from ErrorCenter

        Returns:
            Evolution ticket
        """
        logger.info(f"Triggering evolution for error signature: {error_signature}")

        # Get errors with this signature
        errors = self.error_center.get_errors_by_signature(error_signature)

        if not errors:
            raise ValueError(f"No errors found with signature: {error_signature}")

        # Create ticket
        ticket = EvolutionTicket(
            trigger="error_signature",
            error_signature=error_signature,
            context={
                "error_count": len(errors),
                "first_error": errors[0] if errors else None,
                "recent_errors": errors[:5]
            }
        )

        self._save_ticket(ticket)

        # Run evolution pipeline
        try:
            await self._run_pipeline(ticket)
        except Exception as e:
            logger.error(f"Evolution pipeline failed: {e}")
            ticket.status = TicketStatus.FAILED
            ticket.error = str(e)
            self._save_ticket(ticket)
            raise

        return ticket

    async def trigger_manual(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> EvolutionTicket:
        """
        Manually trigger evolution

        Args:
            description: Description of what to evolve
            context: Additional context

        Returns:
            Evolution ticket
        """
        logger.info(f"Manual evolution trigger: {description}")

        ticket = EvolutionTicket(
            trigger="manual",
            context={
                "description": description,
                **(context or {})
            }
        )

        self._save_ticket(ticket)

        try:
            await self._run_pipeline(ticket)
        except Exception as e:
            logger.error(f"Evolution pipeline failed: {e}")
            ticket.status = TicketStatus.FAILED
            ticket.error = str(e)
            self._save_ticket(ticket)
            raise

        return ticket

    async def _run_pipeline(self, ticket: EvolutionTicket):
        """Run complete evolution pipeline"""

        # Step 1: Planning
        logger.info(f"[{ticket.ticket_id}] Step 1: Planning")
        ticket.status = TicketStatus.PLANNING
        self._save_ticket(ticket)

        try:
            # Convert ticket to dict for planner
            plan = await self.planner.analyze_and_plan(ticket.to_dict())
            ticket.plan = plan
            self._save_ticket(ticket)
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            ticket.plan = {"error": str(e), "status": "failed"}
            self._save_ticket(ticket)
            raise

        # Step 2: Design
        logger.info(f"[{ticket.ticket_id}] Step 2: Designing")
        ticket.status = TicketStatus.DESIGNING
        self._save_ticket(ticket)

        try:
            design = await self.designer.design_implementation(plan)
            ticket.design = design
            self._save_ticket(ticket)
        except Exception as e:
            logger.error(f"Design failed: {e}")
            ticket.design = {"error": str(e), "status": "failed"}
            self._save_ticket(ticket)
            raise

        # Step 3: Implementation
        logger.info(f"[{ticket.ticket_id}] Step 3: Implementing")
        ticket.status = TicketStatus.IMPLEMENTING
        self._save_ticket(ticket)

        try:
            patches = await self.implementation.implement_design(design)
            ticket.patches = patches
            self._save_ticket(ticket)
        except Exception as e:
            logger.error(f"Implementation failed: {e}")
            ticket.patches = {"error": str(e), "status": "failed"}
            self._save_ticket(ticket)
            raise

        # Step 4: Validation
        logger.info(f"[{ticket.ticket_id}] Step 4: Validating")
        ticket.status = TicketStatus.VALIDATING
        self._save_ticket(ticket)

        validation_result = await self._validate_patches(patches)

        if not validation_result["success"]:
            logger.warning(f"Validation failed: {validation_result['errors']}")
            ticket.status = TicketStatus.VALIDATION_FAILED
            ticket.validation_errors = validation_result["errors"]
            self._save_ticket(ticket)
            return

        # Step 5: Create PR (placeholder - will implement in PR Engine section)
        logger.info(f"[{ticket.ticket_id}] Step 5: PR Creation (placeholder)")
        ticket.status = TicketStatus.PR_CREATED
        # pr_url = await self._create_pr(ticket)
        # ticket.pr_url = pr_url
        self._save_ticket(ticket)

        # Log to history
        self._log_to_history(ticket)

        logger.info(f"[{ticket.ticket_id}] Evolution pipeline complete")

    async def _validate_patches(self, patches: Dict) -> Dict[str, Any]:
        """
        Validate generated patches

        Args:
            patches: Generated patches to validate

        Returns:
            Validation result with success status and errors
        """
        # Placeholder - will use PatchValidator when implemented
        # For now, basic validation

        if not patches:
            return {
                "success": False,
                "errors": ["No patches generated"]
            }

        if isinstance(patches, dict) and patches.get("error"):
            return {
                "success": False,
                "errors": [patches["error"]]
            }

        # Check if patches have required structure
        if isinstance(patches, dict) and "files" in patches:
            return {
                "success": True,
                "errors": []
            }

        return {
            "success": True,
            "errors": []
        }

    def _save_ticket(self, ticket: EvolutionTicket):
        """Save ticket to file"""
        ticket.updated_at = datetime.utcnow().isoformat() + 'Z'

        ticket_file = self.tickets_dir / f"ticket_{ticket.ticket_id}.json"

        with open(ticket_file, 'w', encoding='utf-8') as f:
            json.dump(ticket.to_dict(), f, indent=2, ensure_ascii=False)

    def _log_to_history(self, ticket: EvolutionTicket):
        """Log ticket to evolution history"""
        history_entry = {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "ticket_id": ticket.ticket_id,
            "trigger": ticket.trigger,
            "status": ticket.status.value if isinstance(ticket.status, TicketStatus) else ticket.status,
            "error_signature": ticket.error_signature
        }

        with open(self.history_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(history_entry) + '\n')

    def get_ticket(self, ticket_id: str) -> Optional[EvolutionTicket]:
        """Load ticket by ID"""
        ticket_file = self.tickets_dir / f"ticket_{ticket_id}.json"

        if not ticket_file.exists():
            return None

        with open(ticket_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return EvolutionTicket.from_dict(data)

    def list_tickets(
        self,
        status: Optional[TicketStatus] = None,
        limit: int = 20
    ) -> list:
        """List tickets with optional status filter"""
        tickets = []

        for ticket_file in sorted(self.tickets_dir.glob("ticket_*.json"), reverse=True):
            try:
                with open(ticket_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ticket = EvolutionTicket.from_dict(data)

                    if status and ticket.status != status:
                        continue

                    tickets.append(ticket)

                    if len(tickets) >= limit:
                        break
            except Exception as e:
                logger.warning(f"Failed to load ticket {ticket_file}: {e}")
                continue

        return tickets


# Singleton
_orchestrator = None


def get_evolution_orchestrator() -> EvolutionOrchestrator:
    """Get singleton orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = EvolutionOrchestrator()
    return _orchestrator


# CLI for testing
if __name__ == "__main__":
    import sys

    async def test_orchestrator():
        """Test evolution orchestrator"""
        print("Testing Evolution Orchestrator...")

        orchestrator = get_evolution_orchestrator()

        # Test manual trigger
        try:
            ticket = await orchestrator.trigger_manual(
                description="Test evolution: Add error handling to module X",
                context={"module": "test_module", "priority": "low"}
            )

            print(f"\n✅ Evolution ticket created: {ticket.ticket_id}")
            print(f"Status: {ticket.status.value}")
            print(f"Ticket saved to: metrics/evolution_tickets/ticket_{ticket.ticket_id}.json")

            if ticket.plan:
                print(f"\nPlan generated: {len(str(ticket.plan))} chars")
            if ticket.design:
                print(f"Design generated: {len(str(ticket.design))} chars")
            if ticket.patches:
                print(f"Patches generated: {len(str(ticket.patches))} chars")

        except Exception as e:
            print(f"\n⚠️ Test failed (expected - requires full setup): {e}")
            print("This is normal if RAG/LLM services are not configured")

    # Run test
    asyncio.run(test_orchestrator())
