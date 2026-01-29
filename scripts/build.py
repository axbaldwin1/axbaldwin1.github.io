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

    # Build Finds
    finds_path = DATA_DIR / 'finds.json'
    if finds_path.exists():
        print('Processing Finds...')
        with open(finds_path, 'r', encoding='utf-8') as f:
            finds = json.load(f)

        find_cards = []
        for item in finds:
            metadata = fetch_metadata(item.get('url'))
            find_cards.append(generate_find_card(item, metadata))
            delay(0.5)

        finds_html = ''.join(find_cards)
        if update_html_file(ROOT_DIR / 'index.html', 'finds', finds_html):
            print(f"  Updated index.html with {len(finds)} finds\n")

    # Build Publications
    pubs_path = DATA_DIR / 'publications.json'
    if pubs_path.exists():
        print('Processing Publications...')
        with open(pubs_path, 'r', encoding='utf-8') as f:
            pubs = json.load(f)

        pub_cards = []
        for item in pubs:
            metadata = fetch_metadata(item.get('url'))
            pub_cards.append(generate_publication_card(item, metadata))
            delay(0.5)

        pubs_html = ''.join(pub_cards)
        if update_html_file(ROOT_DIR / 'publications.html', 'publications', pubs_html):
            print(f"  Updated publications.html with {len(pubs)} publications\n")

    # Build Projects
    projects_path = DATA_DIR / 'projects.json'
    if projects_path.exists():
        print('Processing Projects...')
        with open(projects_path, 'r', encoding='utf-8') as f:
            projects = json.load(f)

        project_cards = [generate_project_card(item) for item in projects]

        projects_html = ''.join(project_cards)
        if update_html_file(ROOT_DIR / 'projects.html', 'projects', projects_html):
            print(f"  Updated projects.html with {len(projects)} projects\n")

    # Build Writing
    writing_path = DATA_DIR / 'writing.json'
    if writing_path.exists():
        print('Processing Writing...')
        with open(writing_path, 'r', encoding='utf-8') as f:
            writing = json.load(f)

        # Sort by date, newest first
        writing.sort(key=lambda x: x.get('date', ''), reverse=True)

        writing_items = [generate_writing_item(item) for item in writing]

        writing_html = ''.join(writing_items)
        if update_html_file(ROOT_DIR / 'writing.html', 'writing', writing_html):
            print(f"  Updated writing.html with {len(writing)} posts\n")

    print('Build complete!')

if __name__ == '__main__':
    build()
