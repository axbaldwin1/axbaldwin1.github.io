#!/usr/bin/env python3
"""
Build script for Alex Baldwin's personal website

Reads content from _data/*.json files, fetches metadata for URLs,
and generates the HTML sections for the site.

Usage: python3 scripts/build.py
"""

import json
import os
import re
import ssl
import time
import urllib.request
import urllib.error
from html import escape, unescape
from pathlib import Path

# Fix SSL certificate verification on macOS
ssl._create_default_https_context = ssl._create_unverified_context

# Configuration
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
DATA_DIR = ROOT_DIR / '_data'
WRITINGS_DIR = DATA_DIR / 'writings'
WRITING_OUTPUT_DIR = ROOT_DIR / 'writing'
WRITING_TEMPLATE = WRITING_OUTPUT_DIR / '_template.html'

def delay(seconds):
    """Rate limiting delay."""
    time.sleep(seconds)

def fetch_metadata(url):
    """Fetch Open Graph metadata from a URL."""
    if not url:
        return {}

    try:
        print(f"  Fetching: {url}")

        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; MetadataBot/1.0)',
                'Accept': 'text/html,application/xhtml+xml'
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')

        metadata = {}

        # OG Title
        og_title = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']', html, re.I)
        if not og_title:
            og_title = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:title["\']', html, re.I)
        if og_title:
            metadata['title'] = unescape(og_title.group(1))

        # Fallback to title tag
        if 'title' not in metadata:
            title_tag = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
            if title_tag:
                metadata['title'] = unescape(title_tag.group(1).strip())

        # OG Description
        og_desc = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']', html, re.I)
        if not og_desc:
            og_desc = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:description["\']', html, re.I)
        if og_desc:
            metadata['description'] = unescape(og_desc.group(1))

        # Fallback to meta description
        if 'description' not in metadata:
            meta_desc = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', html, re.I)
            if not meta_desc:
                meta_desc = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']description["\']', html, re.I)
            if meta_desc:
                metadata['description'] = unescape(meta_desc.group(1))

        # OG Image
        og_image = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html, re.I)
        if not og_image:
            og_image = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', html, re.I)
        if og_image:
            image_url = og_image.group(1)
            # Handle relative URLs
            if image_url.startswith('/'):
                from urllib.parse import urlparse
                parsed = urlparse(url)
                image_url = f"{parsed.scheme}://{parsed.netloc}{image_url}"
            metadata['image'] = image_url

        # OG Site Name
        og_site = re.search(r'<meta[^>]*property=["\']og:site_name["\'][^>]*content=["\']([^"\']+)["\']', html, re.I)
        if og_site:
            metadata['site_name'] = unescape(og_site.group(1))

        # YouTube specific: get thumbnail
        if 'youtube.com/watch' in url or 'youtu.be' in url:
            video_id = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]+)', url)
            if video_id:
                metadata['image'] = f"https://img.youtube.com/vi/{video_id.group(1)}/maxresdefault.jpg"

        print(f"    Found: \"{metadata.get('title', '(no title)')}\"")
        return metadata

    except Exception as e:
        print(f"    Error: {e}")
        return {}

def escape_html(s):
    """Escape HTML special characters."""
    if not s:
        return ''
    return escape(str(s))

def capitalize(s):
    """Capitalize first letter."""
    return s[0].upper() + s[1:] if s else ''

def generate_find_card(item, metadata):
    """Generate HTML for a Find card."""
    title = escape_html(item.get('title') or metadata.get('title') or 'Untitled')
    description = escape_html(item.get('notes') or metadata.get('description') or '')
    image = item.get('image') or metadata.get('image')
    category = item.get('category', 'link')
    size = item.get('size', 'small')
    url = item.get('url', '#')

    # Quote cards are special
    if category == 'quote':
        return f'''
          <article class="masonry__item" data-category="quote">
            <div class="masonry__content">
              <span class="masonry__category masonry__category--quote">Quote</span>
              <blockquote class="masonry__quote">"{escape_html(item.get('quote', ''))}"</blockquote>
              <p class="masonry__description">— {escape_html(item.get('author', ''))}{'. ' + escape_html(item.get('notes', '')) if item.get('notes') else ''}</p>
            </div>
          </article>'''

    size_class = ' masonry__item--large' if size == 'large' else ' masonry__item--medium' if size == 'medium' else ''

    image_html = f'''
            <div class="masonry__image">
              <img src="{escape_html(image)}" alt="{title}" loading="lazy">
            </div>''' if image else ''

    return f'''
          <article class="masonry__item{size_class}" data-category="{category}">
            {image_html}
            <div class="masonry__content">
              <span class="masonry__category masonry__category--{category}">{capitalize(category)}</span>
              <h3 class="masonry__title"><a href="{escape_html(url)}" target="_blank" rel="noopener">{title}</a></h3>
              <p class="masonry__description">{description}</p>
            </div>
          </article>'''

