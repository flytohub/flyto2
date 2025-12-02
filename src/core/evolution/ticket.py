"""
Evolution Ticket

Tracks complete evolution process from trigger to PR merge
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
import uuid


class TicketStatus(Enum):
    """Ticket lifecycle status"""
    CREATED = "created"
    PLANNING = "planning"
    DESIGNING = "designing"
    IMPLEMENTING = "implementing"
    VALIDATING = "validating"
    VALIDATION_FAILED = "validation_failed"
    PR_CREATED = "pr_created"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"
    FAILED = "failed"


@dataclass
class EvolutionTicket:
    """Represents an evolution ticket"""

    ticket_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')

    # Trigger
    trigger: str = "manual"  # "error_signature", "manual", "scheduled"
    error_signature: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    # Status
    status: TicketStatus = TicketStatus.CREATED

    # Pipeline artifacts
    plan: Optional[Dict] = None
    design: Optional[Dict] = None
    patches: Optional[Dict] = None
    validation_errors: List[str] = field(default_factory=list)

    # PR info
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    branch_name: Optional[str] = None

    # Result
    error: Optional[str] = None
    merged_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization"""
        return {
            "ticket_id": self.ticket_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "trigger": self.trigger,
            "error_signature": self.error_signature,
            "context": self.context,
            "status": self.status.value if isinstance(self.status, TicketStatus) else self.status,
            "plan": self.plan,
            "design": self.design,
            "patches": self.patches,
            "validation_errors": self.validation_errors,
            "pr_url": self.pr_url,
            "pr_number": self.pr_number,
            "branch_name": self.branch_name,
            "error": self.error,
            "merged_at": self.merged_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvolutionTicket':
        """Create ticket from dict"""
        status = data.get('status', 'created')
        if isinstance(status, str):
            status = TicketStatus(status)

        return cls(
            ticket_id=data.get('ticket_id', ''),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            trigger=data.get('trigger', 'manual'),
            error_signature=data.get('error_signature'),
            context=data.get('context', {}),
            status=status,
            plan=data.get('plan'),
            design=data.get('design'),
            patches=data.get('patches'),
            validation_errors=data.get('validation_errors', []),
            pr_url=data.get('pr_url'),
            pr_number=data.get('pr_number'),
            branch_name=data.get('branch_name'),
            error=data.get('error'),
            merged_at=data.get('merged_at')
        )
