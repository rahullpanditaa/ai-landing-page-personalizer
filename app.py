from bs4 import BeautifulSoup
from flask import Flask, request, render_template
import requests
import json

from lib.helpers import (
    _extract_key_elements_with_tags, 
    _rewrite_content,
    _clean_and_parse,
    _inject_ai_content)

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

        # extract content with tags
        soup, h_tag, sub_tag, cta_tag = _extract_key_elements_with_tags(html=html)

        # get original text for ai input
        headline = h_tag.get_text(strip=True) if h_tag else ""
        subheadline = sub_tag.get_text(strip=True) if sub_tag else ""
        cta = cta_tag.get_text(strip=True) if cta_tag else ""
        

        # rewrite using llm
        output = _rewrite_content(ad_text=ad_text, headline=headline,
                                  subheadline=subheadline, cta=cta)
        
        parsed_json = _clean_and_parse(ai_output=output)

        # inject back into html
        modified_html = _inject_ai_content(soup=soup, headline_tag=h_tag,
                                           sub_tag=sub_tag, cta_tag=cta_tag, 
                                           ai_data=parsed_json)
        
        return modified_html

    except Exception as e:
        return render_template("error.html",
                               message=f"Error fetching page: {str(e)}",
                               code=403)
    

if __name__ == "__main__":
    app.run(debug=True)