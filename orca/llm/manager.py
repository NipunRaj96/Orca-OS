"""
LLM Manager for Orca OS.

Handles local LLM integration with structured output generation.
"""

import json
import logging
from typing import Dict, Any, Optional

import httpx
from pydantic import ValidationError

from ..core.models import CommandSuggestion, CommandAction, CommandRisk, UserQuery, SystemContext
from .prompts import PromptManager
from ..tools.search import SearchManager

logger = logging.getLogger(__name__)


class LLMManager:
    """Manages LLM interactions and command generation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize LLM manager with configuration."""
        self.config = config
        self.prompt_manager = PromptManager()
        self.search_manager = SearchManager()
        self.client = httpx.AsyncClient(timeout=60.0)  # Increased timeout for larger model
        
        # LLM endpoint configuration
        self.base_url = getattr(config, 'base_url', "http://localhost:11434")
        self.model_name = getattr(config, 'model', "llama2:latest")
        self.temperature = getattr(config, 'temperature', 0.1)
        self.max_tokens = getattr(config, 'max_tokens', 512)
    
    async def generate_suggestion(
        self, 
        query: UserQuery, 
        context: SystemContext
    ) -> CommandSuggestion:
        """Generate a command suggestion from user query and system context."""
        try:
            # Check if we need to search for current information
            enhanced_query = query
            if self.search_manager.should_search(query.query):
                logger.info(f"Enhancing query with search: {query.query}")
                enhanced_query = UserQuery(
                    query=self.search_manager.enhance_query_with_search(
                        query.query, 
                        context.model_dump()
                    )
                )
            
            # Build structured prompt
            prompt = self.prompt_manager.build_command_prompt(enhanced_query, context)
            
            # Call LLM
            response = await self._call_llm(prompt)
            
            # Parse structured response
            suggestion = self._parse_response(response, query, context)
            
            return suggestion
            
        except Exception as e:
            logger.error(f"Error generating suggestion: {e}")
            # Return a safe fallback
            return CommandSuggestion(
                command="echo 'Error: Unable to process request'",
                confidence=0.0,
                action=CommandAction.CLARIFY,
                risk_level=CommandRisk.SAFE,
                explanation="An error occurred while processing your request. Please try again."
            )
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the local LLM API."""
        try:
            # Try Ollama first (most common for local setup)
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    }
                }
            )
            response.raise_for_status()
            return response.json()["response"]
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling LLM: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling LLM: {e}")
            raise
    
    def _parse_response(
        self, 
        response: str, 
        query: UserQuery, 
        context: SystemContext
    ) -> CommandSuggestion:
        """Parse LLM response into structured CommandSuggestion."""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            # Validate and create CommandSuggestion
            suggestion = CommandSuggestion(
                command=data.get("command", ""),
                confidence=float(data.get("confidence", 0.5)),
                action=CommandAction(data.get("action", "clarify")),
                risk_level=CommandRisk(data.get("risk_level", "safe")),
                explanation=data.get("explanation"),
                context_used=data.get("context_used", [])
            )
            
            return suggestion
            
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            logger.debug(f"Raw response: {response}")
            
            # Fallback: try to extract command from plain text
            command = self._extract_command_from_text(response)
            
            return CommandSuggestion(
                command=command,
                confidence=0.3,  # Low confidence for unparsed response
                action=CommandAction.CLARIFY,
                risk_level=CommandRisk.SAFE,
                explanation="Response could not be fully parsed. Please review the command carefully."
            )
    
    def _extract_command_from_text(self, text: str) -> str:
        """Extract command from plain text response."""
        # Simple heuristic: look for lines that start with common command patterns
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for lines that start with common command patterns
            if any(line.startswith(prefix) for prefix in ['ls', 'ps', 'df', 'find', 'grep', 'cat', 'head', 'tail']):
                # Remove any markdown formatting
                line = line.replace('`', '').replace('**', '').replace('*', '')
                return line
        
        # Fallback
        return "echo 'No valid command found in response'"
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
