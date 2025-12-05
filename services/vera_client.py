import httpx
import json
from typing import Optional
from config.settings import settings
from utils.logger import logger
from models.content import VeraRequest, VeraResponse

class VeraClient:
    def __init__(self):
        self.api_url = settings.vera_api_url
        self.api_key = settings.vera_api_key
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        logger.info(f"VeraClient initialisé avec l'URL: {self.api_url}")
    
    async def fact_check(self, query: str, user_id: str) -> VeraResponse:
        payload = {
            "query": query,
            "userId": user_id
        }
        
        try:
            async with httpx.AsyncClient(timeout=settings.vera_timeout) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers
                )
                
                logger.info(f"Vera response status: {response.status_code}")
                logger.info(f"Vera response headers: {response.headers}")
                logger.info(f"Vera raw response (first 500 chars): {response.text[:500]}")
                
                if response.status_code == 200:
                    response_text = response.text.strip()
                    
                    if not response_text:
                        return VeraResponse(
                            success=False,
                            answer="",
                            error_message="Réponse vide de l'API Vera"
                        )
                    
                    try:
                        data = json.loads(response_text)
                        
                        answer = data.get("answer") or data.get("response") or data.get("message") or data.get("text") or ""
                        sources = data.get("sources", [])
                        
                        if not answer:
                            answer = str(data)
                        
                        logger.info(f"Fact-check réussi pour user {user_id}")
                        
                        return VeraResponse(
                            success=True,
                            answer=answer,
                            sources=sources
                        )
                    
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        logger.error(f"Response text: {response_text[:1000]}")
                        
                        lines = response_text.split('\n')
                        answer_parts = []
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            
                            if line.startswith('data: '):
                                line = line[6:]
                            
                            if line == '[DONE]':
                                continue
                            
                            try:
                                chunk = json.loads(line)
                                if isinstance(chunk, dict):
                                    text = chunk.get('answer') or chunk.get('text') or chunk.get('content') or chunk.get('delta')
                                    if text:
                                        answer_parts.append(str(text))
                                elif isinstance(chunk, str):
                                    answer_parts.append(chunk)
                            except json.JSONDecodeError:
                                if line and not line.startswith('{'):
                                    answer_parts.append(line)
                        
                        final_answer = ''.join(answer_parts) if answer_parts else response_text
                        
                        return VeraResponse(
                            success=True,
                            answer=final_answer,
                            sources=[]
                        )
                else:
                    error_msg = f"Erreur API Vera: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return VeraResponse(
                        success=False,
                        answer="",
                        error_message=error_msg
                    )
        
        except httpx.TimeoutException:
            error_msg = "Timeout de l'API Vera"
            logger.error(error_msg)
            return VeraResponse(
                success=False,
                answer="",
                error_message=error_msg
            )
        
        except Exception as e:
            error_msg = f"Erreur Vera: {str(e)}"
            logger.error(error_msg)
            logger.exception("Stack trace complète:")
            return VeraResponse(
                success=False,
                answer="",
                error_message=error_msg
            )
    
    async def fact_check_multiple(self, claims: list[str], user_id: str) -> VeraResponse:
        combined_query = "Vérifie ces affirmations:\n" + "\n".join([f"- {claim}" for claim in claims])
        return await self.fact_check(combined_query, user_id)