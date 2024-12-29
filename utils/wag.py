from utils import gen_prompt, extract_code, serpcall, llmcall
import html2text
import requests
import json
import ast

def _create_search_query(llm_prompt, model, llmargs):
    system_message = "Using the provided user inputs, generate a Google search query that captures the essence of the information. Ensure the query is concise and focused on the most critical aspects to found relevant information efficiently."    
    query = llmcall(llm_prompt, model, system_message, **llmargs)
    if query.startswith('"') and query.endswith('"'):
        query = query[1:-1]
    return query

def _direct_filter_relevant_results(search_results, N):
    assert "organic_results" in search_results, "No organic results found in the search response"
    results = search_results["organic_results"][:N]
    return results

def _rag_filter_relevant_results(llm_prompt, model, search_results, N, llmargs):
    assert "organic_results" in search_results, "No organic results found in the search response"
    results = search_results["organic_results"]
    llm_prompt += f"\n\nFilter most relevant results.\n\nSearch Results:\n" + json.dumps(results, indent=2)
    system_message = f"""\
Using the provided user inputs and the search results, filter the most relevant results to the specific problem. Return a JSON list with the position of the relevant results (please note that positions start from 1).
Please also take into account what's the website, not just the title.
An example would be: 
```json
[4,2,7]
```
But for this case you are asked to extract exactly the top {N} most relevant positions (in relevance order).\
"""

    filtered_idxs = llmcall(llm_prompt, model, system_message, **llmargs)
    idxs = ast.literal_eval( extract_code(filtered_idxs) )
    return [results[idx-1] for idx in idxs]

def _get_raw_gtdoc(link):
    resp = requests.get(link)
    resp.raise_for_status()
    html = resp.text
    return html2text.html2text(html)

def _s1(llm_prompt, model, serpapi_key, M, N, filter_method, llmargs):
    """
    OUT
    links: dict of str [URLs of the GT selected websites]
    """
    assert N <= M, "N should be less than or equal to M"

    query = _create_search_query(llm_prompt, model, llmargs)
    search_results = serpcall(query, serpapi_key, M)
    if filter_method == 'direct':
        filtered_results = _direct_filter_relevant_results(search_results, N)
    else:
        filtered_results = _rag_filter_relevant_results(llm_prompt, model, search_results, N, llmargs)
    return {result['title']: result['link'] for result in filtered_results}

def _s2(llm_prompt, model, links, llmargs):
    """
    OUT
    gt_docs_all: str [GT documents for each website (labeled)]
    """
    system_message = """\
Using the provided user inputs and the raw 'markdown-like' document extracted from a relevant URL, generate a coherent and highly useful document (also markdown-like) that can be used to answer the user query, considering the information from the raw GT document. 
Take into account that the raw document contains lots of irrelevant information, and the final document should be concise and focused on the most critical aspects to solve the query, only taking into account the most relevant information.\
"""
    gt_docs_all = ""
    for title, link in links.items():
        raw_gt_doc = _get_raw_gtdoc(link)
        
        new_llm_prompt = llm_prompt + f"\n\nRAW GT DOCUMENT:\n{title}:\n{raw_gt_doc}"
        gt_doc = llmcall(new_llm_prompt, model, system_message, **llmargs)

        gt_docs_all += f"\n\n{title}:\n{gt_doc}"
    return gt_docs_all

def _s3(prompt, code, gt_docs, model, gt_docs_all, llmargs):
    """
    OUT
    new_gt_docs: str [summarized GT documents web-extracted]
    """
    llm_prompt = gen_prompt(prompt, code)
    system_message = "Using the provided user inputs and all the Ground-Truth documents, summarize all the GT documents into a single coherent document highly useful to answer the user query. DO NOT directly solve the query, but bring the most relevant information to solve it."
    llm_prompt += f"\n\nGT Documents:\n\n{gt_docs}\n\n" + gt_docs_all
    return llmcall(llm_prompt, model, system_message, **llmargs)

def generate_gt_docs_wag(prompt, code, gt_docs, model, serpapi_key=None, M=10, N=5, filter_method='direct', summarize=False, **kwargs):
    """
    IN
    prompt: str [User query (might be empty)]
    code: str [Code snippet (might be empty, only if prompt is not empty)]
    gt_docs: str [GT documents if any]
    model: str [LLM model to use]
    serpapi_key: str [SerpApi key]
    M: int [Number of search results to consider]
    N: int [Number of GT documents to consider]
    filter_method: str [Filter method to use ('direct' or 'rag')]
    summarize: bool [Summarize the GT documents or not]

    OUT
    new_gt_docs: str [GT documents web-extracted]
    """
    llm_prompt = gen_prompt(prompt, code, gt_docs)

    links = _s1(llm_prompt, model, serpapi_key, M, N, filter_method, kwargs)
    gt_docs_all = _s2(llm_prompt, model, links, kwargs)
    if summarize:
        new_gt_docs = _s3(prompt, code, gt_docs, model, gt_docs_all, kwargs)
    else:
        new_gt_docs = gt_docs_all
    return new_gt_docs
