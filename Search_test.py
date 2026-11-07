import json

# Load the index
with open("inverted_index.json", 'r', encoding='utf-8') as f:
    index = json.load(f)

# Ask user for a word
query = input("🔍 Search for a word: ").strip().lower()

if query in index:
    print(f"✅ Found '{query}' in {len(index[query])} file(s):")
    for file in index[query]:
        print(f"   - {file}")
else:
    print(f"❌ '{query}' not found in any document.")
