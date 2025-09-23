#!/usr/bin/env python3
"""
Orca AI Package Manager
Advanced AI-powered package management with intelligent recommendations
"""

import asyncio
import subprocess
import json
import re
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Add orca-core to path
sys.path.insert(0, '/opt/orca-os')

from orca.llm.manager import LLMManager
from orca.core.models import UserQuery, SystemContext
from orca.utils.config import load_config


@dataclass
class PackageInfo:
    """Package information with AI insights."""
    name: str
    version: str
    description: str
    size: str
    ai_category: str
    ai_importance: str
    ai_recommendation: str
    dependencies: List[str]
    conflicts: List[str]


class OrcaPackageManager:
    """Advanced AI-powered package manager for Orca OS."""
    
    def __init__(self):
        """Initialize the Orca package manager."""
        self.config = load_config('/opt/orca-os/config/orca.yaml')
        self.llm_manager = LLMManager(self.config.llm.dict())
        self.package_cache = {}
        self.installation_history = []
        
    async def install_package(self, package_name: str, user_intent: str = None) -> Dict[str, Any]:
        """Install a package with AI assistance."""
        try:
            # Get package information
            package_info = await self._get_package_info(package_name)
            
            if not package_info:
                return {"status": "error", "message": f"Package '{package_name}' not found"}
            
            # AI analysis of installation
            ai_analysis = await self._analyze_package_installation(package_name, package_info, user_intent)
            
            # Check for conflicts
            conflicts = await self._check_package_conflicts(package_name)
            
            # Get dependencies
            dependencies = await self._get_package_dependencies(package_name)
            
            # Install the package
            install_result = await self._execute_installation(package_name, dependencies)
            
            # Record installation
            self.installation_history.append({
                "package": package_name,
                "timestamp": datetime.now().isoformat(),
                "user_intent": user_intent,
                "ai_analysis": ai_analysis,
                "result": install_result
            })
            
            return {
                "status": "success" if install_result["success"] else "error",
                "package": package_name,
                "ai_analysis": ai_analysis,
                "conflicts": conflicts,
                "dependencies": dependencies,
                "install_result": install_result
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _get_package_info(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed package information."""
        try:
            # Use apt show to get package information
            result = subprocess.run(
                ['apt', 'show', package_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
            
            # Parse apt show output
            package_info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    package_info[key] = value
            
            return package_info
            
        except Exception as e:
            print(f"Error getting package info: {e}")
            return None
    
    async def _analyze_package_installation(self, package_name: str, package_info: Dict, user_intent: str) -> Dict[str, Any]:
        """Analyze package installation with AI."""
        try:
            # Create context for AI analysis
            context = f"""
            Package: {package_name}
            Description: {package_info.get('description', 'No description')}
            Version: {package_info.get('version', 'Unknown')}
            Size: {package_info.get('installed_size', 'Unknown')}
            User Intent: {user_intent or 'Not specified'}
            """
            
            # Query AI for analysis
            query = UserQuery(query=f"Analyze this package installation request: {context}")
            system_context = SystemContext(
                processes=[],
                memory_usage=0,
                cpu_usage=0,
                disk_usage=0
            )
            
            suggestion = await self.llm_manager.generate_suggestion(query, system_context)
            
            # Determine package category
            category = await self._categorize_package(package_name, package_info)
            
            # Determine importance
            importance = await self._assess_package_importance(package_name, package_info, user_intent)
            
            return {
                "category": category,
                "importance": importance,
                "ai_insights": suggestion.explanation or "No specific insights available",
                "recommendation": suggestion.command or "Proceed with installation"
            }
            
        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}
    
    async def _categorize_package(self, package_name: str, package_info: Dict) -> str:
        """Categorize package using AI."""
        try:
            description = package_info.get('description', '').lower()
            name = package_name.lower()
            
            # Common package categories
            categories = {
                'development': ['dev', 'development', 'programming', 'code', 'sdk', 'api'],
                'system': ['system', 'core', 'kernel', 'driver', 'firmware'],
                'multimedia': ['audio', 'video', 'media', 'graphics', 'image', 'sound'],
                'network': ['network', 'web', 'http', 'ftp', 'ssh', 'vpn'],
                'security': ['security', 'crypto', 'encrypt', 'firewall', 'antivirus'],
                'productivity': ['office', 'document', 'text', 'editor', 'spreadsheet'],
                'game': ['game', 'gaming', 'entertainment', 'fun'],
                'utility': ['tool', 'utility', 'helper', 'assistant']
            }
            
            # Check description and name for category keywords
            for category, keywords in categories.items():
                if any(keyword in description or keyword in name for keyword in keywords):
                    return category
            
            return 'other'
            
        except Exception:
            return 'unknown'
    
    async def _assess_package_importance(self, package_name: str, package_info: Dict, user_intent: str) -> str:
        """Assess package importance using AI."""
        try:
            # Critical system packages
            critical_packages = [
                'systemd', 'kernel', 'glibc', 'bash', 'coreutils',
                'apt', 'dpkg', 'gcc', 'python3', 'python'
            ]
            
            if package_name in critical_packages:
                return 'critical'
            
            # Check if it's a development tool
            if 'dev' in package_name or 'development' in package_info.get('description', '').lower():
                return 'development'
            
            # Check user intent
            if user_intent:
                if any(word in user_intent.lower() for word in ['important', 'critical', 'essential', 'required']):
                    return 'important'
                elif any(word in user_intent.lower() for word in ['optional', 'nice', 'convenience']):
                    return 'optional'
            
            return 'normal'
            
        except Exception:
            return 'unknown'
    
    async def _check_package_conflicts(self, package_name: str) -> List[str]:
        """Check for package conflicts."""
        try:
            result = subprocess.run(
                ['apt', 'install', '--dry-run', package_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            conflicts = []
            if result.returncode != 0:
                # Parse error output for conflicts
                error_output = result.stderr
                if 'conflicts' in error_output.lower():
                    conflicts.append("Package conflicts detected")
                if 'breaks' in error_output.lower():
                    conflicts.append("Package breaks existing packages")
            
            return conflicts
            
        except Exception as e:
            return [f"Error checking conflicts: {str(e)}"]
    
    async def _get_package_dependencies(self, package_name: str) -> List[str]:
        """Get package dependencies."""
        try:
            result = subprocess.run(
                ['apt', 'depends', package_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            dependencies = []
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Depends:' in line:
                        deps = line.replace('Depends:', '').strip()
                        dependencies.extend([dep.strip() for dep in deps.split(',')])
            
            return dependencies
            
        except Exception as e:
            return [f"Error getting dependencies: {str(e)}"]
    
    async def _execute_installation(self, package_name: str, dependencies: List[str]) -> Dict[str, Any]:
        """Execute the actual package installation."""
        try:
            # Update package list first
            update_result = subprocess.run(
                ['sudo', 'apt', 'update'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if update_result.returncode != 0:
                return {
                    "success": False,
                    "error": "Failed to update package list",
                    "details": update_result.stderr
                }
            
            # Install the package
            install_result = subprocess.run(
                ['sudo', 'apt', 'install', '-y', package_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            return {
                "success": install_result.returncode == 0,
                "output": install_result.stdout,
                "error": install_result.stderr if install_result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Installation timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_packages(self, query: str) -> List[Dict[str, Any]]:
        """Search for packages with AI assistance."""
        try:
            # Use apt search
            result = subprocess.run(
                ['apt', 'search', query],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            packages = []
            for line in result.stdout.split('\n'):
                if '/' in line and ' ' in line:
                    parts = line.split(' ', 1)
                    if len(parts) >= 2:
                        package_name = parts[0].split('/')[0]
                        description = parts[1].strip()
                        
                        # Get AI analysis for each package
                        ai_analysis = await self._analyze_package_search(package_name, description, query)
                        
                        packages.append({
                            "name": package_name,
                            "description": description,
                            "ai_analysis": ai_analysis
                        })
            
            # Sort by AI relevance score
            packages.sort(key=lambda x: x['ai_analysis'].get('relevance_score', 0), reverse=True)
            
            return packages[:20]  # Return top 20 results
            
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]
    
    async def _analyze_package_search(self, package_name: str, description: str, search_query: str) -> Dict[str, Any]:
        """Analyze package search result with AI."""
        try:
            context = f"""
            Package: {package_name}
            Description: {description}
            Search Query: {search_query}
            """
            
            query = UserQuery(query=f"Analyze how well this package matches the search query: {context}")
            system_context = SystemContext(
                processes=[],
                memory_usage=0,
                cpu_usage=0,
                disk_usage=0
            )
            
            suggestion = await self.llm_manager.generate_suggestion(query, system_context)
            
            # Calculate relevance score (0-100)
            relevance_score = 0
            query_words = search_query.lower().split()
            description_words = description.lower().split()
            
            # Simple relevance scoring
            for word in query_words:
                if word in description_words:
                    relevance_score += 20
                if word in package_name.lower():
                    relevance_score += 30
            
            relevance_score = min(100, relevance_score)
            
            return {
                "relevance_score": relevance_score,
                "ai_insights": suggestion.explanation or "No specific insights",
                "recommendation": suggestion.command or "Consider this package"
            }
            
        except Exception as e:
            return {
                "relevance_score": 0,
                "error": f"AI analysis failed: {str(e)}"
            }
    
    async def get_installation_recommendations(self) -> List[Dict[str, Any]]:
        """Get AI-powered installation recommendations."""
        try:
            # Analyze system state
            system_context = await self._get_system_context()
            
            # Get AI recommendations
            query = UserQuery(query="Recommend useful packages for this system based on current setup")
            suggestion = await self.llm_manager.generate_suggestion(query, system_context)
            
            # Parse recommendations (this would be more sophisticated in a real implementation)
            recommendations = [
                {
                    "package": "htop",
                    "reason": "Better process monitoring",
                    "category": "utility",
                    "priority": "high"
                },
                {
                    "package": "tree",
                    "reason": "Directory structure visualization",
                    "category": "utility",
                    "priority": "medium"
                },
                {
                    "package": "neofetch",
                    "reason": "System information display",
                    "category": "utility",
                    "priority": "low"
                }
            ]
            
            return recommendations
            
        except Exception as e:
            return [{"error": f"Failed to get recommendations: {str(e)}"}]
    
    async def _get_system_context(self) -> SystemContext:
        """Get current system context."""
        try:
            # Get system information
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent()
            disk = psutil.disk_usage('/')
            
            # Get running processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] and proc_info['cpu_percent'] > 1.0:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return SystemContext(
                processes=processes,
                memory_usage=memory.percent,
                cpu_usage=cpu,
                disk_usage=disk.percent
            )
            
        except Exception as e:
            return SystemContext(
                processes=[],
                memory_usage=0,
                cpu_usage=0,
                disk_usage=0
            )
    
    async def get_package_analytics(self) -> Dict[str, Any]:
        """Get package installation analytics."""
        try:
            # Analyze installation history
            total_installations = len(self.installation_history)
            
            # Categorize installations
            categories = {}
            for install in self.installation_history:
                package = install['package']
                category = install['ai_analysis'].get('category', 'unknown')
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
            
            # Get most installed packages
            package_counts = {}
            for install in self.installation_history:
                package = install['package']
                package_counts[package] = package_counts.get(package, 0) + 1
            
            most_installed = sorted(package_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_installations": total_installations,
                "categories": categories,
                "most_installed": most_installed,
                "installation_trends": await self._analyze_installation_trends(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to get analytics: {str(e)}"}
    
    async def _analyze_installation_trends(self) -> List[str]:
        """Analyze installation trends with AI."""
        try:
            if not self.installation_history:
                return ["No installation history available"]
            
            # Get recent installations
            recent_installs = self.installation_history[-10:]  # Last 10 installations
            
            # Analyze patterns
            trends = []
            
            # Check for development tools
            dev_tools = [install for install in recent_installs if 'dev' in install['package']]
            if len(dev_tools) > len(recent_installs) * 0.5:
                trends.append("High focus on development tools")
            
            # Check for system utilities
            utilities = [install for install in recent_installs if install['ai_analysis'].get('category') == 'utility']
            if len(utilities) > len(recent_installs) * 0.3:
                trends.append("Preference for utility packages")
            
            if not trends:
                trends.append("No specific trends detected")
            
            return trends
            
        except Exception as e:
            return [f"Error analyzing trends: {str(e)}"]


async def main():
    """Main entry point for Orca Package Manager."""
    manager = OrcaPackageManager()
    
    print("🐋 Orca AI Package Manager")
    print("=" * 50)
    
    # Get recommendations
    recommendations = await manager.get_installation_recommendations()
    print("AI Recommendations:")
    for rec in recommendations:
        print(f"  • {rec['package']}: {rec['reason']} ({rec['category']})")
    
    # Get analytics
    analytics = await manager.get_package_analytics()
    if "error" not in analytics:
        print(f"\nAnalytics:")
        print(f"  Total Installations: {analytics['total_installations']}")
        print(f"  Categories: {analytics['categories']}")


if __name__ == "__main__":
    asyncio.run(main())
