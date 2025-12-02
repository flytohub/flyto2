#!/usr/bin/env python3
"""
Translate Chinese markdown to English using Ollama
"""
import os
import sys
import re
import requests
from pathlib import Path

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2"  # For translation


def translate_chunk(text: str) -> str:
    """Translate a chunk of text to English"""
    if not text.strip():
        return text

    # Skip if already mostly English
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    if chinese_chars < 10:
        return text

    prompt = f"""Translate the following technical documentation from Chinese to English.
Keep all code blocks, YAML, and markdown formatting intact.
Only translate the Chinese text, do not modify any code or technical terms.

TEXT TO TRANSLATE:
{text}

ENGLISH TRANSLATION:"""

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3}
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text


def split_by_sections(content: str) -> list:
    """Split content by ## headers"""
    sections = []
    current = []

    for line in content.split('\n'):
        if line.startswith('## ') and current:
            sections.append('\n'.join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        sections.append('\n'.join(current))

    return sections


def main():
    input_file = Path("IMPLEMENTATION_GUIDE_V4.md")
    output_file = Path("IMPLEMENTATION_GUIDE_V4_EN.md")

    if not input_file.exists():
        print(f"ERROR: {input_file} not found")
        return 1

    print("=" * 70)
    print("Translating IMPLEMENTATION_GUIDE_V4.md to English")
    print("=" * 70)

    content = input_file.read_text(encoding='utf-8')
    sections = split_by_sections(content)

    print(f"Found {len(sections)} sections to translate")

    translated_sections = []

    for i, section in enumerate(sections, 1):
        # Get section title for progress
        lines = section.split('\n')
        title = next((l for l in lines if l.startswith('#')), f"Section {i}")[:50]

        print(f"[{i}/{len(sections)}] Translating: {title}...")

        translated = translate_chunk(section)
        translated_sections.append(translated)

    # Combine and save
    final_content = '\n'.join(translated_sections)
    output_file.write_text(final_content, encoding='utf-8')

    print(f"\n{'=' * 70}")
    print(f"DONE: Saved to {output_file}")
    print(f"{'=' * 70}")

    return 0


if __name__ == "__main__":
    sys.exit(main())