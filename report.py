from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os
from typing import Optional

router = APIRouter()

class ReportRequest(BaseModel):
    location: str  # state or city name

class OfficeInfo(BaseModel):
    address: str
    helpline: str
    website: str
    location_type: str  # "city" or "state"

class ReportResponse(BaseModel):
    location: str
    office_info: Optional[OfficeInfo] = None
    national_helpline: str
    national_website: str
    message: str

# Load cybercrime offices data
def load_cybercrime_offices():
    try:
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to app directory, then to data
        data_path = os.path.join(current_dir, "..", "data", "cybercrime_offices.json")
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: cybercrime_offices.json not found, using default data")
        return {"states": {}, "national": {"helpline": "1930", "website": "https://cybercrime.gov.in"}}

offices_data = load_cybercrime_offices()

def normalize_location(location: str) -> str:
    """Normalize location name for matching"""
    return location.lower().strip().replace(" ", "_")

def find_office_info(location: str) -> Optional[OfficeInfo]:
    """Find cybercrime office information for given location"""
    normalized_location = normalize_location(location)
    
    # Search in states and cities
    for state, cities in offices_data["states"].items():
        # Check if location matches state name
        if normalized_location == state or normalized_location in state:
            # Return first city in the state as default
            first_city = next(iter(cities.values()))
            return OfficeInfo(
                address=first_city["address"],
                helpline=first_city["helpline"],
                website=first_city["website"],
                location_type="state"
            )
        
        # Check if location matches any city in the state
        for city, info in cities.items():
            if normalized_location == city or normalized_location in city:
                return OfficeInfo(
                    address=info["address"],
                    helpline=info["helpline"],
                    website=info["website"],
                    location_type="city"
                )
    
    # Additional fuzzy matching for common variations
    location_mappings = {
        "bombay": "mumbai",
        "calcutta": "kolkata",
        "madras": "chennai",
        "bengaluru": "bangalore",
        "hyderabad": "hyderabad",
        "ahmedabad": "ahmedabad",
        "delhi": "new_delhi",
        "ncr": "new_delhi",
        "gurgaon": "new_delhi",
        "noida": "new_delhi",
        "pondicherry": "puducherry",
        "pondy": "puducherry"
    }
    
    mapped_location = location_mappings.get(normalized_location)
    if mapped_location:
        return find_office_info(mapped_location)
    
    return None

@router.get("/offices/{location}", response_model=ReportResponse)
async def get_cybercrime_office(location: str):
    """Get cybercrime office information for a specific location"""
    try:
        office_info = find_office_info(location)
        national_info = offices_data.get("national", {})
        
        if office_info:
            message = f"Found cybercrime office information for {location.title()}. You can report cybercrime incidents at the provided address or through the helpline number."
        else:
            message = f"Specific office information not found for {location.title()}. Please use the national helpline or visit the nearest police station. You can also file a complaint online at the national cybercrime portal."
        
        return ReportResponse(
            location=location.title(),
            office_info=office_info,
            national_helpline=national_info.get("helpline", "1930"),
            national_website=national_info.get("website", "https://cybercrime.gov.in"),
            message=message
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving office information: {str(e)}")

@router.get("/all-offices")
async def get_all_offices():
    """Get all available cybercrime office locations"""
    try:
        all_locations = []
        
        for state, cities in offices_data["states"].items():
            state_info = {
                "state": state.replace("_", " ").title(),
                "cities": []
            }
            
            for city in cities.keys():
                state_info["cities"].append(city.replace("_", " ").title())
            
            all_locations.append(state_info)
        
        return {
            "locations": all_locations,
            "national_helpline": offices_data["national"]["helpline"],
            "national_website": offices_data["national"]["website"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving office list: {str(e)}")

@router.get("/emergency")
async def get_emergency_contacts():
    """Get emergency cybercrime contact information"""
    return {
        "emergency_helpline": "1930",
        "national_website": "https://cybercrime.gov.in",
        "email": "complaints@cybercrime.gov.in",
        "instructions": [
            "Call 1930 for immediate cybercrime assistance",
            "Visit cybercrime.gov.in to file online complaint",
            "Preserve all evidence (screenshots, emails, messages)",
            "Do not delete any suspicious communications",
            "Report as soon as possible after the incident"
        ],
        "what_to_report": [
            "Online financial fraud",
            "Identity theft",
            "Cyberbullying and harassment",
            "Phishing and email scams",
            "Social media crimes",
            "Online job fraud",
            "Ransomware attacks",
            "Data theft"
        ]
    }

@router.get("/health")
async def report_health():
    return {"status": "healthy", "service": "Cybercrime Reporting"}
