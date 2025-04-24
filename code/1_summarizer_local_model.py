#!/usr/bin/env python3

from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import argparse

# Headers for website requests to avoid blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# LLM configuration
MODEL = "llama3.2"
OLLAMA_URL = "http://localhost:11434/v1"
OLLAMA_KEY = "ollama"

# Prompt templates
SYSTEM_PROMPT = """You are an assistant that analyzes the contents of a website 
and provides a short summary, ignoring text that might be navigation related. 
Respond in markdown."""


class Website:
    def __init__(self, url):
        """Create a Website object from the given URL using BeautifulSoup"""
        self.url = url
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors

            soup = BeautifulSoup(response.content, 'html.parser')
            self.title = soup.title.string if soup.title else "No title found"

            # Remove irrelevant elements
            if soup.body:
                for tag in soup.body.find_all(["script", "style", "img", "input", "nav", "footer"]):
                    tag.decompose()
                self.text = soup.body.get_text(separator="\n", strip=True)
            else:
                self.text = "No body content found"
        except Exception as e:
            self.title = f"Error: {str(e)}"
            self.text = f"Failed to fetch website content: {str(e)}"


class WebsiteSummarizer:
    def __init__(self):
        """Initialize the summarizer with OpenAI client"""
        self.client = OpenAI(base_url=OLLAMA_URL, api_key=OLLAMA_KEY)

    def _create_user_prompt(self, website):
        """Create user prompt for the LLM based on website content"""
        return f"""You are looking at a website titled {website.title}
The contents of this website is as follows; please provide a short summary 
of this website in markdown. If it includes news or announcements, 
then summarize these too.

{website.text}"""

    def _create_messages(self, website):
        """Create the messages array for the LLM API call"""
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": self._create_user_prompt(website)}
        ]

    def summarize(self, url):
        """Generate a summary of the given website URL"""
        website = Website(url)

        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=self._create_messages(website)
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"## Error Generating Summary\nFailed to generate summary: {str(e)}"

    def display_summary(self, url):
        """Display the summary with markdown formatting"""
        summary = self.summarize(url)
        print(summary)  # Plain text version


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize a website's content using an LLM.")
    parser.add_argument("url", help="The URL of the website to summarize")
    args = parser.parse_args()
    summarizer = WebsiteSummarizer()
    summarizer.display_summary(args.url)