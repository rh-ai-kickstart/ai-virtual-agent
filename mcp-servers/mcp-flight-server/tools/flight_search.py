from mcp import Tool
import os
import requests

class FlightSearchTool(Tool):
    name = "mcp::flight-search"
    description = "Searches for flights based on origin, destination, and date range using Google Search API"
    parameters = {
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "Starting city"},
            "destination": {"type": "string", "description": "Destination city"},
            "start_date": {"type": "string", "description": "Start date of the trip"},
            "end_date": {"type": "string", "description": "End date of the trip"}
        },
        "required": ["origin", "destination", "start_date", "end_date"]
    }

    def run(self, input_data):
        origin = input_data["origin"]
        destination = input_data["destination"]
        start_date = input_data["start_date"]
        end_date = input_data["end_date"]

        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

        query = f"Flights from {origin} to {destination} {start_date} to {end_date} site:google.com/travel/flights"

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": query
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            return {"error": response.text}

        results = response.json().get("items", [])
        return [
            {
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet")
            } for item in results
        ]