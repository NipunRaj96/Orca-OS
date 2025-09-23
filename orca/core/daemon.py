"""
Orca daemon for background operation.
"""

import asyncio
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .models import UserQuery, CommandSuggestion
from .executor import CommandExecutor
from .context import ContextProvider
from ..security.policy import PolicyEngine
from ..llm.manager import LLMManager
from ..utils.config import load_config

logger = logging.getLogger(__name__)


class OrcaDaemon:
    """Background daemon for Orca OS."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        """Initialize daemon."""
        self.host = host
        self.port = port
        self.config = load_config("config/orca.yaml")
        self.app = FastAPI(title="Orca OS Daemon")
        
        # Initialize components
        self.llm_manager = LLMManager(self.config.llm.dict())
        self.context_provider = ContextProvider()
        self.policy_engine = PolicyEngine(self.config.policy.dict())
        self.executor = CommandExecutor(self.config.executor.dict())
        
        self._setup_routes()
        self._setup_middleware()
    
    def _setup_middleware(self):
        """Setup CORS and other middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.post("/query")
        async def handle_query(query: UserQuery) -> Dict[str, Any]:
            """Handle a user query."""
            try:
                # Get system context
                context = await self.context_provider.get_context()
                
                # Generate suggestion
                suggestion = await self.llm_manager.generate_suggestion(query, context)
                
                # Apply policy
                validated_suggestion = self.policy_engine.validate(suggestion)
                
                return {
                    "suggestion": validated_suggestion.dict(),
                    "status": "success"
                }
                
            except Exception as e:
                logger.error(f"Error handling query: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/execute")
        async def execute_command(suggestion: CommandSuggestion) -> Dict[str, Any]:
            """Execute a command suggestion."""
            try:
                result = await self.executor.execute(suggestion)
                
                return {
                    "result": result.dict(),
                    "status": "success"
                }
                
            except Exception as e:
                logger.error(f"Error executing command: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/status")
        async def get_status() -> Dict[str, Any]:
            """Get daemon status."""
            return {
                "status": "running",
                "version": "0.1.0",
                "llm_available": True,  # TODO: Check actual LLM status
                "policy_active": True
            }
        
        @self.app.get("/health")
        async def health_check() -> Dict[str, str]:
            """Health check endpoint."""
            return {"status": "healthy"}
    
    async def start(self):
        """Start the daemon."""
        logger.info(f"Starting Orca daemon on {self.host}:{self.port}")
        
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level=self.config.log_level.lower()
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    async def stop(self):
        """Stop the daemon."""
        logger.info("Stopping Orca daemon")
        # Cleanup resources
        await self.llm_manager.close()
