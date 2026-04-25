"""
Nuna Baby Product Registration - Run this locally.

Setup (one-time):
  pip install playwright
  playwright install chromium

Then run:
  python nuna-register-local.py
"""

import time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

CONTACT = {
    'first_name': 'Louie',
    'last_name': 'Fazio',
    'address': '3018 Goldsmith St',
    'city': 'Santa Monica',
    'state': 'CA',
    'zip': '90405',
    'phone': '5053530969',
}

CAR_SEAT_URL = 'https://nunababy.com/usa/register-car-seat'
STROLLER_URL = 'https://nunababy.com/usa/register-gear'

CAR_SEAT = {
    'product_name': 'PIPA aire rx',
    'model_no': 'CF18508600CVR',
    'serial_no': '1722017',
    'date_of_manufacture': '2025/12/16',
    'date_of_purchase': '03/15/2026',
}

STROLLER = {
    'product_name': 'TRVL lx',
    'model_no': 'ST18100CVR',
    'serial_no': '',
    'date_of_manufacture': '2025/12/13',
    'date_of_purchase': '03/15/2026',
}


def smart_fill(page, selector_attempts, value):
    """Try multiple selectors until one works."""
    for sel in selector_attempts:
        try:
            el = page.locator(sel).first
            if el.count() and el.is_visible(timeout=2000):
                el.fill(value)
                return True
        except Exception:
            continue
    print(f'  WARNING: Could not fill any of {selector_attempts}')
    return False


def smart_select(page, selector_attempts, value):
    """Try multiple selectors for a <select> dropdown."""
    for sel in selector_attempts:
        try:
            el = page.locator(sel).first
            if el.count() and el.is_visible(timeout=2000):
                el.select_option(label=value)
                return True
        except Exception:
            try:
                el.select_option(value=value)
                return True
            except Exception:
                continue
    print(f'  WARNING: Could not select any of {selector_attempts}')
    return False


def dump_fields(page):
    """Print all visible form fields for debugging."""
    fields = page.evaluate("""() => {
        return [...document.querySelectorAll('input,select,textarea')].map(el => {
            const lbl = document.querySelector(`label[for="${el.id}"]`);
            return {tag:el.tagName,type:el.type,name:el.name,id:el.id,
                    placeholder:el.placeholder,label:lbl?lbl.textContent.trim():'',required:el.required};
        });
    }""")
    for f in fields:
        print('   ', f)


def register_car_seat(page):
    print('\n--- Car Seat Registration ---')
    page.goto(CAR_SEAT_URL, wait_until='domcontentloaded', timeout=60000)
    page.wait_for_timeout(3000)
    print('Page:', page.url)

    print('  Form fields detected:')
    dump_fields(page)
    page.screenshot(path='carseat-form.png', full_page=True)

    # Common selector patterns Nuna might use
    smart_fill(page, ['[name*="first"], [id*="first"], [placeholder*="First"]',
                      '[name="first_name"], [id="first_name"]'], CONTACT['first_name'])
    smart_fill(page, ['[name*="last"], [id*="last"], [placeholder*="Last"]',
                      '[name="last_name"], [id="last_name"]'], CONTACT['last_name'])
    smart_fill(page, ['[name*="address"], [id*="address"]'], CONTACT['address'])
    smart_fill(page, ['[name*="city"], [id*="city"]'], CONTACT['city'])
    smart_fill(page, ['[name*="zip"], [name*="postal"], [id*="zip"]'], CONTACT['zip'])
    smart_fill(page, ['[name*="phone"], [id*="phone"]'], CONTACT['phone'])

    # State - might be a select or text
    try:
        smart_select(page, ['[name*="state"], [id*="state"]'], 'California')
    except Exception:
        smart_fill(page, ['[name*="state"], [id*="state"]'], CONTACT['state'])

    # Product fields
    smart_fill(page, ['[name*="model"], [id*="model"]'], CAR_SEAT['model_no'])
    smart_fill(page, ['[name*="serial"], [id*="serial"]'], CAR_SEAT['serial_no'])
    smart_fill(page, ['[name*="manufacture"], [name*="mfg"], [id*="manufacture"]'],
               CAR_SEAT['date_of_manufacture'])
    smart_fill(page, ['[name*="purchase"], [id*="purchase"]'], CAR_SEAT['date_of_purchase'])

    page.screenshot(path='carseat-filled.png', full_page=True)
    print('  Screenshot saved: carseat-filled.png')

    # Check for CAPTCHA before submitting
    captcha = page.locator('iframe[src*="recaptcha"], iframe[src*="hcaptcha"], .g-recaptcha, .h-captcha').count()
    if captcha:
        print('  CAPTCHA DETECTED - manual intervention needed for submit step.')
        input('  Solve the CAPTCHA in the browser, then press Enter to continue...')

    # Submit
    try:
        page.locator('button[type="submit"], input[type="submit"], [class*="submit"]').first.click()
        page.wait_for_timeout(5000)
        page.screenshot(path='carseat-confirmation.png', full_page=True)
        print('  Submitted. Screenshot: carseat-confirmation.png')
        print('  Final URL:', page.url)
    except Exception as e:
        print(f'  Submit error: {e}')
        page.screenshot(path='carseat-error.png', full_page=True)


