#!/usr/bin/env python3
"""Bundle Czech and English HTML stories into an EPUB.

Dependencies:
    pip3 install ebooklib beautifulsoup4 lxml
"""

import zipfile
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup, Tag
from ebooklib import epub

ROOT = Path(__file__).resolve().parent
CZECH_DIR = ROOT / "czech"
ENGLISH_DIR = ROOT / "english"
OUTPUT_FILE = ROOT / "Sylvis_stories.epub"

BOOK_TITLE = "Sylvi's stories"
BOOK_AUTHOR = "Sylvi Puzzlewell"
BOOK_LANGUAGE = "mul"
BOOK_ID = "sylvy-stories-2024"

# Dates to display under each story's title, keyed by lowercase title.
STORY_DATES = {
    "zlaté české ručičky": "April 24, 2021",
    "loud places": "November 16, 2019",
    "bitva na tursku": "March 13, 2025",
    "duchové minulosti ravu": "April 24, 2021",
    "můžeš prostě dělat věci": "November 15, 2024",
    "přístřeší": "April 10, 2026",
    "czech ingenuity": "April 24, 2021",
    "shelter": "April 10, 2026",
}


def parse_story(path: Path) -> tuple[str, str]:
    """Return (title, xhtml_body_content) for an HTML story file."""
    text = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "lxml")

    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else path.stem.replace("_", " ")

    date = STORY_DATES.get(title.strip().lower())
    if date and h1:
        sub = soup.new_tag("h2", attrs={"class": "date"})
        sub.string = date
        h1.insert_after(sub)

    body = soup.find("body")
    if body is None:
        body = soup

    # Render children as XML-compatible XHTML fragments.
    fragments = []
    for child in body.children:
        if isinstance(child, Tag):
            fragments.append(child.decode(formatter="minimal"))
        elif isinstance(child, str):
            fragments.append(child)

    return title, "".join(fragments)


def create_epub() -> None:
    book = epub.EpubBook()
    book.set_identifier(BOOK_ID)
    book.set_title(BOOK_TITLE)
    book.set_language(BOOK_LANGUAGE)
    book.add_author(BOOK_AUTHOR)

    # Title page
    title_page = epub.EpubHtml(
        title=BOOK_TITLE, file_name="title.xhtml", lang=BOOK_LANGUAGE
    )
    title_page.content = (
        f"<h1>{BOOK_TITLE}</h1>"
        f"<p style=\"text-align:center;\">by {BOOK_AUTHOR}</p>"
        "<p style=\"text-align:center;\">A collection of Czech stories and English translations</p>"
    )
    book.add_item(title_page)

    # Table of contents page (built after stories are collected)
    toc_page = epub.EpubHtml(
        title="Table of Contents", file_name="toc.xhtml", lang=BOOK_LANGUAGE
    )
    book.add_item(toc_page)

    # Shared stylesheet
    css = """\
body {
    font-family: Georgia, "Times New Roman", serif;
    line-height: 1.6;
    margin: 1em;
}
h1, h2, h3 {
    text-align: center;
}
h1 {
    text-transform: uppercase;
}
.section-title {
    text-align: center;
    margin-top: 40%;
}
h2.date {
    text-align: center;
    font-size: 1.1em;
    font-weight: normal;
    font-style: italic;
    margin-top: -0.3em;
}
"""
    style = epub.EpubItem(
        uid="style",
        file_name="style/style.css",
        media_type="text/css",
        content=css,
    )
    book.add_item(style)

    spine = [title_page, toc_page]
    toc_entries: list[tuple[epub.Section | epub.EpubHtml, list[epub.EpubHtml]]] = []
    story_index = 0

    def add_section(title: str, file_name: str) -> epub.EpubHtml:
        page = epub.EpubHtml(title=title, file_name=file_name, lang=BOOK_LANGUAGE)
        page.content = f'<h1 class="section-title">{title}</h1>'
        book.add_item(page)
        return page

    def add_stories(directory: Path, section_name: str, section_file: str) -> None:
        nonlocal story_index
        files = sorted(directory.glob("*.html"))
        if not files:
            return

        # Parse stories and sort by date within this section.
        stories = []
        for path in files:
            title, content = parse_story(path)
            date = STORY_DATES.get(title.strip().lower())
            sort_key = (
                datetime.strptime(date, "%B %d, %Y")
                if date
                else datetime.min
            )
            stories.append((sort_key, path, title, content, date))
        stories.sort(key=lambda item: item[0])

        section_page = add_section(section_name, section_file)
        spine.append(section_page)
        chapters: list[epub.EpubHtml] = []
        toc_entries.append((section_page, chapters))

        for _, path, title, content, date in stories:
            display_title = f"{title} — {date}" if date else title
            file_name = f"story_{story_index:03d}.xhtml"
            page = epub.EpubHtml(
                title=display_title, file_name=file_name, lang=BOOK_LANGUAGE
            )
            page.content = content
            page.add_link(href="style/style.css", rel="stylesheet", type="text/css")
            book.add_item(page)
            spine.append(page)
            chapters.append(page)
            story_index += 1

    add_stories(CZECH_DIR, "Czech Stories", "czech_section.xhtml")
    add_stories(ENGLISH_DIR, "English Translations", "english_section.xhtml")

    # Build the inline table of contents
    toc_html = ["<h1>Table of Contents</h1>"]
    for section, chapters in toc_entries:
        toc_html.append(f"<h2>{section.title}</h2>")
        toc_html.append("<ul>")
        for chapter in chapters:
            toc_html.append(
                f'<li><a href="{chapter.file_name}">{chapter.title}</a></li>'
            )
        toc_html.append("</ul>")
    toc_page.content = "\n".join(toc_html)

    book.toc = [(title_page, [toc_page])] + toc_entries
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = spine

    epub.write_epub(OUTPUT_FILE, book)

    # ebooklib emits dtb:depth="0" even though the navMap is nested.
    # Rewrite the NCX with the correct depth while preserving mimetype order.
    with zipfile.ZipFile(OUTPUT_FILE, "r") as zin:
        entries = [(name, zin.read(name)) for name in zin.namelist()]
    entries = [
        (
            name,
            data.replace(
                b'<meta content="0" name="dtb:depth"/>',
                b'<meta content="2" name="dtb:depth"/>',
            )
            if name == "EPUB/toc.ncx"
            else data,
        )
        for name, data in entries
    ]
    with zipfile.ZipFile(OUTPUT_FILE, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in entries:
            if name == "mimetype":
                info = zipfile.ZipInfo(name)
                zout.writestr(info, data, compress_type=zipfile.ZIP_STORED)
            else:
                zout.writestr(name, data)

    print(f"Created {OUTPUT_FILE}")


if __name__ == "__main__":
    create_epub()
