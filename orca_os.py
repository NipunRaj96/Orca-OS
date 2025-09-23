#!/usr/bin/env python3
"""
Orca OS - AI-Powered Operating System
A natural language interface for your computer that anyone can use.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from orca.core.models import UserQuery, SystemContext
from orca.llm.manager import LLMManager
from orca.core.context import ContextProvider
from orca.security.validator import CommandValidator
from orca.security.policy import PolicyEngine
from orca.utils.config import load_config
from orca.core.executor import CommandExecutor


class OrcaOS:
    """The main Orca OS interface - simple and user-friendly."""
    
    def __init__(self):
        """Initialize Orca OS."""
        self.config = load_config("config/orca.yaml")
        self.llm_manager = LLMManager(self.config.llm.model_dump())
        self.context_provider = ContextProvider()
        self.validator = CommandValidator(self.config.policy)
        self.policy_engine = PolicyEngine(self.config.policy.model_dump())
        self.executor = CommandExecutor(self.config.executor.model_dump())
    
    async def process_request(self, user_input: str) -> str:
        """Process a natural language request and return the result."""
        try:
            print(f"🤖 Orca: Understanding your request...")
            
            # Create user query
            query = UserQuery(query=user_input)
            
            # Get system context
            context = await self.context_provider.get_context()
            
            # Generate AI suggestion
            suggestion = await self.llm_manager.generate_suggestion(query, context)
            
            # Validate the suggestion
            validated = self.validator.validate(suggestion)
            
            # Apply policy
            final_suggestion = self.policy_engine.validate(validated)
            
            # Execute if safe
            if final_suggestion.action.value == "execute":
                print(f"✅ Executing: {final_suggestion.command}")
                result = await self.executor.execute(final_suggestion)
                
                if result.success:
                    return f"✅ Done! {final_suggestion.explanation}\n\nOutput:\n{result.stdout}"
                else:
                    return f"❌ Error: {result.stderr}"
            
            elif final_suggestion.action.value == "dry_run":
                return f"🔍 Here's what I would do:\n\nCommand: {final_suggestion.command}\n\nExplanation: {final_suggestion.explanation}\n\nType 'yes' to execute, or ask me to modify it."
            
            else:
                return f"🤔 I need more information. {final_suggestion.explanation}"
                
        except Exception as e:
            return f"❌ Sorry, I encountered an error: {str(e)}"
    
    async def interactive_mode(self):
        """Start interactive mode for natural language interaction."""
        print("🐋 Welcome to Orca OS!")
        print("=" * 50)
        print("I'm your AI assistant. Just tell me what you want to do in plain English.")
        print("Examples:")
        print("  • 'Show me what's using my disk space'")
        print("  • 'Find large files on my computer'")
        print("  • 'Check if my computer is running slowly'")
        print("  • 'Show me running programs'")
        print("\nType 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye! Thanks for using Orca OS!")
                    break
                
                if not user_input:
                    continue
                
                result = await self.process_request(user_input)
                print(f"\nOrca: {result}\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Thanks for using Orca OS!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def single_request(self, user_input: str):
        """Process a single request and return the result."""
        result = await self.process_request(user_input)
        print(f"Orca: {result}")


async def main():
    """Main entry point."""
    orca = OrcaOS()
    
    if len(sys.argv) > 1:
        # Single request mode
        user_input = " ".join(sys.argv[1:])
        await orca.single_request(user_input)
    else:
        # Interactive mode
        await orca.interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
