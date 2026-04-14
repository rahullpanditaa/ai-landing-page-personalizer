# Landing Page Personalizer

## Overview

AdAlign AI is a simple AI-powered system that personalizes landing pages based on ad creatives. It takes an ad and a landing page URL, extracts key content, and rewrites it to better align with the ad’s intent using an LLM.

The system demonstrates how AI can be applied to Conversion Rate Optimization (CRO) by improving messaging without changing page structure.

---

## Features

* Input ad creative (text or link)
* Fetch real landing pages
* Extract key elements:

  * Headline
  * Subheadline
  * Call-To-Action (CTA)
* AI-powered rewriting using Gemini
* Inject updated content back into the original HTML
* Render personalized version of the same page

---

## Tech Stack

* Backend: Flask
* Parsing: BeautifulSoup
* HTTP: Requests
* AI Model: Google Gemini (gemini-2.5-flash-lite)
* Deployment: Render

---

## How It Works

1. User inputs ad creative and landing page URL
2. System fetches raw HTML
3. Extracts key elements using rule-based parsing
4. Sends content + ad to LLM
5. Receives rewritten content (JSON)
6. Injects rewritten text back into HTML
7. Returns modified page

---

## Limitations

* Modern JS-heavy sites may not render perfectly
* Only static HTML is processed (no JS execution)
* Styling may break due to missing assets

---

## Running Locally

```bash
pip install -r requirements.txt
python app.py
```

Create a `.env` file:

```
GOOGLE_API_KEY=your_api_key_here
```

---

## Deployment

Deployed on Render.

Make sure to:

* Add `requirements.txt`
* Add `Procfile`: `web: gunicorn app:app`
* Set environment variables

---

## Example Usage

Ad:
"Start your free trial and grow your audience faster"

URL:
[https://convertkit.com/](https://convertkit.com/)

---

## Future Improvements

* Better DOM understanding
* Multimodal ad input (images/video)
* Headless browser rendering
* Side-by-side comparison UI

---