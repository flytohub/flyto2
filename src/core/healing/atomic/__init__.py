"""
Healing Atomic Modules - Atomic components for AI error handling

Each module handles ONE specific concern:
- vector_query: Query vector DB for similar solutions
- prompt_builder: Build AI prompts with context
- ai_consulter: Consult LLM for solutions
- solution_executor: Execute AI-provided solutions
- similarity_trainer: Train similarity matching
- solution_archiver: Archive successful solutions
"""

from .vector_query import VectorQueryModule
from .prompt_builder import PromptBuilderModule
from .ai_consulter import AIConsulterModule
from .solution_executor import SolutionExecutorModule
from .similarity_trainer import SimilarityTrainerModule
from .solution_archiver import SolutionArchiverModule

__all__ = [
    'VectorQueryModule',
    'PromptBuilderModule',
    'AIConsulterModule',
    'SolutionExecutorModule',
    'SimilarityTrainerModule',
    'SolutionArchiverModule'
]
