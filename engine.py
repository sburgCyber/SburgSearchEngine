from difflib import get_close_matches
import json
import math
import os
import re
from urllib.parse import quote

from flask import Flask, abort, jsonify, render_template, request, send_from_directory

app = Flask(__name__)

DATA_FOLDER = "data"
INDEX_FILE = "inverted_index.json"
WORD_COUNTS_FILE = "word_counts.json"
URL_MAP_FILE = os.path.join("sburg search engine", "url_map.json")

with open(INDEX_FILE, "r", encoding="utf-8") as f:
    INVERTED_INDEX = json.load(f)

with open(WORD_COUNTS_FILE, "r", encoding="utf-8") as f:
    WORD_COUNTS = json.load(f)

with open(URL_MAP_FILE, "r", encoding="utf-8") as f:
    SOURCE_URLS = json.load(f)

TOTAL_DOCS = len(WORD_COUNTS)
AI_CATEGORY_DOCUMENTS = frozenset({
    "Artificial intelligence.txt",
    "Data mining.txt",
    "Data science.txt",
    "Machine learning.txt",
    "Natural language processing.txt",
})
CATEGORIES = {"all", "ai"}

print(f"Loaded index with {len(INVERTED_INDEX)} unique words")
print(f"Total documents: {TOTAL_DOCS}")


def compute_tfidf(word, filename):
    """Compute TF-IDF for a word in a document."""
    word_freq = WORD_COUNTS.get(filename, {}).get(word, 0)
    total_words = sum(WORD_COUNTS.get(filename, {}).values())
    tf = word_freq / total_words if total_words > 0 else 0

    docs_with_word = len(INVERTED_INDEX.get(word, []))
    idf = math.log(TOTAL_DOCS / docs_with_word) if docs_with_word > 0 else 0
    return tf * idf


def highlight_words(text, words):
    """Wrap query words in <mark> tags for highlighting."""
    for word in words:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        text = pattern.sub(f"<mark>{word}</mark>", text)
    return text


def search(query, category="all"):
    """Search indexed documents, optionally limiting results to one category."""
    if category not in CATEGORIES:
        raise ValueError(f"Unknown search category: {category}")

    words = re.findall(r"\b[a-z]+\b", query.lower())
    category_documents = (
        AI_CATEGORY_DOCUMENTS & WORD_COUNTS.keys()
        if category == "ai"
        else None
    )

    if not words:
        if category_documents is None or query.strip():
            return []
        candidate_docs = set(category_documents)
    else:
        candidate_docs = set()
        for word in words:
            if word in INVERTED_INDEX:
                if not candidate_docs:
                    candidate_docs = set(INVERTED_INDEX[word])
                else:
                    candidate_docs &= set(INVERTED_INDEX[word])

        if not candidate_docs:
            for word in words:
                if word in INVERTED_INDEX:
                    candidate_docs.update(INVERTED_INDEX[word])

        if category_documents is not None:
            candidate_docs &= category_documents

    results = []
    for filename in candidate_docs:
        score = sum(compute_tfidf(word, filename) for word in words)
        snippet = highlight_words(generate_snippet(filename, words), words)
        results.append({
            "filename": filename,
            "url": SOURCE_URLS.get(
                filename,
                f"https://en.wikipedia.org/wiki/{quote(filename[:-4].replace(' ', '_'))}",
            ),
            "score": round(score, 6),
            "snippet": snippet,
        })

    results.sort(key=lambda result: (-result["score"], result["filename"].casefold()))
    return results


def generate_snippet(filename, words, snippet_length=200):
    """Extract a short snippet from a document around a matching word."""
    filepath = os.path.join(DATA_FOLDER, filename)
    if not os.path.exists(filepath):
        return ""

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lower_content = content.lower()
    positions = [lower_content.find(word) for word in words]
    positions = [position for position in positions if position != -1]
    if not positions:
        return content[:snippet_length] + "..."

    first_pos = min(positions)
    start = max(0, first_pos - 60)
    end = min(len(content), first_pos + snippet_length)
    snippet = content[start:end].replace("\n", " ").strip()

    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet += "..."
    return snippet


@app.route("/")
def index():
    """Front page with the search box."""
    return render_template("index.html")


@app.route("/search")
def search_results():
    """Render search results for the selected category."""
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "all").strip().lower()
    if category not in CATEGORIES:
        abort(400, description=f"Unknown search category: {category}")

    category_label = "AI" if category == "ai" else "All"
    if not query and category == "all":
        results = []
        message = "Please enter a search term."
    else:
        results = search(query, category)
        if query and results:
            category_context = " in AI" if category == "ai" else ""
            message = f"Found {len(results)} result(s){category_context} for '{query}'"
        elif query:
            category_context = " in AI" if category == "ai" else ""
            message = f"No results found{category_context} for '{query}'"
        elif results:
            message = f"Showing {len(results)} AI topic(s)"
        else:
            message = "No AI topics are available."

    return render_template(
        "results.html",
        query=query,
        category=category,
        category_label=category_label,
        results=results,
        message=message,
    )


@app.route("/suggest")
def suggest():
    """Return word suggestions for autocomplete."""
    query = request.args.get("q", "").strip().lower()
    if not query:
        return jsonify([])

    suggestions = [
        word for word in INVERTED_INDEX
        if word.startswith(query)
    ][:10]
    return jsonify(suggestions)


@app.route("/document/<path:filename>")
def view_document(filename):
    """Serve an indexed text document."""
    return send_from_directory(DATA_FOLDER, filename)


def suggest_correction(query):
    """Suggest a correction when a query has no exact results."""
    matches = get_close_matches(query.lower(), list(INVERTED_INDEX), n=1, cutoff=0.7)
    return matches[0] if matches else None


if __name__ == "__main__":
    app.run(debug=True, port=5000)
