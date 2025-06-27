import streamlit as st
import json
from difflib import get_close_matches

# Load article text
with open("The Role of AI in Modern Content Marketing.docx", "rb") as f:
    import docx
    doc = docx.Document(f)
    article_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

import yake 

kw_extractor = yake.KeywordExtractor(lan="en", n=3, top=15, dedupLim=0.9)
keywords = kw_extractor.extract_keywords(article_text)

anchor_phrases = [kw for kw, _ in keywords]


# Load anchor phrases and matches (Step 5 output)
anchor_phrases = [kw for kw, _ in keywords] 

with open("site_content_index.json", "r", encoding="utf-8") as f:
    site_index = json.load(f)

# Match engine (simplified)
def find_matches(phrase):
    options = []
    for page in site_index:
        if phrase.lower() in page["title"].lower():
            options.append((page["title"], page["url"]))
        elif any(phrase.lower() in h.lower() for h in page.get("h1", [])):
            options.append((page["title"], page["url"]))
    if not options:
        # Fallback to fuzzy matching
        for page in site_index:
            if get_close_matches(phrase.lower(), [page["title"].lower()]):
                options.append((page["title"], page["url"]))
    return options[:3]  # top 3 matches

# Store approved links
final_links = {}

st.title("🔗 AI-Powered Link Suggestion Review")
st.markdown("Review suggested anchor links for your article. Approve, reject, or customize them.")

# Highlight and review each phrase
for phrase in anchor_phrases:
    st.markdown(f"### 🔍 Phrase: `{phrase}`")
    suggestions = find_matches(phrase)

    if suggestions:
        titles = [f"{title} ({url})" for title, url in suggestions]
        choice = st.radio(f"Suggested link for '{phrase}':", ["Reject"] + titles, key=phrase)
        if choice != "Reject":
            selected = suggestions[titles.index(choice) - 1]
            final_links[phrase] = selected
    else:
        st.markdown("_No match found._")

# Generate Final HTML with inserted links
if st.button("Generate Final HTML"):
    html_output = article_text
    for phrase, (title, url) in final_links.items():
        linked = f'<a href="{url}" title="{title}">{phrase}</a>'
        html_output = html_output.replace(phrase, linked, 1)

    st.success("✅ Final HTML Generated!")
    st.download_button("Download HTML", data=html_output, file_name="linked_article.html", mime="text/html")
    st.code(html_output, language="html")
