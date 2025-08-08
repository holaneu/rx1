"""Module configuration for dynamic loading."""

from app.utils.registries import (
    WORKFLOWS_REGISTRY,
    ASSISTANTS_REGISTRY,
    PROMPTS_REGISTRY,
    TOOLS_REGISTRY,
)
from enum import Enum

class ModuleCategories(str, Enum):
    """Enumeration for module categories."""    
    APP = "app"
    USER = "user"

class PackageTypes(str, Enum):
    """Enumeration for package types."""
    WORKFLOWS = "workflows"
    ASSISTANTS = "assistants"
    PROMPTS = "prompts"
    TOOLS = "tools"
    #CONFIGS = "configs"
    #UTILS = "utils"

class ModuleConfig:
    """Centralized configuration for all module paths and package definitions."""
    
    # Package type definitions
    PACKAGE_TYPES = list(PackageTypes) #["workflows", "assistants", "prompts", "tools"]
    MODULE_CATEGORIES = list(ModuleCategories) #["app", "user"]

    def get_registry_for_package(self, package_name):
        """
        Get the registry for a specific package type. 
        
        Args:
            package_name (str): Name of the package type
            
        Returns:
            dict: The corresponding registry
        """
        # Map package names to their corresponding registries for easy lookup
        registry_map = {
             PackageTypes.WORKFLOWS.value: WORKFLOWS_REGISTRY,
             PackageTypes.ASSISTANTS.value: ASSISTANTS_REGISTRY,
             PackageTypes.PROMPTS.value: PROMPTS_REGISTRY,
             PackageTypes.TOOLS.value: TOOLS_REGISTRY
        }
        return registry_map.get(package_name)
    
    @classmethod
    def get_all_module_paths(cls) -> dict:
        """Get all module paths organized by category and package type."""
        return {
            ModuleCategories.APP.value: {
                pkg_type.value: f"app/{pkg_type.value}"
                for pkg_type in cls.PACKAGE_TYPES
            },
            ModuleCategories.USER.value: {
                pkg_type.value: f"user/{pkg_type.value}"
                for pkg_type in cls.PACKAGE_TYPES
            },
        }
    
    @classmethod
    def get_category_paths(cls, category: str) -> list:
        """Get all paths for a specific category."""
        all_paths = cls.get_all_module_paths()
        return list(all_paths.get(category, {}).values())
    
    @classmethod
    def get_package_paths(cls, package_type: str) -> list:
        """Get all paths for a specific package type across all categories."""
        all_paths = cls.get_all_module_paths()
        paths = []
        for category_paths in all_paths.values():
            if package_type in category_paths:
                paths.append(category_paths[package_type])
        return paths