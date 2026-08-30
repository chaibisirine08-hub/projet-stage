import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_names(description):
    """
    Generates 10 creative domain brand name candidates using Gemini.
    """
    prompt = f"""
You are an expert brand-name generator for websites and tech startups.

The user wants a domain name for this project:
"{description}"

Generate 10 creative, highly original, and modern brand-name candidates suitable for a website.

CRITICAL RULES FOR RELEVANCE AND QUALITY:
- RELEVANCE TO DESCRIPTION: The generated names MUST strongly align with the core concept, sector, themes, and keywords of the user's description: "{description}". They must evoke the right industry, feeling, and context.
- BRANDABLE WORDS: Invent new, creative brandable words. You can blend syllables, create portmanteaus, or use evocative sounds, but they must be clearly reminiscent of the business idea.
- Avoid generic dictionary words.
- Do not use spaces.
- Do not use hyphens.
- Use only letters (a-z).
- Keep each name between 5 and 14 letters.
- Make each name easy to pronounce.
- Do NOT include .com, .net, or any other domain extension.
- Each name must be completely unique.
- Return ONLY the names.
- Put exactly one name on each line.
- Do NOT include numbers, bullet points, introduction, or explanations.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        text = response.text
        if not text:
            print("Gemini returned empty response text.")
            return []

        names = []

        for line in text.splitlines():
            name = line.strip()
            if not name:
                continue

            # Remove bullet points (- or *) or numbering (1. or 1-)
            if name.startswith("- ") or name.startswith("* "):
                name = name[2:].strip()
            
            if "." in name[:4]:
                name = name.split(".", 1)[1].strip()
                
            if "-" in name[:4]:
                name = name.split("-", 1)[1].strip()

            # Remove accidental domain extensions
            for ext in [".com", ".net", ".org", ".ma", ".io", ".ai", ".fr", ".co"]:
                name = name.replace(ext, "")

            # Remove spaces, hyphens, and punctuation
            name = "".join(char for char in name if char.isalnum())
            name = name.replace(" ", "")

            # Keep only letters
            if name.isalpha():
                name = name.lower()
                # Keep names between 4 and 15 characters for good flexibility
                if 4 <= len(name) <= 15:
                    names.append(name)

        # Remove duplicates while preserving order
        names = list(dict.fromkeys(names))

        print("GEMINI GENERATED NAMES:", names)

        # Ensure we return at least a subset or fallback
        return names[:10]

    except Exception as e:
        print(f"Gemini generation error: {e}")
        return []