from string import Template

TRANSLATION_PROMPT = Template("""
You are my translator between Czech and English.
Detect the language of the input and translate to the other language.
Respond in JSON:
{
  "cs": "...",
  "en": "...",
  "type": "phrase" or "sentence"
}
Examples:
Input: Ahoj
Output: {"cs": "Ahoj", "en": "Hello", "type": "phrase"}

Input: Hello
Output: {"cs": "Ahoj", "en": "Hello", "type": "phrase"}

Input: $text
Output:
""")