def generate_publication_card(item, metadata):
    """Generate HTML for a Publication card."""
    title = escape_html(item.get('title') or metadata.get('title') or 'Untitled')
    authors = ', '.join(item.get('authors', []))
    venue = escape_html(item.get('venue') or metadata.get('site_name') or '')
    year = item.get('year', '')
    pub_type = item.get('type', 'journal')
    image = item.get('image') or metadata.get('image') or get_default_publication_image(pub_type)
    url = item.get('url', '#')

    return f'''
        <article class="uniform-card">
          <div class="uniform-card__image">
            <img src="{escape_html(image)}" alt="{title}" loading="lazy">
          </div>
          <div class="uniform-card__content">
            <span class="uniform-card__tag uniform-card__tag--publication">{capitalize(pub_type)}</span>
            <h3 class="uniform-card__title">
              <a href="{escape_html(url)}" target="_blank" rel="noopener">{title}</a>
            </h3>
            <p class="uniform-card__description">{escape_html(authors)}</p>
            <span class="uniform-card__meta">{venue}{', ' + str(year) if year else ''}</span>
            {f'''
            <div class="uniform-card__links">
              <a href="{escape_html(url)}" class="uniform-card__link" target="_blank" rel="noopener">View</a>
            </div>''' if url != '#' else ''}
          </div>
        </article>'''

def generate_project_card(item):
    """Generate HTML for a Project card."""
    title = escape_html(item.get('title', 'Untitled Project'))
    description = escape_html(item.get('description', ''))
    status = item.get('status', 'active')
    tech = item.get('tech', [])
    image = item.get('image') or get_default_project_image()
    url = item.get('url', '#')

    status_class = 'uniform-card__tag--active' if status == 'active' else 'uniform-card__tag--completed'

    return f'''
        <article class="uniform-card">
          <div class="uniform-card__image">
            <img src="{escape_html(image)}" alt="{title}" loading="lazy">
          </div>
          <div class="uniform-card__content">
            <span class="uniform-card__tag {status_class}">{capitalize(status)}</span>
            <h3 class="uniform-card__title">
              <a href="{escape_html(url)}" target="_blank" rel="noopener">{title}</a>
            </h3>
            <p class="uniform-card__description">{description}</p>
            <span class="uniform-card__meta">{', '.join(tech)}</span>
            {f'''
            <div class="uniform-card__links">
              <a href="{escape_html(url)}" class="uniform-card__link" target="_blank" rel="noopener">View</a>
            </div>''' if url != '#' else ''}
          </div>
        </article>'''

def get_default_publication_image(pub_type):
    """Get default image for publication type."""
    images = {
        'journal': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400&q=80',
        'conference': 'https://images.unsplash.com/photo-1517976487492-5750f3195933?w=400&q=80',
        'thesis': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400&q=80',
        'preprint': 'https://images.unsplash.com/photo-1518152006812-edab29b069ac?w=400&q=80',
        'workshop': 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&q=80'
    }
    return images.get(pub_type, images['journal'])

def get_default_project_image():
    """Get default image for project."""
    import random
    images = [
        'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80',
        'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80',
        'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80'
    ]
    return random.choice(images)

def format_date(date_str):
    """Format date string for display."""
    from datetime import datetime
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.strftime('%B %d, %Y'), date.strftime('%B %Y')
    except:
        return date_str, date_str

