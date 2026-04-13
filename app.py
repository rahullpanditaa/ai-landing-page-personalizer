from flask import Flask, request, render_template

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
    
    return render_template("generated.html", ad_text=ad_text, url=url)