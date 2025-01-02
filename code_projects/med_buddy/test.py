import llm
from serpapi import GoogleSearch
import os

def search_web_with_serper(query, api_key):
    search = GoogleSearch({
        "q": query,
        "api_key": api_key
    })
    results = search.get_dict()
    return results["organic_results"] if "organic_results" in results else []

def main():
    # Get the model
    model = llm.get_model("gemini-exp-1206")

    # Get Serper API key from environment variable
    serper_api_key = os.environ.get("SERPER_API_KEY")

    # Get keywords from user input
    keywords = "multiple myeloma experimental treatments"

    # Perform web search using serper.dev
    search_results = search_web_with_serper(keywords, serper_api_key)

    # Format search results for the prompt
    search_results_text = ""
    for i, result in enumerate(search_results):
        search_results_text += f"{i+1}. {result['title']}\n"
        search_results_text += f"   {result['snippet']}\n"
        search_results_text += f"   URL: {result['link']}\n"

    # Combine search results with the original prompt
    # prompt = f"""
    # You are a helpful assistant. Use the following information to answer the question:

    # Search Results:
    # {search_results_text}

    # Question: what are these webpages talking about {keywords} based on {search_results_text}?
    # """

    # # Send the combined prompt to the model
    # response = model.prompt(prompt)

    # Print the response
    print(search_results_text)
    # print(response.text())

if __name__ == "__main__":
    main()