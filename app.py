from flask import Flask, request, render_template
import requests
import json

from lib.helpers import (
    _extract_key_elements, 
    _rewrite_content,
    _clean_and_parse)

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

        # extract content
        headline, subheadline, cta = _extract_key_elements(html=html)

        # rewrite using llm
        output = _rewrite_content(ad_text=ad_text, headline=headline,
                                  subheadline=subheadline, cta=cta)
        
        # parse jsoon
        try:
            parsed_json = _clean_and_parse(ai_output=output)
        except:
            parsed_json = {"raw_output": output}

        return f"""
        <h2>Original</h2>
        <p><strong>Headline:</strong> {headline}</p>
        <p><strong>Subheadline:</strong> {subheadline}</p>
        <p><strong>CTA:</strong> {cta}</p>
        
        <hr>
        
        <h2>AI personalized
        <pre>{parsed_json}</pre>"""

    except Exception as e:
        return render_template("error.html",
                               message=f"Error fetching page: {str(e)}",
                               code=403)
    

if __name__ == "__main__":
    app.run(debug=True)