from bs4 import BeautifulSoup
from flask import Flask, request, render_template
import requests

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
    subheading = ""
    paragraphs = soup.find_all("p")

    for p in paragraphs:
        text = p.get_text(strip=True)
        if text and len(text) > 30:
            subheading = text
            break

    # extract the CTA
    buttons = soup.find_all(["button", "a"])

    cta_text = "Click here"
    for btn in buttons:
        # if nav elems present, skip
        if btn.find_parent("nav"):
            continue

        text = btn.get_text(strip=True)
        if (any(word in text.lower() for word in ["get", 
                                                  "start", "try", 
                                                  "sign up", "buy", 
                                                  "free", "demo", "join"]) 
                                                  and 2 <= len(text) <= 25
                                                  and "login" not in text.lower()
                                                  and "sign in" not in text.lower()):
            cta_text = text
            break

    # return temp html
    return f"""
    <h3>Extracted content</h3>
    <p><strong>Headline:</strong> {headline}</p>
    <p><strong>Subheadline:</strong> {subheading}</p>
    <p><strong>CTA:</strong> {cta_text}</p>"""