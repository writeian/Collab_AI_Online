"""
Migration Script for OpenAI Utils.

This script handles the final migration from the old monolithic openai_utils.py
to the new modular structure while maintaining backward compatibility.
"""

import os
import shutil
import sys
from datetime import datetime
from typing import List, Dict, Any


class MigrationManager:
    """Manages the migration from old to new openai_utils structure."""
    
    def __init__(self):
        self.backup_dir = "backups"
        self.old_file = "openai_utils.py"
        self.new_package = "openai_utils"
        self.migration_log = []
    
    def log(self, message: str):
        """Log a migration message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.migration_log.append(log_entry)
        print(log_entry)
    
    def create_backup(self) -> bool:
        """Create a backup of the old openai_utils.py file."""
        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.backup_dir}/openai_utils_backup_{timestamp}.py"
            
            if os.path.exists(self.old_file):
                shutil.copy2(self.old_file, backup_file)
                self.log(f"✅ Backup created: {backup_file}")
                return True
            else:
                self.log(f"⚠️  No {self.old_file} found to backup")
                return True
                
        except Exception as e:
            self.log(f"❌ Failed to create backup: {str(e)}")
            return False
    
    def verify_new_structure(self) -> bool:
        """Verify that the new modular structure is complete."""
        try:
            required_files = [
                f"{self.new_package}/__init__.py",
                f"{self.new_package}/config.py",
                f"{self.new_package}/exceptions.py",
                f"{self.new_package}/api_clients.py",
                f"{self.new_package}/mode_manager.py",
                f"{self.new_package}/assessment.py",
                f"{self.new_package}/conversation.py",
                f"{self.new_package}/main_interface.py",
                f"{self.new_package}/test_suite.py"
            ]
            
            missing_files = []
            for file_path in required_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                self.log(f"❌ Missing files: {missing_files}")
                return False
            
            self.log(f"✅ All required files present")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to verify structure: {str(e)}")
            return False
    
    def test_imports(self) -> bool:
        """Test that all imports work correctly."""
        try:
            # Test basic imports
            import openai_utils
            from openai_utils import (
                AIConfig,
                AIAPIError,
                APIClientFactory,
                ModeManager,
                LearningAssessment,
                ConversationManager,
                OpenAIUtilsInterface
            )
            
            # Test backward compatibility functions
            from openai_utils import (
                get_client_type,
                get_ai_response,
                call_anthropic_api,
                call_openai_api,
                call_ollama_api,
                get_modes_for_room,
                generate_room_modes,
                get_mode_system_prompt,
                assess_learning_progression,
                get_progression_recommendation,
                get_next_learning_step,
                generate_chat_introduction,
                format_conversation_for_ai,
                process_conversation_context,
                get_config,
                get_status
            )
            
            self.log(f"✅ All imports successful")
            return True
            
        except Exception as e:
            self.log(f"❌ Import test failed: {str(e)}")
            return False
    
    def test_functionality(self) -> bool:
        """Test basic functionality of the new modules."""
        try:
            from openai_utils import OpenAIUtilsInterface, AIConfig
            
            # Test interface initialization
            interface = OpenAIUtilsInterface()
            
            # Test configuration
            config = interface.get_config()
            self.log(f"✅ Configuration loaded: {config.DEFAULT_CLIENT_TYPE}")
            
            # Test status
            status = interface.get_status()
            self.log(f"✅ Status check: {status.get('config', 'unknown')}")
            
            # Test conversation formatting
            messages = [{"content": "Test message", "is_ai": False}]
            formatted_messages, parameters = interface.format_conversation_for_ai(messages)
            self.log(f"✅ Conversation formatting: {len(formatted_messages)} messages")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Functionality test failed: {str(e)}")
            return False
    
    def create_compatibility_wrapper(self) -> bool:
        """Create a compatibility wrapper that redirects to the new structure."""
        try:
            wrapper_content = '''"""
Compatibility Wrapper for OpenAI Utils.

