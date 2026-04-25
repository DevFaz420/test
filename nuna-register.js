const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const CONTACT = {
  firstName: 'Louie',
  lastName: 'Fazio',
  address: '3018 Goldsmith St',
  city: 'Santa Monica',
  state: 'CA',
  zip: '90405',
  phone: '+15053530969',
};

const CAR_SEAT = {
  productName: 'PIPA aire rx',
  modelNo: 'CF18508600CVR',
  serialNo: '1722017',
  dateOfManufacture: '2025/12/16',
  dateOfPurchase: '03/15/2026',
};

const STROLLER = {
  productName: 'TRVL lx',
  modelNo: 'ST18100CVR',
  serialNo: '',
  dateOfManufacture: '2025/12/13',
  dateOfPurchase: '03/15/2026',
};

async function screenshotPath(name) {
  return path.join('/home/user/test', `${name}.png`);
}

async function fillCarSeat(page) {
  console.log('\n=== Car Seat Registration ===');
  await page.goto('https://nunababy.com/usa/register-car-seat', { waitUntil: 'networkidle', timeout: 60000 });
  console.log('Page loaded:', page.url());

  // Take initial screenshot to see the form
  await page.screenshot({ path: await screenshotPath('carseat-form'), fullPage: true });

  // Log all input fields for debugging
  const inputs = await page.$$eval('input, select, textarea', els =>
    els.map(el => ({ tag: el.tagName, type: el.type, name: el.name, id: el.id, placeholder: el.placeholder, label: el.getAttribute('aria-label') }))
  );
  console.log('Form fields:', JSON.stringify(inputs, null, 2));

  return inputs;
}

async function fillStroller(page) {
  console.log('\n=== Stroller Registration ===');
  await page.goto('https://nunababy.com/usa/register-gear', { waitUntil: 'networkidle', timeout: 60000 });
  console.log('Page loaded:', page.url());

  await page.screenshot({ path: await screenshotPath('stroller-form'), fullPage: true });

  const inputs = await page.$$eval('input, select, textarea', els =>
    els.map(el => ({ tag: el.tagName, type: el.type, name: el.name, id: el.id, placeholder: el.placeholder, label: el.getAttribute('aria-label') }))
  );
  console.log('Form fields:', JSON.stringify(inputs, null, 2));

  return inputs;
}

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });

  try {
    const page = await context.newPage();

    // First, inspect both forms
    await fillCarSeat(page);
    await fillStroller(page);

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
})();
