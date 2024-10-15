from serpapi import Client as SerpApiClient 
from serpapi.exceptions import APIKeyNotProvided

def request(prompt, api_key=None):
    try:
        sp_client = SerpApiClient(api_key=api_key)
    except APIKeyNotProvided as e:
        raise Exception(f"API key not valid or not provided")
    response = sp_client.get_search({
        "engine": "google",
        "q": prompt
    })
    return response
