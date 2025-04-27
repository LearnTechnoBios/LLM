#!/usr/bin/env python3
import os
import json
import time
import random
import requests
from openai import OpenAI
from typing import List
from bs4 import BeautifulSoup
import gradio as gr

# --- Configuration ---
MODEL = "llama3.2"
OLLAMA_URL = "http://localhost:11434/v1"
OLLAMA_KEY = "ollama"

USER_AGENTS = [
    # Rotating user agents improves stealth and reduces blocks[3][4][5]
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS)
    }

# --- Utility Classes ---
class Website:
    """
    Represents a scraped website with title, text, and links.
    """
    def __init__(self, url):
        self.url = url
        self.title = "No title found"
        self.text = ""
        self.links = []
        self._fetch_and_parse()

    def _fetch_and_parse(self):
        try:
            response = requests.get(self.url, headers=get_headers(), timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            self.title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"
            if soup.body:
                for tag in soup.body(["script", "style", "img", "input"]):
                    tag.decompose()
                self.text = soup.body.get_text(separator="\n", strip=True)
            self.links = [a.get('href') for a in soup.find_all('a', href=True) if a.get('href')]
        except Exception as e:
            print(f"Error fetching {self.url}: {e}")

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

    def get_website_links(self):
        return self.links

# --- LLM Prompt Templates ---
link_system_prompt = (
    "You are provided with a list of links found on a webpage. "
    "You are able to decide which of the links would be most relevant to include in a brochure about the company, "
    "such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
    "You should respond in JSON as in this example:\n"
    '{ "links": [ {"type": "about page", "url": "https://full.url/goes/here/about"}, {"type": "careers page", "url": "https://another.full.url/careers"} ] }'
)

def get_links_user_prompt(website):
    user_prompt = (
            f"Here is the list of links on the website of {website.url} - "
            "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. "
            "Do not include Terms of Service, Privacy, email links.\n"
            "Links (some might be relative links):\n"
            + "\n".join(website.links)
    )
    return user_prompt

def get_links(url):
    website = Website(url)
    openai = OpenAI(base_url=OLLAMA_URL, api_key=OLLAMA_KEY)
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(website)}
        ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    return json.loads(result)

# --- Brochure Content Aggregator ---
def get_all_details(url):
    result = "Landing page:\n"
    website = Website(url)
    result += website.get_contents()
    links = get_links(url)
    print("Found links:", links)
    for link in links.get("links", []):
        # Only follow links that are not "/" and have length > 1
        if link["url"] and link["url"] != "/" and len(link["url"]) > 1:
            time.sleep(random.uniform(1, 2))  # Respectful delay between requests[1][4][5]
            result += f"\n\n{link['type']}\n"
            result += Website(link["url"]).get_contents()
    return result

system_prompt = (
    "You are an assistant that analyzes the contents of several relevant pages from a company website "
    "and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown. "
    "Include details of company culture, customers and careers/jobs if you have the information."
)

def get_brochure_user_prompt(company_name, url):
    user_prompt = (
            f"You are looking at a company called: {company_name}\n"
            "Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
            + get_all_details(url)
    )
    return user_prompt[:5000]  # Truncate if more than 5,000 characters

def create_brochure(company_name, url):
    openai = OpenAI(base_url=OLLAMA_URL, api_key=OLLAMA_KEY)
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ],
    )
    # print(response.choices[0].message.content)
    return response.choices[0].message.content


view = gr.Interface(
    fn=create_brochure,
    inputs=[
        gr.Textbox(label="Company name:"),
        gr.Textbox(label="Landing page URL including http:// or https://")
        # ,gr.Dropdown(["GPT", "Claude"], label="Select model")
    ],
    outputs=[gr.Markdown(label="Brochure:")],
    flagging_mode="never"
)
view.launch(debug=True, share=True)