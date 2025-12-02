"""
Evolution system - Autonomous self-improvement
"""

from .reporter import (
    EvolutionReporter,
    ErrorCenter,
    DebugEngine,
    get_reporter,
    get_error_center,
    get_debug_engine
)
from .ticket import EvolutionTicket, TicketStatus
from .orchestrator import EvolutionOrchestrator, get_evolution_orchestrator
from .auto_evolution_engine import (
    EvolutionPlanner,
    EvolutionDesigner,
    ImplementationAgent
)

__all__ = [
    'EvolutionReporter',
    'ErrorCenter',
    'DebugEngine',
    'get_reporter',
    'get_error_center',
    'get_debug_engine',
    'EvolutionTicket',
    'TicketStatus',
    'EvolutionOrchestrator',
    'get_evolution_orchestrator',
    'EvolutionPlanner',
    'EvolutionDesigner',
    'ImplementationAgent',
]