def generate_writing_item(item):
    """Generate HTML for a Writing list item."""
    title = escape_html(item.get('title', 'Untitled'))
    slug = item.get('slug', '')
    date_str = item.get('date', '')
    _, short_date = format_date(date_str)
    url = f"/writing/{slug}.html" if slug else '#'

    return f'''
          <li class="list__item">
            <a href="{url}" class="list__link">
              <span class="list__title">{title}</span>
              <span class="list__meta">{short_date}</span>
            </a>
          </li>'''


# --- Markdown Processing ---

def markdown_to_html(markdown):
    """Convert Markdown to HTML (handles common formatting for prose)."""
    text = markdown

    # Normalize line endings
    text = text.replace('\r\n', '\n')

    # Escape HTML entities first
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # Restore blockquotes (we escaped the >)
    text = re.sub(r'^&gt;\s?(.*)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    # Merge consecutive blockquotes
    text = text.replace('</blockquote>\n<blockquote>', '\n')

    # Headers
    text = re.sub(r'^######\s+(.*)$', r'<h6>\1</h6>', text, flags=re.MULTILINE)
    text = re.sub(r'^#####\s+(.*)$', r'<h5>\1</h5>', text, flags=re.MULTILINE)
    text = re.sub(r'^####\s+(.*)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^###\s+(.*)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s+(.*)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^#\s+(.*)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)

    # Horizontal rules
    text = re.sub(r'^(\*{3,}|-{3,}|_{3,})$', r'<hr>', text, flags=re.MULTILINE)

    # Bold and italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'___(.+?)___', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)

    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # Links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

    # Unordered lists
    text = re.sub(r'^[\*\-]\s+(.*)$', r'<li>\1</li>', text, flags=re.MULTILINE)

    # Wrap consecutive <li> in <ul>
    def wrap_lists(match):
        return '<ul>\n' + match.group(0) + '</ul>\n'
    text = re.sub(r'(<li>.*</li>\n?)+', wrap_lists, text)

    # Paragraphs: wrap text blocks
    blocks = text.split('\n\n')
    result = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # Skip if already an HTML block element
        if re.match(r'^<(h[1-6]|ul|ol|li|blockquote|pre|hr|div|p)', block):
            result.append(block)
        else:
            # Wrap in paragraph, convert single newlines to <br>
            result.append('<p>' + block.replace('\n', '<br>') + '</p>')

    return '\n\n'.join(result)


def parse_writing_markdown(content):
    """Parse a writing markdown file.
    Format: First # header = title, Second # header = date, rest = content
    """
    lines = content.split('\n')
    title = ''
    date = ''
    content_start_index = 0
    headers_found = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        match = re.match(r'^#\s+(.+)$', stripped)
        if match:
            headers_found += 1
            if headers_found == 1:
                title = match.group(1)
            elif headers_found == 2:
                date = match.group(1)
                content_start_index = i + 1
                break

    # Get content after the two headers
    content_lines = lines[content_start_index:]
    content_markdown = '\n'.join(content_lines).strip()
    content_html = markdown_to_html(content_markdown)

    return {'title': title, 'date': date, 'content': content_html}


def slugify(text):
    """Generate URL-friendly slug from text."""
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def generate_writing_list_item(title, date, slug):
    """Generate HTML for a writing list item from markdown."""
    return f'''
          <li class="list__item">
            <a href="/writing/{slug}.html" class="list__link">
              <span class="list__title">{escape_html(title)}</span>
              <span class="list__meta">{escape_html(date)}</span>
            </a>
          </li>'''


def generate_writing_masonry_card(title, date, slug, excerpt=''):
    """Generate masonry card HTML for a writing."""
    return f'''
          <article class="masonry__item" data-category="writing">
            <div class="masonry__content">
              <span class="masonry__category masonry__category--writing">My Writing</span>
              <h3 class="masonry__title"><a href="/writing/{slug}.html">{escape_html(title)}</a></h3>
              <p class="masonry__description">{escape_html(excerpt) if excerpt else escape_html(date)}</p>
            </div>
          </article>'''


def generate_publication_masonry_card(item, metadata):
    """Generate masonry card HTML for a publication."""
    title = escape_html(item.get('title') or metadata.get('title') or 'Untitled')
    authors = ', '.join(item.get('authors', []))
    venue = item.get('venue') or metadata.get('site_name') or ''
    year = item.get('year', '')
    url = item.get('url', '#')
    image = item.get('image') or metadata.get('image')

    meta_parts = []
    if venue:
        meta_parts.append(escape_html(venue))
    if year:
        meta_parts.append(str(year))
    meta = ', '.join(meta_parts)

    image_html = f'''
            <div class="masonry__image">
              <img src="{escape_html(image)}" alt="{title}" loading="lazy">
            </div>''' if image else ''

    return f'''
          <article class="masonry__item" data-category="publication">
            {image_html}
            <div class="masonry__content">
              <span class="masonry__category masonry__category--publication">My Publication</span>
              <h3 class="masonry__title"><a href="{escape_html(url)}" target="_blank" rel="noopener">{title}</a></h3>
              <p class="masonry__description">{escape_html(authors)}</p>
              {f'<p class="masonry__meta">{meta}</p>' if meta else ''}
            </div>
          </article>'''


def generate_project_masonry_card(item):
    """Generate masonry card HTML for a project."""
    title = escape_html(item.get('title', 'Untitled Project'))
    description = escape_html(item.get('description', ''))
    tech = item.get('tech', [])
    url = item.get('url', '#')
    image = item.get('image')

    image_html = f'''
            <div class="masonry__image">
              <img src="{escape_html(image)}" alt="{title}" loading="lazy">
            </div>''' if image else ''

    return f'''
          <article class="masonry__item masonry__item--medium" data-category="project">
            {image_html}
            <div class="masonry__content">
              <span class="masonry__category masonry__category--project">My Project</span>
              <h3 class="masonry__title"><a href="{escape_html(url)}" target="_blank" rel="noopener">{title}</a></h3>
              <p class="masonry__description">{description}</p>
              {f'<p class="masonry__meta">{", ".join(tech)}</p>' if tech else ''}
            </div>
          </article>'''


def parse_date_for_sort(date_str):
    """Parse date string for sorting."""
    from datetime import datetime
    months = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    # "January 15, 2026" or "January 2026"
    match = re.search(r'(\w+)\s*(\d+)?,?\s*(\d{4})', date_str.lower())
    if match:
        month = months.get(match.group(1), 1)
        day = int(match.group(2)) if match.group(2) else 1
        year = int(match.group(3))
        return datetime(year, month, day)

    # Fallback
    return datetime(1970, 1, 1)

def update_html_file(filepath, marker, content):
    """Update HTML file with generated content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    begin_marker = f'<!-- BEGIN:{marker} -->'
    end_marker = f'<!-- END:{marker} -->'

    begin_index = html.find(begin_marker)
    end_index = html.find(end_marker)

    if begin_index == -1 or end_index == -1:
        print(f"  Warning: Markers not found for {marker} in {filepath}")
        return False

    before = html[:begin_index + len(begin_marker)]
    after = html[end_index:]

    html = before + '\n' + content + '\n        ' + after

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    return True

def build():
    """Main build function."""
    print('Building site...\n')

    # Collect all masonry cards for the combined finds grid
    all_masonry_cards = []

    # Process Finds
    finds_path = DATA_DIR / 'finds.json'
    finds_count = 0
    if finds_path.exists():
        print('Processing Finds...')
        with open(finds_path, 'r', encoding='utf-8') as f:
            finds = json.load(f)

        for item in finds:
            metadata = fetch_metadata(item.get('url'))
            all_masonry_cards.append(generate_find_card(item, metadata))
            delay(0.5)
        finds_count = len(finds)
        print(f"  Processed {finds_count} finds\n")

    # Process Publications
    pubs_path = DATA_DIR / 'publications.json'
    pubs_count = 0
    if pubs_path.exists():
        print('Processing Publications...')
        with open(pubs_path, 'r', encoding='utf-8') as f:
            pubs = json.load(f)

        pub_page_cards = []
        for item in pubs:
            metadata = fetch_metadata(item.get('url'))
            # Add to masonry grid
            all_masonry_cards.append(generate_publication_masonry_card(item, metadata))
            # Add to publications page
            pub_page_cards.append(generate_publication_card(item, metadata))
            delay(0.5)

        pubs_html = ''.join(pub_page_cards)
        if update_html_file(ROOT_DIR / 'publications.html', 'publications', pubs_html):
            print(f"  Updated publications.html with {len(pubs)} publications\n")
        pubs_count = len(pubs)

    # Process Projects
    projects_path = DATA_DIR / 'projects.json'
    projects_count = 0
    if projects_path.exists():
        print('Processing Projects...')
        with open(projects_path, 'r', encoding='utf-8') as f:
            projects = json.load(f)

        project_page_cards = []
        for item in projects:
            # Add to masonry grid
            all_masonry_cards.append(generate_project_masonry_card(item))
            # Add to projects page
            project_page_cards.append(generate_project_card(item))

        projects_html = ''.join(project_page_cards)
        if update_html_file(ROOT_DIR / 'projects.html', 'projects', projects_html):
            print(f"  Updated projects.html with {len(projects)} projects\n")
        projects_count = len(projects)

    # Process Writings from Markdown files
    writings_count = 0
    if WRITINGS_DIR.exists() and WRITING_TEMPLATE.exists():
        print('Processing Writings...')
        with open(WRITING_TEMPLATE, 'r', encoding='utf-8') as f:
            template = f.read()

        md_files = list(WRITINGS_DIR.glob('*.md'))

        if md_files:
            writings = []

            for md_file in md_files:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                parsed = parse_writing_markdown(content)

                if not parsed['title']:
                    print(f"  Warning: No title found in {md_file.name}, skipping")
                    continue

                slug = slugify(parsed['title'])
                print(f"  Processing: {parsed['title']}")

                # Generate the individual writing page
                page_html = template.replace('POST_TITLE', escape_html(parsed['title']))
                page_html = page_html.replace('POST_DATE', escape_html(parsed['date']))
                page_html = page_html.replace('POST_DESCRIPTION', escape_html(parsed['title']))

                # Replace the content placeholder
                page_html = re.sub(
                    r'<!-- Your content here -->\s*<p>\s*Start writing\.\.\.\s*</p>',
                    parsed['content'],
                    page_html
                )

                # Write the page
                output_path = WRITING_OUTPUT_DIR / f'{slug}.html'
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(page_html)

                # Extract first paragraph as excerpt (strip HTML tags)
                excerpt_match = re.search(r'<p>(.+?)</p>', parsed['content'], re.DOTALL)
                excerpt = ''
                if excerpt_match:
                    excerpt = re.sub(r'<[^>]+>', '', excerpt_match.group(1))[:150]
                    if len(excerpt_match.group(1)) > 150:
                        excerpt += '...'

                writings.append({
                    'title': parsed['title'],
                    'date': parsed['date'],
                    'slug': slug,
                    'excerpt': excerpt,
                    'sort_date': parse_date_for_sort(parsed['date'])
                })

                # Add to masonry grid
                all_masonry_cards.append(generate_writing_masonry_card(
                    parsed['title'], parsed['date'], slug, excerpt
                ))

            # Sort writings by date (newest first)
            writings.sort(key=lambda w: w['sort_date'], reverse=True)

            # Generate the list HTML for writing.html
            list_html = ''.join(
                generate_writing_list_item(w['title'], w['date'], w['slug'])
                for w in writings
            )

            if update_html_file(ROOT_DIR / 'writing.html', 'writing', list_html):
                print(f'  Updated writing.html with {len(writings)} writings\n')
            writings_count = len(writings)
        else:
            print('  No .md files found in _data/writings/\n')
    elif not WRITINGS_DIR.exists():
        print(f'  Writings directory not found: {WRITINGS_DIR}\n')

    # Update the combined finds grid on index.html
    if all_masonry_cards:
        finds_html = ''.join(all_masonry_cards)
        if update_html_file(ROOT_DIR / 'index.html', 'finds', finds_html):
            total = finds_count + pubs_count + projects_count + writings_count
            print(f'Updated index.html with {total} total items')
            print(f'  ({finds_count} finds, {pubs_count} publications, {projects_count} projects, {writings_count} writings)\n')

    print('Build complete!')

if __name__ == '__main__':
    build()
