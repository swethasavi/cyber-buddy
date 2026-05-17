from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import json
import os
from typing import Optional

router = APIRouter()

# Configure Google AI
google_ai_key = os.getenv("GOOGLE_AI_API_KEY")
if google_ai_key:
    genai.configure(api_key=google_ai_key)
else:
    print("Warning: GOOGLE_AI_API_KEY not found in environment variables")

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[list] = []

class ChatResponse(BaseModel):
    response: str
    is_cybersecurity_related: bool
    cyber_law_info: Optional[dict] = None

# Load cyber law knowledge base
def load_cyber_law_knowledge():
    try:
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to app directory, then to data
        data_path = os.path.join(current_dir, "..", "data", "cyber_law_knowledge.json")
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: cyber_law_knowledge.json not found, using empty data")
        return {"scams": {}}

cyber_law_data = load_cyber_law_knowledge()

def check_cyberattack_keywords(message: str) -> Optional[dict]:
    """Check if message contains cyberattack-related keywords and return relevant info"""
    message_lower = message.lower()

    # Check for exact matches first
    for attack_type, attack_info in cyber_law_data["cyberattacks"].items():
        attack_name = attack_type.replace("_", " ")
        if attack_name in message_lower or attack_type in message_lower:
            return {
                "attack_name": attack_name.title(),
                "definition": attack_info["definition"],
                "indian_cyber_law": attack_info["indian_cyber_law"],
                "penalty": attack_info["penalty"],
                "safety_tips": attack_info["safety_tips"]
            }
    
    # Check for common attack-related terms
    attack_keywords = {
        "phish": "phishing_attacks",
        "virus": "malware_attacks",
        "trojan": "malware_attacks",
        "malware": "malware_attacks",
        "ddos": "denial_of_service",
        "dos": "denial_of_service",
        "hack": "hacking",
        "unauthorized": "hacking",
        "identity": "identity_theft",
        "breach": "data_breach",
        "defacement": "website_defacement",
        "stalk": "cyberstalking_cyberbullying",
        "bully": "cyberstalking_cyberbullying",
        "piracy": "piracy_digital_content_theft",
        "fraud": "financial_fraud",
        "upi": "financial_fraud",
        "banking": "financial_fraud"
    }

    for keyword, attack_type in attack_keywords.items():
        if keyword in message_lower and attack_type in cyber_law_data["cyberattacks"]:
            attack_info = cyber_law_data["cyberattacks"][attack_type]
            return {
                "attack_name": attack_type.replace("_", " ").title(),
                "definition": attack_info["definition"],
                "indian_cyber_law": attack_info["indian_cyber_law"],
                "penalty": attack_info["penalty"],
                "safety_tips": attack_info["safety_tips"]
            }
    
    return None

def is_cybersecurity_related(message: str) -> bool:
    """Check if the message is related to cybersecurity"""
    cybersecurity_keywords = [
        "cyber", "security", "hack", "malware", "virus", "phishing", "ransomware",
        "firewall", "antivirus", "password", "encryption", "breach", "vulnerability",
        "threat", "attack", "fraud", "scam", "identity theft", "data protection",
        "privacy", "authentication", "authorization", "ssl", "https", "vpn",
        "cybercrime", "cyber law", "it act", "digital security", "online safety"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in cybersecurity_keywords)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    try:
        # Check if the message is cybersecurity-related
        if not is_cybersecurity_related(request.message):
            return ChatResponse(
                response="I'm Cyber Buddy, your cybersecurity assistant! I can only help with cybersecurity-related questions. Please ask me about topics like online safety, cyber threats, digital security, cyber laws, or any cybersecurity concerns you might have.",
                is_cybersecurity_related=False
            )
        
        # Check for specific cyberattack information
        cyber_law_info = check_cyberattack_keywords(request.message)

        # Check if Google AI is configured
        if not google_ai_key:
            bot_response = "I'm Cyber Buddy! I'm currently running in offline mode, but I can still provide you with legal information about cyberattacks if you ask about specific threats."
            if cyber_law_info:
                bot_response = f"I found some information about {cyber_law_info['attack_name']} in my knowledge base."
            
            return ChatResponse(
                response=bot_response,
                is_cybersecurity_related=True,
                cyber_law_info=cyber_law_info
            )

        # Create the model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create a cybersecurity-focused prompt
        system_prompt = """You are Cyber Buddy, a specialized cybersecurity assistant. You ONLY answer questions related to cybersecurity, online safety, digital security, cyber threats, cyber laws, and related topics.

Key guidelines:
1. Focus exclusively on cybersecurity topics
2. Provide practical, actionable advice
3. Include relevant Indian cyber laws when applicable
4. Be concise but comprehensive
5. Always prioritize user safety and security
6. If asked about non-cybersecurity topics, politely redirect to cybersecurity

Topics you can help with:
- Cyber threats (malware, phishing, ransomware, etc.)
- Online safety and digital hygiene
- Password security and authentication
- Data protection and privacy
- Cyber laws and regulations (especially Indian IT Act)
- Incident response and reporting
- Security tools and best practices
- Social engineering awareness
- Mobile and IoT security

Respond in a helpful, professional manner while keeping cybersecurity as the central focus."""
        
        # Combine system prompt with user message
        full_prompt = f"{system_prompt}\n\nUser Question: {request.message}"
        
        # Generate response
        try:
            response = model.generate_content(full_prompt)
            bot_response = response.text
        except Exception as ai_error:
            print(f"Google AI API error: {ai_error}")
            bot_response = "I'm experiencing technical difficulties with the AI service. However, I can still provide you with cybersecurity guidance based on my knowledge base."

        # If we have specific cyber law information, append it or mention it
        if cyber_law_info and not bot_response:
             bot_response = f"I found some legal information regarding {cyber_law_info['attack_name']}."
        
        return ChatResponse(
            response=bot_response,
            is_cybersecurity_related=True,
            cyber_law_info=cyber_law_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@router.get("/health")
async def bot_health():
    return {"status": "healthy", "service": "Cybersecurity Bot"}