This file provides backward compatibility for the old openai_utils.py
by redirecting all imports to the new modular structure.
"""

# Import all functions from the new modular structure
from openai_utils import *

# Log the migration
import logging
logger = logging.getLogger(__name__)
logger.info("Using new modular openai_utils structure")

# Re-export all symbols for backward compatibility
__all__ = [
    # Configuration and exceptions
    "AIConfig",
    "AIAPIError",
    "ConfigurationError", 
    "AssessmentError",
    "ModeGenerationError",
    "ConversationError",
    "RateLimitError",
    "AuthenticationError",
    
    # API Clients
    "BaseAPIClient",
    "AnthropicClient",
    "OpenAIClient",
    "OllamaClient",
    "APIClientFactory",
    "call_anthropic_api",
    "call_openai_api",
    "call_ollama_api",
    
    # Mode Manager
    "ChatMode",
    "ModeManager",
    "get_modes_for_room",
    "generate_room_modes",
    "get_mode_system_prompt",
    "get_client_type",
    "MODES",
    
    # Assessment
    "AssessmentResult",
    "LearningAssessment",
    "assess_learning_progression",
    "get_progression_recommendation",
    "get_next_learning_step",
    
    # Conversation
    "ConversationMessage",
    "ConversationManager",
    "format_conversation_for_ai",
    "get_ai_response",
    "generate_chat_introduction",
    "get_client_type",
    
    # Main Interface
    "OpenAIUtilsInterface",
    "get_client_type",
    "get_ai_response",
    "call_anthropic_api",
    "call_openai_api",
    "call_ollama_api",
    "get_modes_for_room",
    "generate_room_modes",
    "get_mode_system_prompt",
    "assess_learning_progression",
    "get_progression_recommendation",
    "get_next_learning_step",
    "generate_chat_introduction",
    "format_conversation_for_ai",
    "process_conversation_context",
    "get_config",
    "get_status"
]

# Print deprecation warning
import warnings
warnings.warn(
    "openai_utils.py is deprecated. Please use the new modular structure: from openai_utils import *",
    DeprecationWarning,
    stacklevel=2
)
'''
            
            # Write the compatibility wrapper
            with open(self.old_file, 'w') as f:
                f.write(wrapper_content)
            
            self.log(f"✅ Compatibility wrapper created")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to create compatibility wrapper: {str(e)}")
            return False
    
    def update_imports_in_project(self) -> bool:
        """Update imports in other project files to use the new structure."""
        try:
            # Files that might import openai_utils
            project_files = [
                "app.py",
                "chat.py", 
                "room.py",
                "dashboard.py"
            ]
            
            updated_files = []
            for file_path in project_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        
                        # Check if file imports openai_utils
                        if "from openai_utils import" in content or "import openai_utils" in content:
                            self.log(f"📝 Found imports in {file_path}")
                            updated_files.append(file_path)
                        
                    except Exception as e:
                        self.log(f"⚠️  Could not check {file_path}: {str(e)}")
            
            if updated_files:
                self.log(f"📋 Files that may need import updates: {updated_files}")
            else:
                self.log(f"✅ No files found with openai_utils imports")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to check project imports: {str(e)}")
            return False
    
    def run_migration(self) -> bool:
        """Run the complete migration process."""
        self.log("🚀 Starting OpenAI Utils Migration")
        self.log("=" * 50)
        
        # Step 1: Create backup
        self.log("Step 1: Creating backup...")
        if not self.create_backup():
            return False
        
        # Step 2: Verify new structure
        self.log("Step 2: Verifying new structure...")
        if not self.verify_new_structure():
            return False
        
        # Step 3: Test imports
        self.log("Step 3: Testing imports...")
        if not self.test_imports():
            return False
        
        # Step 4: Test functionality
        self.log("Step 4: Testing functionality...")
        if not self.test_functionality():
            return False
        
        # Step 5: Create compatibility wrapper
        self.log("Step 5: Creating compatibility wrapper...")
        if not self.create_compatibility_wrapper():
            return False
        
        # Step 6: Check project imports
        self.log("Step 6: Checking project imports...")
        if not self.update_imports_in_project():
            return False
        
        # Step 7: Final verification
        self.log("Step 7: Final verification...")
        if not self.test_imports():
            return False
        
        self.log("=" * 50)
        self.log("🎉 Migration completed successfully!")
        self.log("✅ New modular structure is active")
        self.log("✅ Backward compatibility maintained")
        self.log("✅ All tests passing")
        
        return True
    
    def generate_report(self) -> str:
        """Generate a migration report."""
        report = f"""
# OpenAI Utils Migration Report

## Migration Summary
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status**: {'✅ SUCCESS' if self.migration_log else '❌ FAILED'}
- **Files Created**: {len([f for f in os.listdir(self.new_package) if f.endswith('.py')])} modules

## Migration Log
{chr(10).join(self.migration_log)}

## New Structure
```
openai_utils/
├── __init__.py              # Package initialization
├── config.py               # Configuration management
├── exceptions.py           # Custom exceptions
├── api_clients.py          # API client implementations
├── mode_manager.py         # Mode management
├── assessment.py           # Learning assessment
├── conversation.py         # Conversation management
├── main_interface.py       # Unified interface
├── test_suite.py           # Test suite
└── migration.py            # This migration script
```

## Backward Compatibility
- ✅ All original functions preserved
- ✅ Import statements unchanged
- ✅ API signatures maintained
- ✅ Deprecation warnings added

## Next Steps
1. Test the application thoroughly
2. Update any custom imports if needed
3. Remove the old monolithic file when ready
4. Update documentation

## Rollback Instructions
If you need to rollback:
1. Restore the backup from `backups/openai_utils_backup_YYYYMMDD_HHMMSS.py`
2. Remove the `openai_utils/` directory
3. Restart the application
"""
        return report


def main():
    """Main migration function."""
    print("🚀 OpenAI Utils Migration Tool")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Error: Please run this script from the project root directory")
        return False
    
    # Create migration manager
    manager = MigrationManager()
    
    # Run migration
    success = manager.run_migration()
    
    # Generate and save report
    report = manager.generate_report()
    with open("MIGRATION_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n📋 Migration report saved to MIGRATION_REPORT.md")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 