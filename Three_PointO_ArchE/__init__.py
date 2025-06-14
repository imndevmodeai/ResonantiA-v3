"""
ResonantiA Protocol v3.0 - Core Package
"""

__version__ = "3.0.0"
__author__ = "ResonantiA Development Team"
__description__ = "Core implementation of the ResonantiA Protocol v3.0"

from .workflow_engine import IARCompliantWorkflowEngine
from .action_context import ActionContext

__all__ = ['IARCompliantWorkflowEngine', 'ActionContext'] 