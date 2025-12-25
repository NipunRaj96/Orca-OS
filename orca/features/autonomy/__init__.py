"""
Advanced autonomy features for Orca OS.
Self-healing and failure learning systems.
"""

from .self_healing import AggressiveSelfHealing
from .failure_learning import FailureLearningSystem

__all__ = ['AggressiveSelfHealing', 'FailureLearningSystem']

