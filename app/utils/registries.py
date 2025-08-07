"""
Registry module to break circular dependencies.
This module acts as a central store for all application registries.
"""

# Define global registries
WORKFLOWS_REGISTRY = {}
ASSISTANTS_REGISTRY = {}
PROMPTS_REGISTRY = {}
TOOLS_REGISTRY = {}
