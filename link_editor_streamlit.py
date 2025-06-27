
import streamlit as st
import json
from docx import Document
from difflib import get_close_matches
import yake

# Load article
doc = Document("The Role of AI in Modern Content Marketing.docx")
article_text = "".join([p.text for p in doc.paragraphs if p.text.strip()])

# Extract keywords using YAKE
kw_extractor = yake.KeywordExtractor(lan="en", n=3, top=15, dedupLim=0.9)
keywords = kw_extractor.extract_keywords(article_text)
anchor_phrases = [kw for kw, _ in keywords]

# Load site index
with open("site_content_index.json", "r", encoding="utf-8") as f:
    site_index = json.load(f)

def find_matches(phrase):
    options = []
    for page in site_index:
        if phrase.lower() in page["title"].lower():
            options.append((page["title"], page["url"]))
        elif any(phrase.lower() in h.lower() for h in page.get("h1", [])):
            options.append((page["title"], page["url"]))
    if not options:
        for page in site_index:
            if get_close_matches(phrase.lower(), [page["title"].lower()]):
                options.append((page["title"], page["url"]))
    return options[:3]

st.title("🔗 Internal Link Suggestion Review")

final_links = {}

for phrase in anchor_phrases:
    st.markdown(f"### 🔍 Anchor Phrase: `{phrase}`")
    suggestions = find_matches(phrase)
    if suggestions:
        options = ["Reject"] + [f"{title} ({url})" for title, url in suggestions]
        selected = st.radio("Select a link:", options, key=phrase)
        if selected != "Reject":
            final_links[phrase] = suggestions[options.index(selected) - 1]
    else:
        st.warning("No good match found.")

if st.button("Generate Final HTML"):
    html_output = article_text
    for phrase, (title, url) in final_links.items():
        linked = f'<a href="{url}" title="{title}">{phrase}</a>'
        html_output = html_output.replace(phrase, linked, 1)
    st.success("✅ Final HTML Generated!")
    st.download_button("Download HTML", data=html_output, file_name="linked_article.html", mime="text/html")
    st.code(html_output, language="html")
