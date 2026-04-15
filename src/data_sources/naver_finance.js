#!/usr/bin/env node
/**
 * naver_finance.js — Naver Finance scraper for Korean/Asian company data.
 *
 * Usage:
 *   node naver_finance.js "Company Name or Korean Ticker"
 *
 * Outputs: JSON object to stdout with financial metrics.
 * Exit codes:
 *   0 = success
 *   1 = usage error
 *   2 = scrape failed / company not found
 *
 * Called by naver_finance.py as a subprocess.
 * Useful for Korean KOSPI/KOSDAQ companies not covered by US data sources.
 */

const puppeteer = require('puppeteer');

const query = process.argv[2];
if (!query) {
  process.stderr.write('Usage: node naver_finance.js "Company Name"\n');
  process.exit(1);
}

const SEARCH_URL = `https://finance.naver.com/search/searchList.naver?query=${encodeURIComponent(query)}`;
const WAIT_MS = 3000;

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

    // Step 1: Search for the company
    await page.goto(SEARCH_URL, { waitUntil: 'domcontentloaded', timeout: 20000 });
    await new Promise(r => setTimeout(r, WAIT_MS));

    // Extract first matching company's stock code and name from search results
    const firstResult = await page.evaluate(() => {
      // Naver Finance search result table: rows have company name links
      const rows = document.querySelectorAll('table.tbl_search tbody tr, .search_result table tbody tr');
      for (const row of rows) {
        const link = row.querySelector('a[href*="code="]');
        if (!link) continue;
        const href = link.href || '';
        const codeMatch = href.match(/code=(\d{6})/);
        if (!codeMatch) continue;
        return {
          code: codeMatch[1],
          name: link.textContent.trim(),
        };
      }
      return null;
    });

    if (!firstResult) {
      process.stderr.write(`No results found for "${query}" on Naver Finance.\n`);
      process.exit(2);
    }

    // Step 2: Navigate to the company's main page
    const companyUrl = `https://finance.naver.com/item/main.naver?code=${firstResult.code}`;
    await page.goto(companyUrl, { waitUntil: 'domcontentloaded', timeout: 20000 });
    await new Promise(r => setTimeout(r, WAIT_MS));

    // Step 3: Extract financial data
    const data = await page.evaluate((code, name) => {
      const getText = (sel) => {
        const el = document.querySelector(sel);
        return el ? el.textContent.trim() : null;
      };

      // Current price — typically in .no_today .blind or .stock_price
      const priceEl = document.querySelector('.no_today .blind') ||
                      document.querySelector('#_nowVal') ||
                      document.querySelector('.stock_price');
      const price = priceEl ? priceEl.textContent.replace(/[^0-9,]/g, '').replace(/,/g, '') : null;

      // Key stats table — Naver Finance shows PER, PBR, ROE in a table
      const stats = {};
      const statRows = document.querySelectorAll('.tab_con1 table tr, .section_trade table tr, table.tb_type1 tr');
      for (const row of statRows) {
        const cells = row.querySelectorAll('th, td');
        if (cells.length >= 2) {
          const key = cells[0].textContent.trim();
          const val = cells[1].textContent.trim();
          if (key && val) stats[key] = val;
        }
      }

      // Market cap — often labeled 시가총액
      const marketCapEl = document.querySelector('[class*="cap"], [class*="market"]');

      // Extract from aside/summary tables
      const tableData = {};
      const allTables = document.querySelectorAll('table');
      for (const tbl of allTables) {
        const rows = tbl.querySelectorAll('tr');
        for (const row of rows) {
          const ths = row.querySelectorAll('th');
          const tds = row.querySelectorAll('td');
          for (let i = 0; i < Math.min(ths.length, tds.length); i++) {
            const k = ths[i].textContent.trim();
            const v = tds[i].textContent.trim();
            if (k && v && k.length < 20) tableData[k] = v;
          }
        }
      }

      return {
        stock_code: code,
        company_name: name,
        current_price_krw: price ? parseInt(price) : null,
        stats: stats,
        table_data: tableData,
        page_url: window.location.href,
      };
    }, firstResult.code, firstResult.name);

    // Clean and structure the output
    const result = {
      stock_code: data.stock_code,
      company_name: data.company_name,
      exchange: 'KOSPI/KOSDAQ',
      current_price_krw: data.current_price_krw,
      page_url: data.page_url,
      metrics: {},
    };

    // Map Korean labels to English keys
    const koreanMap = {
      'PER(배)': 'per',
      'PBR(배)': 'pbr',
      'ROE(%)': 'roe_pct',
      '시가총액': 'market_cap_display',
      '매출액': 'revenue_display',
      '영업이익': 'operating_income_display',
      '당기순이익': 'net_income_display',
      '부채비율': 'debt_ratio_pct',
      '배당수익률': 'dividend_yield_pct',
      'EPS(원)': 'eps_krw',
    };

    const combined = { ...data.stats, ...data.table_data };
    for (const [kor, eng] of Object.entries(koreanMap)) {
      if (combined[kor]) {
        result.metrics[eng] = combined[kor];
      }
    }

    process.stdout.write(JSON.stringify(result, null, 2));
    process.exit(0);

  } finally {
    await browser.close();
  }
}

scrape().catch(err => {
  process.stderr.write(`Naver Finance scrape error: ${err.message}\n`);
  process.exit(2);
});
