import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def extract_sections_from_usga(url: str):
    """Fetches a public rules page and extracts section headings + paragraphs.

    This produces a structured JSON dataset with source URLs so the app can
    surface citations and users can verify wording at the source.
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    sections = []
    current_title = None
    current_text_parts = []

    for element in soup.find_all(["h2", "h3", "p"]):
        tag = element.name.lower()
        text = element.get_text(" ", strip=True)
        if not text:
            continue

        if tag in {"h2", "h3"}:
            if current_title and current_text_parts:
                sections.append(
                    {
                        "title": current_title,
                        "text": " ".join(current_text_parts).strip(),
                        "source": url,
                    }
                )
            current_title = text
            current_text_parts = []
        elif tag == "p":
            current_text_parts.append(text)

    if current_title and current_text_parts:
        sections.append(
            {
                "title": current_title,
                "text": " ".join(current_text_parts).strip(),
                "source": url,
            }
        )

    return sections


def main():
    project_root = Path(__file__).resolve().parents[1]
    output_file = project_root / "data" / "rules_dataset.json"

    # Add or replace with the exact USGA Rules pages you want to use.
    source_urls = [
        "https://www.usga.org/rules-hub.html"
    ]

    all_sections = []
    for url in source_urls:
        try:
            all_sections.extend(extract_sections_from_usga(url))
        except Exception as exc:
            print(f"Failed to parse {url}: {exc}")

    if not all_sections:
        print("No sections extracted. Keeping existing dataset unchanged.")
        return

    records = []
    for idx, section in enumerate(all_sections, start=1):
        records.append(
            {
                "id": f"USGA-{idx}",
                "title": section["title"],
                "text": section["text"],
                "keywords": [],
                "source": section["source"],
            }
        )

    output_file.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} sections to {output_file}")


if __name__ == "__main__":
    main()