def register_stroller(page):
    print('\n--- Stroller Registration ---')
    page.goto(STROLLER_URL, wait_until='domcontentloaded', timeout=60000)
    page.wait_for_timeout(3000)
    print('Page:', page.url)

    print('  Form fields detected:')
    dump_fields(page)
    page.screenshot(path='stroller-form.png', full_page=True)

    smart_fill(page, ['[name*="first"], [id*="first"], [placeholder*="First"]',
                      '[name="first_name"], [id="first_name"]'], CONTACT['first_name'])
    smart_fill(page, ['[name*="last"], [id*="last"], [placeholder*="Last"]',
                      '[name="last_name"], [id="last_name"]'], CONTACT['last_name'])
    smart_fill(page, ['[name*="address"], [id*="address"]'], CONTACT['address'])
    smart_fill(page, ['[name*="city"], [id*="city"]'], CONTACT['city'])
    smart_fill(page, ['[name*="zip"], [name*="postal"], [id*="zip"]'], CONTACT['zip'])
    smart_fill(page, ['[name*="phone"], [id*="phone"]'], CONTACT['phone'])

    try:
        smart_select(page, ['[name*="state"], [id*="state"]'], 'California')
    except Exception:
        smart_fill(page, ['[name*="state"], [id*="state"]'], CONTACT['state'])

    smart_fill(page, ['[name*="model"], [id*="model"]'], STROLLER['model_no'])
    if STROLLER['serial_no']:
        smart_fill(page, ['[name*="serial"], [id*="serial"]'], STROLLER['serial_no'])
    smart_fill(page, ['[name*="manufacture"], [name*="mfg"], [id*="manufacture"]'],
               STROLLER['date_of_manufacture'])
    smart_fill(page, ['[name*="purchase"], [id*="purchase"]'], STROLLER['date_of_purchase'])

    page.screenshot(path='stroller-filled.png', full_page=True)
    print('  Screenshot saved: stroller-filled.png')

    captcha = page.locator('iframe[src*="recaptcha"], iframe[src*="hcaptcha"], .g-recaptcha, .h-captcha').count()
    if captcha:
        print('  CAPTCHA DETECTED - manual intervention needed for submit step.')
        input('  Solve the CAPTCHA in the browser, then press Enter to continue...')

    try:
        page.locator('button[type="submit"], input[type="submit"], [class*="submit"]').first.click()
        page.wait_for_timeout(5000)
        page.screenshot(path='stroller-confirmation.png', full_page=True)
        print('  Submitted. Screenshot: stroller-confirmation.png')
        print('  Final URL:', page.url)
    except Exception as e:
        print(f'  Submit error: {e}')
        page.screenshot(path='stroller-error.png', full_page=True)


with sync_playwright() as p:
    # headless=False so you can see what's happening and solve any CAPTCHA
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
    page = ctx.new_page()

    register_car_seat(page)
    register_stroller(page)

    print('\nAll done. Check the screenshot files in the current directory.')
    browser.close()
