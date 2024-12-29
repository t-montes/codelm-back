from serpapi import Client as SerpApiClient 
from serpapi.exceptions import APIKeyNotProvided

def request(prompt, api_key=None, num_results=10):
    try:
        sp_client = SerpApiClient(api_key=api_key)
    except APIKeyNotProvided as e:
        raise Exception(f"API key not valid or not provided")
    response = sp_client.search({
        "engine": "google",
        "q": prompt,
        "num": num_results,
    })
    return response
