from serpapi import Client as SerpApiClient 
import os

sp_client = SerpApiClient(api_key=os.getenv("SERPAPI_KEY"))

def request(prompt):
    response = sp_client.get_search({
        "engine": "google",
        "q": prompt
    })
    return response
