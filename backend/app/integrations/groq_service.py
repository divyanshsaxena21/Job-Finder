from groq import Groq
from app.config import settings
from app.models.schemas import JobMatchResult
from app.services.auth_service import PreferencesService
from typing import Tuple


class GroqService:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = "mixtral-8x7b-32768"  # or "llama2-70b-4096"

    async def match_job(self, user_id: str, job_data: dict) -> JobMatchResult:
        """Match a job against user preferences using Groq"""
        
        # Get user preferences
        prefs = await PreferencesService.get_preferences(user_id)
        
        # Prepare prompt
        user_skills = ", ".join(prefs.get("skills", []) or [])
        user_roles = ", ".join(prefs.get("roles", []) or [])
        user_exp = prefs.get("experience", "Unknown")
        
        job_title = job_data.get("title", "")
        job_company = job_data.get("company", "")
        job_desc = job_data.get("description", "")[:1000]  # Limit to 1000 chars
        
        prompt = f"""Analyze the match between a candidate and a job posting.

CANDIDATE PROFILE:
- Skills: {user_skills or "Not specified"}
- Target Roles: {user_roles or "Not specified"}
- Experience Level: {user_exp}

JOB POSTING:
- Title: {job_title}
- Company: {job_company}
- Description: {job_desc}

Provide a JSON response with exactly this structure (NO markdown, pure JSON):
{{
  "match_score": <0-100 integer>,
  "reason": "<brief explanation of match>",
  "missing_skills": ["<skill1>", "<skill2>"],
  "strengths": ["<strength1>", "<strength2>"]
}}

Be realistic with scoring. 0-30 is poor match, 30-60 is moderate, 60-100 is strong match."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500,
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            # Try to extract JSON if response has extra text
            if "{" in response_text:
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                json_str = response_text[start_idx:end_idx]
                result_dict = json.loads(json_str)
            else:
                result_dict = json.loads(response_text)
            
            return JobMatchResult(
                match_score=float(result_dict.get("match_score", 0)),
                reason=result_dict.get("reason", ""),
                missing_skills=result_dict.get("missing_skills", []),
                strengths=result_dict.get("strengths", [])
            )
        
        except Exception as e:
            print(f"Error in job matching: {e}")
            # Return default match
            return JobMatchResult(
                match_score=50,
                reason="Unable to analyze. Please review manually.",
                missing_skills=[],
                strengths=[]
            )

    async def generate_resume(self, user_id: str, job_data: dict, user_profile: dict) -> str:
        """Generate tailored resume for a job"""
        
        prefs = await PreferencesService.get_preferences(user_id)
        
        prompt = f"""Create a professional resume tailored for the following job:

JOB: {job_data.get('title')} at {job_data.get('company')}
DESCRIPTION: {job_data.get('description', '')[:800]}

CANDIDATE:
- Name: {user_profile.get('name', 'John Doe')}
- Email: {user_profile.get('email', 'email@example.com')}
- Skills: {', '.join(prefs.get('skills', []) or [])}
- Experience: {prefs.get('experience', 'Not specified')}

Generate a concise, ATS-friendly resume (2 pages max) that:
1. Highlights relevant skills for this job
2. Shows matched experience
3. Uses action verbs
4. Is professionally formatted

Return only the resume content, ready to copy-paste."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=2000,
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating resume: {e}")
            return "Unable to generate resume. Please create manually."

    async def generate_cover_letter(self, user_id: str, job_data: dict, user_profile: dict) -> str:
        """Generate tailored cover letter for a job"""
        
        prefs = await PreferencesService.get_preferences(user_id)
        
        prompt = f"""Write a compelling cover letter for this job application:

JOB: {job_data.get('title')} at {job_data.get('company')}
DESCRIPTION: {job_data.get('description', '')[:800]}

CANDIDATE:
- Name: {user_profile.get('name', 'John Doe')}
- Email: {user_profile.get('email', 'email@example.com')}
- Skills: {', '.join(prefs.get('skills', []) or [])}
- Experience: {prefs.get('experience', 'Not specified')}

Write a professional cover letter that:
1. Addresses the hiring manager (use "Hiring Manager" if unknown)
2. Shows genuine interest in the role and company
3. Highlights 2-3 relevant accomplishments
4. Matches the job requirements
5. Has a strong closing

Keep it to 1 page. Return only the cover letter content."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500,
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating cover letter: {e}")
            return "Unable to generate cover letter. Please create manually."
