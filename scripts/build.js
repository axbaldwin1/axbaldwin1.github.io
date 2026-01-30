#!/usr/bin/env node

/**
 * Build script for Alex Baldwin's personal website
 *
 * Reads content from _data/*.json files, fetches metadata for URLs,
 * and generates the HTML sections for the site.
 *
 * Usage: node scripts/build.js
 */

const fs = require('fs');
const path = require('path');

// Configuration
const DATA_DIR = path.join(__dirname, '..', '_data');
const OUTPUT_DIR = path.join(__dirname, '..');
const WRITINGS_DIR = path.join(DATA_DIR, 'writings');
const WRITING_OUTPUT_DIR = path.join(OUTPUT_DIR, 'writing');
const WRITING_TEMPLATE = path.join(WRITING_OUTPUT_DIR, '_template.html');

// Utility: delay for rate limiting
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Fetch Open Graph metadata from a URL
async function fetchMetadata(url) {
  if (!url) return {};

  try {
    console.log(`  Fetching: ${url}`);

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);

    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; MetadataBot/1.0)',
        'Accept': 'text/html,application/xhtml+xml'
      }
    });
    clearTimeout(timeout);

    if (!response.ok) {
      console.log(`    Warning: HTTP ${response.status}`);
      return {};
    }

    const html = await response.text();

    // Extract Open Graph and meta tags
    const metadata = {};

    // OG Title
    const ogTitle = html.match(/<meta[^>]*property=["']og:title["'][^>]*content=["']([^"']+)["']/i)
      || html.match(/<meta[^>]*content=["']([^"']+)["'][^>]*property=["']og:title["']/i);
    if (ogTitle) metadata.title = decodeHtmlEntities(ogTitle[1]);

    // Fallback to title tag
    if (!metadata.title) {
      const titleTag = html.match(/<title[^>]*>([^<]+)<\/title>/i);
      if (titleTag) metadata.title = decodeHtmlEntities(titleTag[1].trim());
    }

    // OG Description
    const ogDesc = html.match(/<meta[^>]*property=["']og:description["'][^>]*content=["']([^"']+)["']/i)
      || html.match(/<meta[^>]*content=["']([^"']+)["'][^>]*property=["']og:description["']/i);
    if (ogDesc) metadata.description = decodeHtmlEntities(ogDesc[1]);

    // Fallback to meta description
    if (!metadata.description) {
      const metaDesc = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']+)["']/i)
        || html.match(/<meta[^>]*content=["']([^"']+)["'][^>]*name=["']description["']/i);
      if (metaDesc) metadata.description = decodeHtmlEntities(metaDesc[1]);
    }

    // OG Image
    const ogImage = html.match(/<meta[^>]*property=["']og:image["'][^>]*content=["']([^"']+)["']/i)
      || html.match(/<meta[^>]*content=["']([^"']+)["'][^>]*property=["']og:image["']/i);
    if (ogImage) {
      let imageUrl = ogImage[1];
      // Handle relative URLs
      if (imageUrl.startsWith('/')) {
        const urlObj = new URL(url);
        imageUrl = `${urlObj.protocol}//${urlObj.host}${imageUrl}`;
      }
      metadata.image = imageUrl;
    }

    // OG Site Name
    const ogSite = html.match(/<meta[^>]*property=["']og:site_name["'][^>]*content=["']([^"']+)["']/i);
    if (ogSite) metadata.siteName = decodeHtmlEntities(ogSite[1]);

    // YouTube specific: get thumbnail
    if (url.includes('youtube.com/watch') || url.includes('youtu.be')) {
      const videoId = url.match(/(?:v=|youtu\.be\/)([a-zA-Z0-9_-]+)/);
      if (videoId) {
        metadata.image = `https://img.youtube.com/vi/${videoId[1]}/maxresdefault.jpg`;
      }
    }

    console.log(`    Found: "${metadata.title || '(no title)'}"`);
    return metadata;

  } catch (error) {
    console.log(`    Error: ${error.message}`);
    return {};
  }
}

function decodeHtmlEntities(str) {
  return str
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#x27;/g, "'")
    .replace(/&#x2F;/g, '/')
    .replace(/&nbsp;/g, ' ');
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// Generate HTML for a Find card
function generateFindCard(item, metadata) {
  const title = escapeHtml(item.title || metadata.title || 'Untitled');
  const description = escapeHtml(item.notes || metadata.description || '');
  const image = item.image || metadata.image;
  const category = item.category || 'link';
  const size = item.size || 'small';
  const url = item.url || '#';

  // Quote cards are special
  if (category === 'quote') {
    return `
          <article class="masonry__item" data-category="quote">
            <div class="masonry__content">
              <span class="masonry__category masonry__category--quote">Quote</span>
              <blockquote class="masonry__quote">"${escapeHtml(item.quote)}"</blockquote>
              <p class="masonry__description">— ${escapeHtml(item.author)}${item.notes ? '. ' + escapeHtml(item.notes) : ''}</p>
            </div>
          </article>`;
  }

  const sizeClass = size === 'large' ? ' masonry__item--large' : size === 'medium' ? ' masonry__item--medium' : '';

  const imageHtml = image ? `
            <div class="masonry__image">
              <img src="${escapeHtml(image)}" alt="${title}" loading="lazy">
            </div>` : '';

  return `
          <article class="masonry__item${sizeClass}" data-category="${category}">
            ${imageHtml}
            <div class="masonry__content">
              <span class="masonry__category masonry__category--${category}">${capitalize(category)}</span>
              <h3 class="masonry__title"><a href="${escapeHtml(url)}" target="_blank" rel="noopener">${title}</a></h3>
              <p class="masonry__description">${description}</p>
            </div>
          </article>`;
}

// Generate HTML for a Publication card
function generatePublicationCard(item, metadata) {
  const title = escapeHtml(item.title || metadata.title || 'Untitled');
  const authors = item.authors ? item.authors.join(', ') : '';
  const venue = escapeHtml(item.venue || metadata.siteName || '');
  const year = item.year || '';
  const type = item.type || 'journal';
  const image = item.image || metadata.image || getDefaultPublicationImage(type);
  const url = item.url || '#';
  const notes = escapeHtml(item.notes || '');

  return `
        <article class="uniform-card">
          <div class="uniform-card__image">
            <img src="${escapeHtml(image)}" alt="${title}" loading="lazy">
          </div>
          <div class="uniform-card__content">
            <span class="uniform-card__tag uniform-card__tag--publication">${capitalize(type)}</span>
            <h3 class="uniform-card__title">
              <a href="${escapeHtml(url)}" target="_blank" rel="noopener">${title}</a>
            </h3>
            <p class="uniform-card__description">${escapeHtml(authors)}</p>
            <span class="uniform-card__meta">${venue}${year ? ', ' + year : ''}</span>
            ${url !== '#' ? `
            <div class="uniform-card__links">
              <a href="${escapeHtml(url)}" class="uniform-card__link" target="_blank" rel="noopener">View</a>
            </div>` : ''}
          </div>
        </article>`;
}

// Generate HTML for a Project card
function generateProjectCard(item) {
  const title = escapeHtml(item.title || 'Untitled Project');
  const description = escapeHtml(item.description || '');
  const status = item.status || 'active';
  const tech = item.tech || [];
  const image = item.image || getDefaultProjectImage();
  const url = item.url || '#';

  const statusClass = status === 'active' ? 'uniform-card__tag--active' : 'uniform-card__tag--completed';

  return `
        <article class="uniform-card">
          <div class="uniform-card__image">
            <img src="${escapeHtml(image)}" alt="${title}" loading="lazy">
          </div>
          <div class="uniform-card__content">
            <span class="uniform-card__tag ${statusClass}">${capitalize(status)}</span>
            <h3 class="uniform-card__title">
              <a href="${escapeHtml(url)}" target="_blank" rel="noopener">${title}</a>
            </h3>
            <p class="uniform-card__description">${description}</p>
            <span class="uniform-card__meta">${tech.join(', ')}</span>
            ${url !== '#' ? `
            <div class="uniform-card__links">
              <a href="${escapeHtml(url)}" class="uniform-card__link" target="_blank" rel="noopener">View</a>
            </div>` : ''}
          </div>
        </article>`;
}

function getDefaultPublicationImage(type) {
  const images = {
    journal: 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400&q=80',
    conference: 'https://images.unsplash.com/photo-1517976487492-5750f3195933?w=400&q=80',
    thesis: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400&q=80',
    preprint: 'https://images.unsplash.com/photo-1518152006812-edab29b069ac?w=400&q=80',
    workshop: 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&q=80'
  };
  return images[type] || images.journal;
}

function getDefaultProjectImage() {
  const images = [
    'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80',
    'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80',
    'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80'
  ];
  return images[Math.floor(Math.random() * images.length)];
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// Simple Markdown to HTML converter (handles common formatting for prose)
function markdownToHtml(markdown) {
  let html = markdown;

  // Normalize line endings
  html = html.replace(/\r\n/g, '\n');

  // Escape HTML entities (but preserve markdown syntax)
  html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  // Restore blockquotes (we escaped the >)
  html = html.replace(/^&gt;\s?(.*)$/gm, '<blockquote>$1</blockquote>');
  // Merge consecutive blockquotes
  html = html.replace(/<\/blockquote>\n<blockquote>/g, '\n');

  // Headers (process after escaping so # works)
  html = html.replace(/^######\s+(.*)$/gm, '<h6>$1</h6>');
  html = html.replace(/^#####\s+(.*)$/gm, '<h5>$1</h5>');
  html = html.replace(/^####\s+(.*)$/gm, '<h4>$1</h4>');
  html = html.replace(/^###\s+(.*)$/gm, '<h3>$1</h3>');
  html = html.replace(/^##\s+(.*)$/gm, '<h2>$1</h2>');
  html = html.replace(/^#\s+(.*)$/gm, '<h1>$1</h1>');

  // Horizontal rules
  html = html.replace(/^(\*{3,}|-{3,}|_{3,})$/gm, '<hr>');

  // Bold and italic (process bold first to handle ***)
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  html = html.replace(/___(.+?)___/g, '<strong><em>$1</em></strong>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  html = html.replace(/_(.+?)_/g, '<em>$1</em>');

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Links [text](url)
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

  // Unordered lists
  html = html.replace(/^[\*\-]\s+(.*)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => '<ul>\n' + match + '</ul>\n');

  // Ordered lists
  html = html.replace(/^\d+\.\s+(.*)$/gm, '<li>$1</li>');
  // Only wrap consecutive <li> that aren't already in <ul>
  html = html.replace(/(<li>.*<\/li>\n?)(?!<\/ul>)/g, (match, p1, offset, str) => {
    // Check if already in a list
    const before = str.substring(0, offset);
    if (before.endsWith('<ul>\n') || before.endsWith('<li>\n')) return match;
    return match;
  });

  // Paragraphs: wrap text blocks that aren't already wrapped
  const lines = html.split('\n\n');
  html = lines.map(block => {
    block = block.trim();
    if (!block) return '';
    // Skip if already an HTML block element
    if (/^<(h[1-6]|ul|ol|li|blockquote|pre|hr|div|p)/.test(block)) {
      return block;
    }
    // Wrap in paragraph
    return '<p>' + block.replace(/\n/g, '<br>') + '</p>';
  }).join('\n\n');

  return html;
}

// Parse a writing markdown file
// Format: First # header = title, Second # header = date, rest = content
function parseWritingMarkdown(content) {
  const lines = content.split('\n');
  let title = '';
  let date = '';
  let contentStartIndex = 0;
  let headersFound = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    const headerMatch = line.match(/^#\s+(.+)$/);

    if (headerMatch) {
      headersFound++;
      if (headersFound === 1) {
        title = headerMatch[1];
      } else if (headersFound === 2) {
        date = headerMatch[1];
        contentStartIndex = i + 1;
        break;
      }
    }
  }

  // Get content after the two headers
  const contentLines = lines.slice(contentStartIndex);
  const contentMarkdown = contentLines.join('\n').trim();
  const contentHtml = markdownToHtml(contentMarkdown);

  return { title, date, content: contentHtml };
}

// Generate slug from title
function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim();
}

// Generate HTML for a writing list item
function generateWritingListItem(title, date, slug) {
  return `
          <li class="list__item">
            <a href="/writing/${slug}.html" class="list__link">
              <span class="list__title">${escapeHtml(title)}</span>
              <span class="list__meta">${escapeHtml(date)}</span>
            </a>
          </li>`;
}

// Parse date string for sorting (handles various formats)
function parseDateForSort(dateStr) {
  // Try to parse common date formats
  const months = {
    'january': 0, 'february': 1, 'march': 2, 'april': 3, 'may': 4, 'june': 5,
    'july': 6, 'august': 7, 'september': 8, 'october': 9, 'november': 10, 'december': 11
  };

  // "January 15, 2026" or "January 2026"
  const match = dateStr.toLowerCase().match(/(\w+)\s*(\d+)?,?\s*(\d{4})/);
  if (match) {
    const month = months[match[1]] || 0;
    const day = parseInt(match[2]) || 1;
    const year = parseInt(match[3]);
    return new Date(year, month, day);
  }

  // Fallback: try native parsing
  const parsed = new Date(dateStr);
  return isNaN(parsed) ? new Date(0) : parsed;
}

// Update HTML file with generated content
function updateHtmlFile(filepath, marker, content) {
  let html = fs.readFileSync(filepath, 'utf-8');

  // Look for markers like <!-- BEGIN:finds --> ... <!-- END:finds -->
  const beginMarker = `<!-- BEGIN:${marker} -->`;
  const endMarker = `<!-- END:${marker} -->`;

  const beginIndex = html.indexOf(beginMarker);
  const endIndex = html.indexOf(endMarker);

  if (beginIndex === -1 || endIndex === -1) {
    console.log(`  Warning: Markers not found for ${marker} in ${filepath}`);
    return false;
  }

  const before = html.substring(0, beginIndex + beginMarker.length);
  const after = html.substring(endIndex);

  html = before + '\n' + content + '\n        ' + after;

  fs.writeFileSync(filepath, html);
  return true;
}

// Main build function
async function build() {
  console.log('Building site...\n');

  // Load data files
  const findsPath = path.join(DATA_DIR, 'finds.json');
  const pubsPath = path.join(DATA_DIR, 'publications.json');
  const projectsPath = path.join(DATA_DIR, 'projects.json');

  // Build Finds
  if (fs.existsSync(findsPath)) {
    console.log('Processing Finds...');
    const finds = JSON.parse(fs.readFileSync(findsPath, 'utf-8'));

    const findCards = [];
    for (const item of finds) {
      const metadata = await fetchMetadata(item.url);
      findCards.push(generateFindCard(item, metadata));
      await delay(500); // Rate limiting
    }

    const findsHtml = findCards.join('');
    if (updateHtmlFile(path.join(OUTPUT_DIR, 'index.html'), 'finds', findsHtml)) {
      console.log(`  Updated index.html with ${finds.length} finds\n`);
    }
  }

  // Build Publications
  if (fs.existsSync(pubsPath)) {
    console.log('Processing Publications...');
    const pubs = JSON.parse(fs.readFileSync(pubsPath, 'utf-8'));

    const pubCards = [];
    for (const item of pubs) {
      const metadata = await fetchMetadata(item.url);
      pubCards.push(generatePublicationCard(item, metadata));
      await delay(500);
    }

    const pubsHtml = pubCards.join('');
    if (updateHtmlFile(path.join(OUTPUT_DIR, 'publications.html'), 'publications', pubsHtml)) {
      console.log(`  Updated publications.html with ${pubs.length} publications\n`);
    }
  }

  // Build Projects
  if (fs.existsSync(projectsPath)) {
    console.log('Processing Projects...');
    const projects = JSON.parse(fs.readFileSync(projectsPath, 'utf-8'));

    const projectCards = projects.map(item => generateProjectCard(item));

    const projectsHtml = projectCards.join('');
    if (updateHtmlFile(path.join(OUTPUT_DIR, 'projects.html'), 'projects', projectsHtml)) {
      console.log(`  Updated projects.html with ${projects.length} projects\n`);
    }
  }

  // Build Writings from Markdown files
  if (fs.existsSync(WRITINGS_DIR) && fs.existsSync(WRITING_TEMPLATE)) {
    console.log('Processing Writings...');
    const template = fs.readFileSync(WRITING_TEMPLATE, 'utf-8');

    // Get all .md files
    const mdFiles = fs.readdirSync(WRITINGS_DIR)
      .filter(f => f.endsWith('.md'));

    if (mdFiles.length > 0) {
      const writings = [];

      for (const file of mdFiles) {
        const filePath = path.join(WRITINGS_DIR, file);
        const content = fs.readFileSync(filePath, 'utf-8');
        const parsed = parseWritingMarkdown(content);

        if (!parsed.title) {
          console.log(`  Warning: No title found in ${file}, skipping`);
          continue;
        }

        const slug = slugify(parsed.title);
        console.log(`  Processing: ${parsed.title}`);

        // Generate the individual writing page
        let pageHtml = template
          .replace(/POST_TITLE/g, escapeHtml(parsed.title))
          .replace(/POST_DATE/g, escapeHtml(parsed.date))
          .replace(/POST_DESCRIPTION/g, escapeHtml(parsed.title));

        // Replace the content placeholder
        pageHtml = pageHtml.replace(
          /<!-- Your content here -->\s*<p>\s*Start writing\.\.\.\s*<\/p>/,
          parsed.content
        );

        // Write the page
        const outputPath = path.join(WRITING_OUTPUT_DIR, `${slug}.html`);
        fs.writeFileSync(outputPath, pageHtml);

        writings.push({
          title: parsed.title,
          date: parsed.date,
          slug: slug,
          sortDate: parseDateForSort(parsed.date)
        });
      }

      // Sort writings by date (newest first)
      writings.sort((a, b) => b.sortDate - a.sortDate);

      // Generate the list HTML
      const listHtml = writings
        .map(w => generateWritingListItem(w.title, w.date, w.slug))
        .join('');

      if (updateHtmlFile(path.join(OUTPUT_DIR, 'writing.html'), 'writing', listHtml)) {
        console.log(`  Updated writing.html with ${writings.length} writings\n`);
      }
    } else {
      console.log('  No .md files found in _data/writings/\n');
    }
  }

  console.log('Build complete!');
}

// Run
build().catch(console.error);
