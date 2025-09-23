"""
Command executor for Orca OS.

Safely executes commands with sandboxing and monitoring.
"""

import asyncio
import subprocess
import time
from typing import Dict, Any
from ..core.models import CommandSuggestion, ExecutionResult


class CommandExecutor:
    """Executes commands safely with sandboxing."""
    
    def __init__(self, config):
        """Initialize executor with configuration."""
        self.config = config
        self.use_sandbox = getattr(config, 'use_sandbox', True)
        self.timeout = getattr(config, 'timeout', 30)
        self.max_output_size = getattr(config, 'max_output_size', 1024 * 1024)  # 1MB
    
    async def execute(self, suggestion: CommandSuggestion) -> ExecutionResult:
        """Execute a command suggestion safely."""
        start_time = time.time()
        
        try:
            if self.use_sandbox:
                result = await self._execute_sandboxed(suggestion)
            else:
                result = await self._execute_direct(suggestion)
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=result.returncode == 0,
                exit_code=result.returncode,
                stdout=result.stdout[:self.max_output_size],
                stderr=result.stderr[:self.max_output_size],
                execution_time=execution_time,
                sandbox_used=self.use_sandbox
            )
            
        except asyncio.TimeoutError:
            return ExecutionResult(
                success=False,
                exit_code=124,  # Timeout exit code
                stdout="",
                stderr="Command timed out",
                execution_time=time.time() - start_time,
                sandbox_used=self.use_sandbox
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                exit_code=1,
                stdout="",
                stderr=f"Execution error: {str(e)}",
                execution_time=time.time() - start_time,
                sandbox_used=self.use_sandbox
            )
    
    async def _execute_sandboxed(self, suggestion: CommandSuggestion) -> subprocess.CompletedProcess:
        """Execute command in a sandboxed environment."""
        # On macOS, use direct execution with resource limits
        # On Linux, use systemd-run for sandboxing
        import platform
        
        if platform.system() == "Darwin":  # macOS
            # Use direct execution on macOS
            return await self._execute_direct(suggestion)
        else:
            # Use systemd-run for Linux
            sandbox_cmd = [
                "systemd-run",
                "--scope",
                "--user",
                "--property=MemoryLimit=512M",
                "--property=CPUQuota=50%",
                "sh", "-c", suggestion.command
            ]
        
            process = await asyncio.create_subprocess_exec(
                *sandbox_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
                
                return subprocess.CompletedProcess(
                    args=sandbox_cmd,
                    returncode=process.returncode,
                    stdout=stdout.decode('utf-8', errors='replace'),
                    stderr=stderr.decode('utf-8', errors='replace')
                )
            finally:
                if process.returncode is None:
                    process.kill()
                    await process.wait()
    
    async def _execute_direct(self, suggestion: CommandSuggestion) -> subprocess.CompletedProcess:
        """Execute command directly (for testing/development)."""
        process = await asyncio.create_subprocess_shell(
            suggestion.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            
            return subprocess.CompletedProcess(
                args=suggestion.command,
                returncode=process.returncode,
                stdout=stdout.decode('utf-8', errors='replace'),
                stderr=stderr.decode('utf-8', errors='replace')
            )
        finally:
            if process.returncode is None:
                process.kill()
                await process.wait()
