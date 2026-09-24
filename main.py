from prompts import get_product_features_prompt
from ollama_call import call_ollama_qwen
from models import Response
from langchain_core.output_parsers import JsonOutputParser
import pandas as pd
from search_product import get_amazon_search_results
import os
import json

def get_product_specifications(product, user_requirement,budget):
    prompt = get_product_features_prompt(product, user_requirement,budget)
    response = call_ollama_qwen(prompt)
    # print(response)
    parser = JsonOutputParser(pydantic_object=Response)
    try:
        parsed_response = parser.parse(response)
        return (parsed_response['features'],parsed_response['rationale'],parsed_response['search_query'])
    except:
        return (None,None,None)

if __name__ == "__main__":
    # product_tuples = [("chair","for wfh",10000),("tablet","for reading ebooks",25000),("mattress","to prevent backpain",10000)]
    # result_tuples = []
    # for product, user_req, budget in product_tuples:
    #     print(product, user_req,budget)
    #     features, rationale, search_query = get_product_specifications(product,user_req, budget)
    #     result_tuples.append((product, user_req, budget,features, rationale, search_query))
    
    # result_df = pd.DataFrame(result_tuples, columns=['Product','User Requirement','Budget','Features(AI)','Rationale','Search Query(AI)'])
    # result_df.to_csv('initial_results.csv',index=False)
    
    # os.makedirs('results',exist_ok=True)
    # df = pd.read_csv('initial_results.csv')
    # for index, row in df.iterrows():
    #     search_term = row['Search Query(AI)']
    #     budget = row['Budget']
    #     if search_term:
    #         results = get_amazon_search_results(search_term,budget)
    #         file_name = row['Product'] + "_amazon_search_results.json"
    #         with open(f"results/{file_name}","w") as f:
    #             json.dump(results,f)
    pass