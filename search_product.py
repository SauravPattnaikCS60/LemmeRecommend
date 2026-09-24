from dotenv import load_dotenv
import os
import serpapi
import random

load_dotenv()

MAX_SEARCH_RESULTS = 50
MAX_RANDOMIZED_RESULTS = 20 # pick 20 samples randomly
MAX_TOP_RESULTS = MAX_SEARCH_RESULTS - MAX_RANDOMIZED_RESULTS

serp_api_key = os.environ['SERP_API']
client = serpapi.Client(api_key=serp_api_key)

def filter_results(results, budget):
    relevant_options = []
    for option in results:
        if not option.get('sponsored',False) and option.get('extracted_price',float('inf')) <= budget:
            relevant_options.append(option)
    
    return relevant_options

def get_amazon_search_results(search_query,budget):
    results = client.search({
    "engine": "amazon",
    "k": search_query,
    "amazon_domain": "amazon.in"
    })
    all_results = results["organic_results"]
    
    # filter top results
    top_results = all_results[:MAX_TOP_RESULTS]
    
    # pick random options from the next set of results
    random.seed(60)
    random_results = random.sample(all_results[MAX_TOP_RESULTS:],min(MAX_RANDOMIZED_RESULTS,len(all_results[MAX_TOP_RESULTS:])))
    
    # filter results
    filtered_results = filter_results(top_results+random_results,budget)
    response = {"search_results":filtered_results}
    return response