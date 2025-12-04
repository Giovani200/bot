import httpx
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
            "user_id": user_id
        }
        
        try:
            async with httpx.AsyncClient(timeout=settings.vera_timeout) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers
                )
                
                logger.info(f"Vera response status: {response.status_code}")
                logger.debug(f"Vera response body: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    answer = data.get("answer", data.get("response", data.get("message", "Aucune réponse")))
                    sources = data.get("sources", [])
                    
                    logger.info(f"Fact-check réussi pour user {user_id}")
                    
                    return VeraResponse(
                        success=True,
                        answer=answer,
                        sources=sources
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
            return VeraResponse(
                success=False,
                answer="",
                error_message=error_msg
            )
    
    async def fact_check_multiple(self, claims: list[str], user_id: str) -> VeraResponse:
        combined_query = "Vérifie ces affirmations:\n" + "\n".join([f"- {claim}" for claim in claims])
        return await self.fact_check(combined_query, user_id)