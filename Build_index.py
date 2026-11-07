import os
import json
import re
from collections import defaultdict

# ============================================
# SETUP
# ============================================
DATA_FOLDER = "data"           # Folder where your .txt files are
INDEX_FILE = "inverted_index.json"   # Where to save the index
STOP_WORDS = {"the", "a", "an", "of", "to", "for", "on", "at", "in", "with", "by"}  # Maneno yasiyo na maana

# ============================================
# STEP 1: Read all text files
# ============================================
def read_all_files():
    """
    Reads all .txt files in the data folder.
    Returns a dictionary: {filename: content}
    """
    documents = {}
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".txt"):
            filepath = os.path.join(DATA_FOLDER, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            documents[filename] = content
    return documents

# ============================================
# STEP 2: Tokenization (split into words)
# ============================================
def tokenize(text):
    """
    Splits text into lowercase words, removes punctuation and stop words.
    Returns a list of words.
    """
    # Convert to lowercase and split by non-alphabetic characters
    words = re.findall(r'\b[a-z]+\b', text.lower())
    # Remove stop words
    words = [w for w in words if w not in STOP_WORDS]
    return words

# ============================================
# STEP 3: Build Inverted Index
# ============================================
def build_inverted_index(documents):
    """
    Creates an inverted index: {word: [filename1, filename2, ...]}
    Also counts word frequency per document for TF-IDF later.
    """
    index = defaultdict(set)   # Use set to avoid duplicate filenames
    word_counts = {}           # Optional: for TF-IDF

    for filename, content in documents.items():
        words = tokenize(content)
        # Count frequency per document (for TF)
        word_counts[filename] = {}
        for word in words:
            word_counts[filename][word] = word_counts[filename].get(word, 0) + 1
            index[word].add(filename)

    # Convert sets to lists for JSON serialization
    index = {word: list(files) for word, files in index.items()}
    return index, word_counts

# ============================================
# STEP 4: Save Index to JSON
# ============================================
def save_index(index, filename=INDEX_FILE):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=4)
    print(f"✅ Index saved to {filename}")

# ============================================
# MAIN
# ============================================
def main():
    print("📖 Reading documents from 'data/' folder...")
    documents = read_all_files()
    print(f"📄 Found {len(documents)} text files.")

    if not documents:
        print("❌ No .txt files found. Run the crawler first.")
        return

    print("🔨 Building inverted index...")
    index, word_counts = build_inverted_index(documents)
    print(f"📊 Index built with {len(index)} unique words.")

    # Save index
    save_index(index)

    # Optional: Save word counts too for TF-IDF later
    with open("word_counts.json", 'w', encoding='utf-8') as f:
        json.dump(word_counts, f, indent=4)
    print("✅ Word counts saved to word_counts.json")

    # Show a small sample
    print("\n--- SAMPLE OF INDEX (first 5 words) ---")
    sample_words = list(index.keys())[:5]
    for word in sample_words:
        print(f"  {word}: {index[word]}")

    print("\n🎉 Done! You can now search using the index.")

if __name__ == "__main__":
    main()