"""
Resume Customizer Service

Tailors resume based on job requirements and user's GitHub projects.
"""

from typing import List, Optional
from app.models.schemas import GitHubProfile
from app.services.github_service import GitHubService
import logging

logger = logging.getLogger(__name__)


class ResumeCustomizerService:
    """Service to customize resumes based on job requirements"""
    
    @staticmethod
    def extract_keywords(job_description: str) -> List[str]:
        """
        Extract important keywords from job description
        
        Args:
            job_description: Full job description text
        
        Returns:
            List of keywords (skills, tech stack, etc.)
        """
        # Common tech keywords to look for
        keywords = set()
        
        tech_keywords = [
            "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
            "React", "Vue", "Angular", "Node.js", "Django", "FastAPI", "Spring",
            "MongoDB", "PostgreSQL", "MySQL", "Redis", "Elasticsearch",
            "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes",
            "Git", "CI/CD", "Agile", "REST API", "GraphQL", "WebSocket",
            "Machine Learning", "Data Science", "AI", "TensorFlow", "PyTorch"
        ]
        
        job_lower = job_description.lower()
        for keyword in tech_keywords:
            if keyword.lower() in job_lower:
                keywords.add(keyword)
        
        return list(keywords)
    
    @staticmethod
    def calculate_match_score(
        job_keywords: List[str],
        user_skills: List[str],
        user_experience: Optional[str] = None
    ) -> float:
        """
        Calculate how well user matches job requirements
        
        Args:
            job_keywords: Keywords extracted from job
            user_skills: User's listed skills
            user_experience: User's experience level
        
        Returns:
            Match score 0-100
        """
        if not job_keywords:
            return 50.0
        
        matched = 0
        for keyword in job_keywords:
            if any(keyword.lower() in skill.lower() for skill in user_skills):
                matched += 1
        
        score = (matched / len(job_keywords)) * 100
        return min(100.0, score)
    
    @staticmethod
    def customize_resume(
        base_resume: str,
        job_description: str,
        github_profile: Optional[GitHubProfile] = None,
        user_skills: Optional[List[str]] = None
    ) -> str:
        """
        Customize resume for specific job
        
        Args:
            base_resume: User's base resume
            job_description: Target job description
            github_profile: User's GitHub profile (optional)
            user_skills: User's skills list
        
        Returns:
            Customized resume text
        """
        # Start with base resume
        customized = base_resume
        
        # Extract job requirements
        job_keywords = ResumeCustomizerService.extract_keywords(job_description)
        
        # Reorder skills to prioritize job-relevant ones
        if user_skills:
            prioritized_skills = []
            # Add job-matching skills first
            for keyword in job_keywords:
                for skill in user_skills:
                    if keyword.lower() in skill.lower() and skill not in prioritized_skills:
                        prioritized_skills.append(skill)
            
            # Add remaining skills
            for skill in user_skills:
                if skill not in prioritized_skills:
                    prioritized_skills.append(skill)
            
            # Replace skills section if found
            if "## Skills" in customized or "# Skills" in customized:
                skills_text = "\n".join(f"- {skill}" for skill in prioritized_skills[:15])
                # Simple replacement - in production, use more sophisticated parsing
                customized = customized.replace("## Skills", f"## Skills (Tailored)\n{skills_text}\n")
        
        # Add GitHub projects if available and relevant
        if github_profile:
            # Filter projects by relevance to job
            relevant_projects = []
            for repo in github_profile.repos:
                if any(keyword.lower() in (repo.description or "").lower() 
                       or keyword.lower() in (repo.language or "").lower()
                       for keyword in job_keywords):
                    relevant_projects.append(repo)
            
            if relevant_projects:
                projects_section = "\n## Relevant Projects\n"
                for project in relevant_projects[:3]:
                    projects_section += f"- **{project.name}**: {project.description}\n"
                
                customized += projects_section
        
        return customized
    
    @staticmethod
    def generate_cover_letter_prompt(
        job_title: str,
        company: str,
        job_description: str,
        user_name: str,
        user_skills: List[str],
        match_score: float
    ) -> str:
        """
        Generate a prompt for Groq AI to write cover letter
        
        Args:
            job_title: Job title
            company: Company name
            job_description: Full job description
            user_name: User's name
            user_skills: User's skills
            match_score: Job match percentage
        
        Returns:
            Prompt for AI cover letter generation
        """
        prompt = f"""
Write a professional cover letter for:
Position: {job_title} at {company}

Applicant: {user_name}
Relevant Skills: {', '.join(user_skills[:10])}
Job Match Score: {match_score:.0f}%

Job Requirements:
{job_description[:500]}...

The cover letter should:
1. Be professional and concise (250-300 words)
2. Highlight relevant skills that match the job
3. Show genuine interest in the company and role
4. Be personalized and not generic
5. Include a call to action

Please write the cover letter:
"""
        return prompt
    
    @staticmethod
    async def generate_cover_letter_with_groq(
        job_title: str,
        company: str,
        job_description: str,
        user_name: str,
        user_skills: List[str],
        match_score: float
    ) -> str:
        """
        Generate cover letter using Groq AI API
        
        Args:
            job_title: Job title
            company: Company name
            job_description: Full job description
            user_name: User's name
            user_skills: User's skills
            match_score: Job match percentage
        
        Returns:
            Generated cover letter text
        """
        try:
            from groq import Groq
            import os
            
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                logger.warning("GROQ_API_KEY not set, returning template letter")
                return ResumeCustomizerService._generate_template_letter(
                    user_name, company, job_title
                )
            
            # Initialize Groq client
            client = Groq(api_key=groq_api_key)
            
            # Generate prompt
            prompt = ResumeCustomizerService.generate_cover_letter_prompt(
                job_title, company, job_description, user_name, user_skills, match_score
            )
            
            # Call Groq API
            message = client.messages.create(
                model="mixtral-8x7b-32768",  # Free tier model
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            cover_letter = message.content[0].text
            logger.info(f"Generated cover letter for {job_title} at {company}")
            
            return cover_letter.strip()
        
        except ImportError:
            logger.warning("Groq library not installed, using template letter")
            return ResumeCustomizerService._generate_template_letter(
                user_name, company, job_title
            )
        except Exception as e:
            logger.warning(f"Error generating cover letter with Groq: {str(e)}")
            logger.info("Falling back to template letter")
            return ResumeCustomizerService._generate_template_letter(
                user_name, company, job_title
            )
    
    @staticmethod
    def _generate_template_letter(
        user_name: str,
        company: str,
        job_title: str
    ) -> str:
        """
        Generate a template cover letter as fallback
        
        Args:
            user_name: User's name
            company: Company name
            job_title: Job title
        
        Returns:
            Template cover letter
        """
        return f"""
Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. With my technical background and passion for creating solutions, I am confident in my ability to make a meaningful contribution to your team.

Throughout my career, I have developed strong expertise in various technologies and demonstrated my ability to solve complex problems efficiently. I am particularly drawn to {company} because of its commitment to innovation and excellence in the tech industry.

I am excited about the opportunity to bring my skills and experience to your organization and would welcome the chance to discuss how I can contribute to your team's success.

Thank you for considering my application. I look forward to the opportunity to speak with you soon.

Best regards,
{user_name}
"""
