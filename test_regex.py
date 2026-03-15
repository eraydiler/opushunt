import re
tags = ['ios', 'c++', 'objective-c', 'c#', '.net']
texts = [
    "We need an iOS developer",
    "Welcome to our studios",
    "Looking for C++ expert",
    "Looking for C expert",
    "Looking for C# expert",
    "Experience in Objective-C is required",
    "ASP.NET developer needed"
]

for text in texts:
    print(f"\nText: {text}")
    for t in tags:
        pattern = r'(?<![a-zA-Z0-9_])' + re.escape(t) + r'(?![a-zA-Z0-9_])'
        match = re.search(pattern, text, re.IGNORECASE)
        # Handle start/end of string by testing
        # wait, lookbehind requires fixed width, but here we use single char class, so it's fine.
        # But if the word is at the START of the string, (?<!...) might fail if it doesn't match?
        # No, negative lookbehind (?<!...) succeeds if there is NO matching char before it. Start of string has NO char before it, so it succeeds!
        
        # Let's test
        print(f"  Tag '{t}': {bool(match)}")
