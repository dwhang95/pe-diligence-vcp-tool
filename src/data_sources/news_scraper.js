#!/usr/bin/env node
/**
 * news_scraper.js — Google News scraper via Puppeteer
 *
 * Usage:
 *   node news_scraper.js "Company Name"
 *
 * Outputs: JSON array to stdout, one object per article:
 *   { title, datetime, source }
 *
 * Exit codes:
 *   0 = success (JSON on stdout)
 *   1 = usage error
 *   2 = scrape failed (error on stderr)
 *
 * Called by news.py as a subprocess. Falls back to Google RSS in Python
 * if this script exits non-zero.
 */

const puppeteer = require('puppeteer');

const company = process.argv[2];
if (!company) {
  process.stderr.write('Usage: node news_scraper.js "Company Name"\n');
  process.exit(1);
}

const GOOGLE_NEWS_URL =
  `https://news.google.com/search?q=${encodeURIComponent(company)}&hl=en-US&gl=US&ceid=US:en`;

// Article link class — confirmed from live inspection 2026-04-06
const ARTICLE_LINK_CLASS = 'JtKRv';
const WAIT_TIMEOUT_MS = 15000;
const RENDER_SETTLE_MS = 2500;
const MAX_ARTICLES = 60;

async function scrape() {
  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
    ],
  });

  try {
    const page = await browser.newPage();
    await page.setUserAgent(
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' +
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    );

    // Navigate and wait for the article link class to appear
    await page.goto(GOOGLE_NEWS_URL, { waitUntil: 'networkidle2', timeout: WAIT_TIMEOUT_MS });

    // Give JS a moment to fully render card metadata
    await new Promise(r => setTimeout(r, RENDER_SETTLE_MS));

    // Extract articles using the same selector strategy validated via MCP
    const articles = await page.evaluate((linkClass, maxItems) => {
      const results = [];
      const seen = new Set();
      const links = Array.from(document.querySelectorAll(`a.${linkClass}`));

      for (const a of links) {
        if (results.length >= maxItems) break;

        const title = a.textContent.trim();
        if (!title || seen.has(title)) continue;
        seen.add(title);

        // Climb the DOM to find the card container holding time + source
        let node = a;
        let timeEl = null;
        let srcEl = null;

        for (let i = 0; i < 12; i++) {
          node = node.parentElement;
          if (!node) break;
          if (!timeEl) timeEl = node.querySelector('time[datetime]');
          if (!srcEl) {
            srcEl = node.querySelector('[class*="wEwyrc"]') ||
                    node.querySelector('[class*="AVN2gc"]') ||
                    node.querySelector('[class*="vr1PYe"]');
          }
          if (timeEl && srcEl) break;
        }

        results.push({
          title,
          datetime: timeEl ? timeEl.getAttribute('datetime') : '',
          source: srcEl ? srcEl.textContent.trim().split('\n')[0].trim() : '',
        });
      }

      return results;
    }, ARTICLE_LINK_CLASS, MAX_ARTICLES);

    if (articles.length === 0) {
      process.stderr.write(
        `No articles found for "${company}". ` +
        `Google News may have changed its DOM structure (article link class: ${ARTICLE_LINK_CLASS}).\n`
      );
      process.exit(2);
    }

    process.stdout.write(JSON.stringify(articles));
    process.exit(0);

  } finally {
    await browser.close();
  }
}

scrape().catch(err => {
  process.stderr.write(`Scrape error: ${err.message}\n`);
  process.exit(2);
});
