import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    page.goto("https://playwright.dev/python/docs/input")
    for _ in range(100):
        page.mouse.wheel(0, 20)
    time.sleep(5)
