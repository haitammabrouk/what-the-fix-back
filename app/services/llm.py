import httpx
import json
import logging
from typing import Dict
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.base_url = settings.llm_base_url
        self.token = settings.llm_token
        self.model = settings.llm_model

    async def generate_title_and_tags(self, problem: str, solution: str) -> Dict[str, any]:
        """
        Generate title and tags for a given problem-solution pair using actual AI model
        Returns: {"title": str, "tags": List[str]}
        Raises: Exception if AI generation fails (no fallback)
        """
        prompt = self._build_prompt(problem, solution)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert software engineer and DevOps specialist. Generate concise, professional titles and relevant technical tags for IT problems and solutions. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 200,
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                error_msg = f"AI API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)

            data = response.json()
            ai_response = data["choices"][0]["message"]["content"]

            logger.info(f"Raw AI response: {ai_response}")

            # Parse JSON response
            result = json.loads(ai_response)

            # Validate and clean the response
            title = result.get("title", "")[:80]  # Limit title length
            tags = result.get("tags", [])[:6]  # Limit to 6 tags max

            # Clean tags (remove duplicates, empty strings, normalize)
            tags = list(set([
                tag.strip().lower().replace(" ", "-")
                for tag in tags
                if tag.strip()
            ]))[:5]  # Final limit to 5 tags

            logger.info(f"AI Generated title: {title}")
            logger.info(f"AI Generated tags: {tags}")

            return {
                "title": title,
                "tags": tags
            }

    def _build_prompt(self, problem: str, solution: str) -> str:
        """Build optimized prompt for IT/DevOps title and tag generation"""
        return f"""
Generate a professional title and relevant technical tags for this IT/DevOps problem and solution:

**Problem:** {problem[:600]}
**Solution:** {solution[:600]}

Requirements:
- Title: Max 80 characters, clear and descriptive, professional tone
- Tags: 3-5 relevant technical tags (programming languages, frameworks, tools, concepts)
- Focus on: IT, software development, DevOps, infrastructure, databases, cloud, etc.
- Response format: {{"title": "...", "tags": ["tag1", "tag2", "tag3"]}}

Examples:
Problem: "React app crashes when user logs in due to undefined state"
Solution: "Added null checks and proper state initialization in useEffect"
Response: {{"title": "Fix React login crash - undefined state handling", "tags": ["react", "javascript", "state-management", "hooks", "debugging"]}}

Problem: "Docker container fails to start in production environment"
Solution: "Updated Dockerfile to use correct base image and fixed environment variables"
Response: {{"title": "Fix Docker container startup - image and env config", "tags": ["docker", "containers", "deployment", "production", "devops"]}}

Problem: "Database queries are slow and timing out"
Solution: "Added proper indexes and optimized JOIN queries"
Response: {{"title": "Optimize database performance - indexes and queries", "tags": ["database", "sql", "performance", "optimization", "indexing"]}}

Please respond with JSON only:
"""


# Singleton instance
llm_service = LLMService()