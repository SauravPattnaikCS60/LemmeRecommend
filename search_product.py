from dotenv import load_dotenv
import os
import serpapi

load_dotenv()
serp_api_key = os.environ['SERP_API']

client = serpapi.Client(api_key=serp_api_key)
def get_amazon_search_results(search_query):
    results = client.search({
    "engine": "amazon",
    "k": search_query,
    "amazon_domain": "amazon.in"
    })
    organic_results = results["organic_results"][:15]
    response = {"search_results":organic_results}
    return response