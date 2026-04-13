from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai
import os

# load api key
load_dotenv()
API_KEY = os.getenv("API_KEY")

# configure gemini
client = genai.Client(api_key=API_KEY)

# extrct headline, subheadline, cta
def _extract_key_elements(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # remove sections
    for tag in soup(["nave", "header", "footer", "script", "style"]):
        tag.decompose()

    # extract headline
    headlines = soup.find_all("h1")
    headline = "No headline found"
    for h in headlines:
        text = h.get_text(strip=True)
        if (text and len(text) > 15 
            and "logo" not in text.lower()
            and "sign in" not in text.lower()
            and "login" not in text.lower()):
            headline = text
            break


    # extract subheadline
    subheadline = ""
    paragraphs = soup.find_all("p")

    for p in paragraphs:
        text = p.get_text(strip=True)
        if text and len(text) > 30:
            subheadline = text
            break

    # extract the CTA
    buttons = soup.find_all(["button", "a"])

    cta_text = "Click here"
    
    priority_words = ["start", "get", "try", "sign", "free",
                      "demo", "join", "buy", "book", "create"]
    fallbacks = []
    for btn in buttons:
        if btn.find_parent("nav"):
            continue

        text = btn.get_text(strip=True)
        if not text or len(text) > 30:
            continue

        if any(word in text.lower() for word in priority_words):
            cta_text = text
            break

        if (5 <= len(text) <= 25 and
            text[0].isupper() and # button-like
            " " in text and
            not any(b in text.lower() for b in ["revenue", "growth",
                                                "customers", "users", "%"])):
            fallbacks.append(text)  
        

        # use fallback if no strong cta found
        if cta_text == "Click here" and fallbacks:
            cta_text = fallbacks[0]

    return headline, subheadline, cta_text

def _rewrite_content(ad_text: str, headline: str, subheadline: str, cta: str):
    prompt = f"""
You are an expert in conversion rate optimization (CRO).

Rewrite the landing page content to match the ad intent.

Ad Creative:
{ad_text}

Landing Page:
Headline: {headline}
Subheadline: {subheadline}
CTA: {cta}

Rules:
- Do NOT invent new features
- Keep meaning consistent
- Make it more persuasive
- Keep it concise

Output STRICT JSON:
{{
  "headline": "...",
  "subheadline": "...",
  "cta": "..."
}}
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    return response.text