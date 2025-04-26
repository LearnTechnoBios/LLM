# LLMs as Information Architects: Creating an Automated Company Brochure System

In today's rapidly evolving digital landscape, Large Language Models (LLMs) are transforming how we approach content creation and information processing tasks. This article explores a practical implementation: an automated system that converts company websites into comprehensive brochures using local LLM technology. We'll dive into the technical aspects, ethical considerations, and practical applications of this solution.

## Introduction: The Challenge of Information Synthesis

Have you ever needed to quickly understand what a company does, its culture, and its offerings without spending hours digging through their website? Perhaps you're preparing for an interview, researching potential investments, or scoping out competitors. This common challenge inspired our solution: an automated brochure generator that leverages LLMs to scrape, analyze, and synthesize information from company websites.

Unlike traditional web scrapers that simply extract text, our solution uses an LLM to intelligently identify relevant content and transform it into a cohesive narrative—a skill that previously required human judgment and writing ability. What makes this approach particularly interesting is that it runs entirely on local infrastructure using Ollama, making it accessible to developers without requiring expensive API subscriptions.

## GitHub Repo code:
https://github.com/LearnTechnoBios/LLM/blob/main/code/2_brochure_builder_cmd.py

## The Technical Foundation: Understanding the Architecture

Let's break down the main components of our brochure generation system:

### 1. Web Scraping with BeautifulSoup

The foundation of our system is a web scraper built with Python's BeautifulSoup library. This component:
- Fetches the HTML content from specified URLs
- Extracts text content while removing scripts, styles, and other non-content elements
- Identifies links for further exploration
- Implements respectful scraping practices with rotating user agents and time delays

### 2. Intelligent Link Analysis

Not all links on a company website are relevant for our brochure. The system uses an LLM to intelligently select which links to follow:

```python
link_system_prompt = (
    "You are provided with a list of links found on a webpage. "
    "You are able to decide which of the links would be most relevant to include in a brochure about the company, "
    "such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
    "You should respond in JSON as in this example:\n"
    '{ "links": [ {"type": "about page", "url": "https://full.url/goes/here/about"}, {"type": "careers page", "url": "https://another.full.url/careers"} ] }'
)
```

This approach saves computational resources by focusing only on pages that contain valuable company information, rather than blindly crawling the entire site.

### 3. Content Aggregation and Processing

Once the system has collected content from the main page and relevant subpages, it aggregates this information and prepares it for the LLM to analyze:

```python
def get_all_details(url):
    result = "Landing page:\n"
    website = Website(url)
    result += website.get_contents()
    links = get_links(url)
    for link in links.get("links", []):
        if link["url"] and link["url"] != "/" and len(link["url"]) > 1:
            time.sleep(random.uniform(1, 2))  # Respectful delay between requests
            result += f"\n\n{link['type']}\n"
            result += Website(link["url"]).get_contents()
    return result
```

### 4. LLM-Powered Content Generation

The final piece is using a locally-hosted LLM through Ollama to transform the gathered information into a coherent brochure:

```python
system_prompt = (
    "You are an assistant that analyzes the contents of several relevant pages from a company website "
    "and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown. "
    "Include details of company culture, customers and careers/jobs if you have the information."
)
```

## Running LLMs Locally with Ollama

A key feature of this solution is its use of Llama 3.2 running locally through Ollama. This approach offers several advantages:

1. **Cost Efficiency**: Eliminates the need for expensive API subscriptions
2. **Privacy**: Data doesn't leave your local environment
3. **Flexibility**: Freedom to customize and fine-tune the model
4. **Control**: No rate limits or unexpected downtime

Setting up Ollama is straightforward:
- Install Ollama on your local machine
- Pull the Llama 3.2 model with a simple command
- Configure the Python client to connect to the local endpoint

```python
OLLAMA_URL = "http://localhost:11434/v1"
OLLAMA_KEY = "ollama"

openai = OpenAI(base_url=OLLAMA_URL, api_key=OLLAMA_KEY)
```

The code leverages the OpenAI client library to interact with Ollama using the same interface, making it easy to switch between local and cloud-based LLMs if needed.

## Ethical Scraping and Web Citizenship

Our implementation incorporates several best practices for ethical web scraping:

1. **Rotating User Agents**: The system uses different user agents to avoid placing unusual load on servers:

```python
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
]
```

2. **Timing Delays**: Implements random delays between requests to respect server resources:

```python
time.sleep(random.uniform(1, 2))  # Respectful delay between requests
```

3. **Selective Crawling**: Only follows relevant links rather than indiscriminately crawling the entire website

These practices ensure our tool respects website owners' resources while still gathering the necessary information.

## Practical Applications and Use Cases

This automated brochure generator offers value across multiple domains:

### Business Intelligence and Competitive Analysis
Sales teams and business analysts can quickly generate summaries of competitors, potential clients, or partners before meetings or strategy sessions.

### Recruitment and Job Searching
Job seekers can generate concise company profiles to prepare for interviews, while recruiters can create standardized company information packets for candidates.

### Investment Research
Investors can efficiently process information about potential investments, automating the first stage of company research.

### Educational Settings
Students learning about business analysis can use this tool to quickly understand company structures and operations.

## Limitations and Future Improvements

While powerful, the current implementation has some limitations:

1. **JavaScript-Heavy Sites**: The scraper may struggle with websites that load content dynamically through JavaScript

2. **Visual Content**: The system cannot interpret images, charts, or other visual elements that might contain important information

3. **Structure Preservation**: Complex page layouts and hierarchical information might lose their structure when extracted as plain text

Future enhancements could include:

- Integration with headless browsers like Playwright or Selenium for JavaScript rendering
- Image analysis capabilities using multimodal models
- More sophisticated content filtering and categorization
- Implementation of robots.txt compliance

## Conclusion: The Evolving Landscape of LLM Applications

This brochure generator represents just one example of how LLMs are transforming traditional data processing workflows. What's particularly exciting is how accessible these technologies have become—running sophisticated models like Llama 3.2 locally was unthinkable just a few years ago.

As these technologies continue to evolve, we'll see increasingly sophisticated applications that blend web scraping, content analysis, and natural language generation. The democratization of these tools through projects like Ollama opens up possibilities for developers to create specialized solutions without relying on expensive cloud services.

Whether you're exploring LLMs for business intelligence, content creation, or research assistance, the core principles demonstrated in this project—ethical data collection, intelligent content filtering, and context-aware generation—provide a solid foundation for building responsible and effective AI solutions.

## Key Takeaways for Implementation

1. **Start Small**: Begin with a focused use case and expand functionality incrementally

2. **Respect Web Resources**: Implement ethical scraping practices including delays between requests, rotating user agents, and selective crawling

3. **Effective Prompting**: The quality of your LLM outputs depends heavily on clear system and user prompts that provide context and objectives

4. **Local First**: Consider running models locally for cost savings and privacy before scaling to cloud solutions

5. **Balance Automation and Oversight**: While automation is powerful, maintain human oversight for quality control and ethical considerations

---

By combining web scraping, local LLM technology, and thoughtful prompt engineering, developers can create powerful information processing tools that were previously impossible without significant human effort. As you explore your own implementations, remember that the most effective LLM applications aren't just about replacing human work—they're about augmenting human capabilities to process information more efficiently and effectively.
