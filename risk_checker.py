from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
from urllib.parse import urlparse
from typing import List, Optional

router = APIRouter()

# Google Safe Browsing API configuration
SAFE_BROWSING_API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
SAFE_BROWSING_URL = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={SAFE_BROWSING_API_KEY}"

class URLCheckRequest(BaseModel):
    url: str

class URLCheckResponse(BaseModel):
    url: str
    is_safe: bool
    status: str  # "SAFE", "RISKY", or "UNVERIFIED"
    threat_types: List[str] = []
    message: str

async def check_google_safe_browsing(url: str) -> dict:
    """Check URL against Google Safe Browsing API"""
    if not SAFE_BROWSING_API_KEY:
        return {"error": "API Key missing"}

    payload = {
        "client": {
            "clientId": "cyber-buddy",
            "clientVersion": "1.0.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SAFE_BROWSING_URL, json=payload, timeout=10.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API Error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/check-url", response_model=URLCheckResponse)
async def check_url_safety(request: URLCheckRequest):
    try:
        url = request.url.strip()

        if not url:
            raise HTTPException(status_code=400, detail="URL cannot be empty")

        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # 1. Check Protocol
        is_protocol_safe = url.startswith('https://')
        protocol_message = ""
        if not is_protocol_safe:
            protocol_message = "⚠️ Warning: This URL uses HTTP (not secure). "
        
        # 2. Check with Google Safe Browsing
        sb_result = await check_google_safe_browsing(url)
        
        threat_types = []
        is_safe = True
        status = "SAFE"
        
        if "matches" in sb_result:
            is_safe = False
            status = "RISKY"
            threat_types = [match["threatType"] for match in sb_result["matches"]]
            message = f"🚨 DANGER: This URL is flagged as {', '.join(threat_types)} by Google Safe Browsing. {protocol_message}Do not visit this site!"
        elif "error" in sb_result:
            # If API fails, fall back to protocol check
            is_safe = is_protocol_safe
            status = "SAFE" if is_safe else "RISKY"
            message = f"{protocol_message}Google Safe Browsing verification unavailable. {'Your connection is encrypted.' if is_safe else 'Your connection is not secure.'}"
        else:
            # Safe according to Google
            is_safe = is_protocol_safe
            status = "SAFE" if is_safe else "RISKY"
            message = f"✅ No threats detected by Google Safe Browsing. {protocol_message}{'Your connection is secure.' if is_safe else ''}"

        return URLCheckResponse(
            url=url,
            is_safe=is_safe,
            status=status,
            threat_types=threat_types,
            message=message
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking URL: {str(e)}")

@router.get("/health")
async def risk_checker_health():
    return {"status": "healthy", "service": "URL Risk Checker"}

# Additional endpoint for bulk URL checking
@router.post("/check-urls")
async def check_multiple_urls(urls: List[str]):
    """Check multiple URLs at once"""
    results = []
    
    for url in urls[:10]:  # Limit to 10 URLs to prevent abuse
        try:
            request = URLCheckRequest(url=url)
            result = await check_url_safety(request)
            results.append(result)
        except Exception as e:
            results.append({
                "url": url,
                "is_safe": False,
                "status": "ERROR",
                "threat_types": [],
                "message": f"Error checking URL: {str(e)}"
            })
    
    return {"results": results}
