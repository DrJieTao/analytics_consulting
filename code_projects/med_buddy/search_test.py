import os
import requests
import llm
from datetime import datetime
import sys

def search_web_with_google_custom_search(query, api_key, cse_id, num_results=10):
    """
    Searches the web using Google Custom Search and returns a list of search results.

    Args:
        query (str): The search query string.
        api_key (str): Your Google Custom Search API key.
        cse_id (str): The ID of your Custom Search Engine.
        num_results (int, optional): The maximum number of search results to return. Defaults to 10.

    Returns:
        list: A list of search result dictionaries, where each dictionary contains the title, snippet, and link of a search result.
              Returns an empty list if no results are found or if an error occurs.
    
    Raises:
        requests.exceptions.HTTPError: If the Google Custom Search API request fails.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    results = []
    start_index = 1

    while len(results) < num_results:
        params = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "start": start_index
        }
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes

        response_data = response.json()
        
        if 'items' in response_data:
            new_results = response_data['items']
            results.extend(new_results)
            start_index += len(new_results)
        else:
            # No more results available
            break

    return results[:num_results]

def main():
    """
    Conducts research on a given topic using a language model and web search.

    This function retrieves search keywords from a language model, performs a web search using Google Custom Search,
    formats the search results, and then uses the results to generate a research report using the language model.
    The report is saved to a markdown file in a subdirectory named after the topic.

    Environment Variables:
        GOOGLE_SEARCH_API_KEY: The API key for Google Custom Search.
        GOOGLE_CSE_ID: The ID of the Custom Search Engine.

    Raises:
        EnvironmentError: If the GOOGLE_SEARCH_API_KEY or GOOGLE_CSE_ID environment variables are not set.
    """

    # Get the model
    model = llm.get_model("gemini-exp-1206")

    # Get API key and CSE ID from environment variables
    google_api_key = os.environ.get("GOOGLE_SEARCH_API_KEY")
    google_cse_id = os.environ.get("GOOGLE_CSE_ID")

    # Check if API key and CSE ID are set
    if not google_api_key or not google_cse_id:
        raise EnvironmentError("GOOGLE_SEARCH_API_KEY or GOOGLE_CSE_ID environment variables not set.")

    # Get keywords from user input
    # Get keywords from user input
    topic = None
    for arg in sys.argv[1:]:
        if arg.startswith("topic="):
            topic = arg.split("=")[1]
            break

    if topic is None:
        raise ValueError("The 'topic' argument must be provided.")

    # Get keywords from user input
    initial_prompt = f"""I'm finding most information on {topic} to help the patients and their loved ones, 
    provide an list of NO MORE THAN 5 most important keywords for search."""


    # Send the initial prompt to the model to get search keywords
    response = model.prompt(initial_prompt)
    keywords = response.text()
    print(f"searching on {keywords} for the most important results...")

    # Perform web search using Google Custom Search
    search_results = search_web_with_google_custom_search(keywords, google_api_key, google_cse_id)


    # Format search results for the prompt
    search_results_text = ""
    for i, result in enumerate(search_results):
        search_results_text += f"{i+1}. {result['title']}\n"
        if 'snippet' in result:
            search_results_text += f"   {result['snippet']}\n"
        search_results_text += f"   URL: {result['link']}\n"

    with open("./prompts/researcher.txt", "r") as f:
        prompt_template = f.read()

    # Insert the search results and keywords into the prompt template
    prompt = prompt_template.format(
        keywords=keywords,
        search_results_text=search_results_text
    )
    # Question: What are the most importat Quality of life factors are discussed on {keywords} based on {search_results_text}?

    # Send the combined prompt to the model
    response = model.prompt(prompt)

    # Print the response
    # print(search_results_text)
    # print(response.text())

    # Create subdirectory if it doesn't exist
    subdirectory = os.path.join("reports", "".join(c if c.isalnum() else "_" for c in topic).strip("_"))
    os.makedirs(subdirectory, exist_ok=True)

    now = datetime.now()
    date_time = now.strftime("%Y%m%d%H%M%S")
    filename = f"{subdirectory}/report{date_time}.md"
    with open(filename, "w") as f:
        f.write(response.text())

if __name__ == "__main__":
    main()