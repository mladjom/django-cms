# services.py
import aiohttp
import asyncio
from django.conf import settings
from typing import Optional, Dict, Any
from django.conf import settings

class GPT2Service:
    """Service class for interacting with GPT-2 API"""
    
    def __init__(self):
        self.api_url = settings.GPT2_API_URL

    async def generate_text(self, prompt: str, max_length: int = 100) -> Optional[str]:
        """Generate text with improved length control"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.api_url}/generate/",
                    json={
                        "input": prompt,
                        "max_length": max_length + 50,  # Add buffer for better sentence completion
                        "temperature": 0.7,
                        "num_return_sequences": 1,
                        "top_p": 0.9,
                        "top_k": 50,
                        "stop_sequences": ["."]  # Try to stop at sentence boundaries
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        text = data["generated_texts"][0]
                        
                        # Clean and truncate the text
                        text = text.strip()
                        if len(text) > max_length:
                            # Try to find a sentence boundary
                            last_period = text[:max_length].rfind('.')
                            if last_period > 0:
                                text = text[:last_period + 1]
                            else:
                                text = text[:max_length]
                        
                        return text
                    return None
            except Exception as e:
                print(f"Error generating text: {str(e)}")
                return None