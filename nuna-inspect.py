import os, json
from playwright.sync_api import sync_playwright

os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/opt/pw-browsers'

def inspect_form(page, url, label):
    print(f'\n=== {label} ===')
    page.goto(url, wait_until='networkidle', timeout=60000)
    print('URL:', page.url)
    page.screenshot(path=f'/home/user/test/{label.lower().replace(" ","-")}-initial.png', full_page=True)

    inputs = page.evaluate('''() => {
        const fields = [];
        document.querySelectorAll('input, select, textarea').forEach(el => {
            const label = document.querySelector(`label[for="${el.id}"]`);
            fields.push({
                tag: el.tagName,
                type: el.type || '',
                name: el.name || '',
                id: el.id || '',
                placeholder: el.placeholder || '',
                ariaLabel: el.getAttribute('aria-label') || '',
                labelText: label ? label.textContent.trim() : '',
                required: el.required,
                value: el.value || ''
            });
        });
        return fields;
    }''')
    print('Fields:')
    for f in inputs:
        print(f'  {f}')

    # Also check for any iframes
    frames = page.frames
    print(f'Frames: {len(frames)}')
    for i, frame in enumerate(frames):
        print(f'  Frame {i}: {frame.url}')

    return inputs

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
        args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
    )
    ctx = browser.new_context(viewport={'width': 1280, 'height': 900}, ignore_https_errors=True)
    page = ctx.new_page()

    inspect_form(page, 'https://nunababy.com/usa/register-car-seat', 'car-seat')
    inspect_form(page, 'https://nunababy.com/usa/register-gear', 'stroller')

    browser.close()
    print('\nDone.')
