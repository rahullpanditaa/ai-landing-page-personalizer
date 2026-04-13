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

        # Return the html fetched
        return html
    except Exception as e:
        return render_template("error.html",
                               message=f"Error fetching page: {str(e)}",
                               code=403)

    return render_template("generated.html", ad_text=ad_text, url=url)