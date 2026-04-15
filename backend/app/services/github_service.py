"""
GitHub Integration Service

Fetches user's GitHub profile and repositories for resume enhancement.
"""

import aiohttp
from typing import List, Optional
from app.models.schemas import GitHubProfile, GitHubRepo
import logging

logger = logging.getLogger(__name__)


class GitHubService:
    """Service to interact with GitHub API"""
    
    GITHUB_API_BASE = "https://api.github.com"
    
    @staticmethod
    async def get_user_repos(username: str, token: Optional[str] = None) -> Optional[GitHubProfile]:
        """
        Fetch GitHub user profile and repositories
        
        Args:
            username: GitHub username
            token: GitHub personal access token (optional, for higher rate limits)
        
        Returns:
            GitHubProfile with repos, or None if error
        """
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"token {token}"
            
            async with aiohttp.ClientSession() as session:
                # Get user profile
                user_url = f"{GitHubService.GITHUB_API_BASE}/users/{username}"
                async with session.get(user_url, headers=headers) as resp:
                    if resp.status != 200:
                        logger.error(f"Failed to fetch GitHub user {username}: {resp.status}")
                        return None
                    
                    user_data = await resp.json()
                
                # Get user repos
                repos_url = f"{GitHubService.GITHUB_API_BASE}/users/{username}/repos"
                async with session.get(repos_url, headers=headers, params={"sort": "stars", "per_page": 30}) as resp:
                    if resp.status != 200:
                        repos_data = []
                    else:
                        repos_data = await resp.json()
            
            # Parse repos
            repos = []
            for repo in repos_data:
                if not repo.get("fork"):  # Skip forked repos
                    repos.append(GitHubRepo(
                        name=repo["name"],
                        url=repo["html_url"],
                        description=repo.get("description"),
                        language=repo.get("language"),
                        stars=repo.get("stargazers_count", 0),
                        topics=repo.get("topics", [])
                    ))
            
            return GitHubProfile(
                username=user_data["login"],
                name=user_data.get("name"),
                bio=user_data.get("bio"),
                repos=repos[:10],  # Top 10 repos
                public_repos=user_data.get("public_repos", 0)
            )
        
        except Exception as e:
            logger.error(f"Error fetching GitHub profile: {str(e)}")
            return None
    
    @staticmethod
    def format_repos_for_resume(profile: GitHubProfile) -> str:
        """
        Format GitHub repos into resume-friendly text
        
        Args:
            profile: GitHubProfile object
        
        Returns:
            Formatted text for resume
        """
        if not profile.repos:
            return ""
        
        text = f"\n## GitHub Projects ({profile.username})\n"
        for repo in profile.repos[:5]:  # Top 5 repos in resume
            text += f"- **{repo.name}** ({repo.stars} ⭐): {repo.description or 'No description'}\n"
            if repo.language:
                text += f"  Languages: {repo.language}\n"
            if repo.topics:
                text += f"  Topics: {', '.join(repo.topics[:3])}\n"
        
        return text
    
    @staticmethod
    def extract_technologies(profile: GitHubProfile) -> List[str]:
        """
        Extract all technologies from repos
        
        Args:
            profile: GitHubProfile object
        
        Returns:
            List of unique technologies/languages
        """
        techs = set()
        
        # Add languages
        for repo in profile.repos:
            if repo.language:
                techs.add(repo.language)
            techs.update(repo.topics)
        
        return list(techs)
