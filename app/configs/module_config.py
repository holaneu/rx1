"""Module configuration for dynamic loading."""

from app.utils.registries import (
    WORKFLOWS_REGISTRY,
    ASSISTANTS_REGISTRY,
    PROMPTS_REGISTRY,
    TOOLS_REGISTRY,
)
from app.configs.app_config import USER_SETTINGS
from enum import Enum

class ModuleCategory(str, Enum):
    """Enumeration for module categories."""    
    APP = "app"
    USER = "user"
    USER_ADMIN = "admin"  
    USER_EXTENSIONS = "extensions"  
    USER_CUSTOM = "user_custom"  


class ModuleConfig:
    """Centralized configuration for all module paths and package definitions."""
    
    # Package type definitions
    PACKAGE_TYPES = ["workflows", "assistants", "prompts", "tools"]
    
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
             "workflows": WORKFLOWS_REGISTRY,
             "assistants": ASSISTANTS_REGISTRY,
             "prompts": PROMPTS_REGISTRY,
             "tools": TOOLS_REGISTRY
        }
        return registry_map.get(package_name)
    
    @classmethod
    def get_all_module_paths(cls) -> dict:
        """Get all module paths organized by category and package type."""
        return {
            "app": {
                pkg_type: f"app/{pkg_type}"
                for pkg_type in cls.PACKAGE_TYPES
            },
            # rename to "user_admin"
            "admin": {
                pkg_type: f"user_data/admin/custom_{pkg_type}"
                for pkg_type in cls.PACKAGE_TYPES
            },
            ModuleCategory.USER_EXTENSIONS: {
                pkg_type: f"user_data/extensions/{pkg_type}"
                for pkg_type in cls.PACKAGE_TYPES
            },
            # rename to "user"
            "user_custom": {
                pkg_type: f"user_data/{USER_SETTINGS.USER_ID}/custom_{pkg_type}"
                for pkg_type in cls.PACKAGE_TYPES
            }
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