from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, request, render_template
import os
import requests
import google.generativeai as genai
import json

# load api key
load_dotenv()
api_key = os.getenv("API_KEY")

# configure gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    ad_text = request.form.get("ad_text")
    url = request.form.get("url")

    # Validate parameters
    if not ad_text or not url:
        return render_template("error.html", 
                               message="Missing add text or URL", 
                               code=400)
    
    # Send http request to fetch page
    try:
        response = requests.get(url,
                                {"User-Agent": "Mozilla/5.0"},
                                timeout=5)
        if response.status_code != 200:
            return render_template("error.html", 
                                   message="Failed to fetch page. Try another URL",
                                   code=response.status_code)
        
        # Get html 
        html = response.text        

        # extract key elements from html
        html = _extract_key_elements(html=html)

        return html
    except Exception as e:
        return render_template("error.html",
                               message=f"Error fetching page: {str(e)}",
                               code=403)
    
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

def rewrite_content(ad_text: str, headline: str, subheadline: str, cta: str):
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

    response = model.generate_content(prompt)
    return response.text