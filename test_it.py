import re
from playwright.sync_api import Page, expect


def test_search_google_image(page: Page) -> None:
    page.goto("https://tw.yahoo.com")
    page.locator('xpath=/html/body/div[1]/div/nav/div/div[1]/ul/li[1]').hover()
    page.mouse.down()
    search_input = page.locator("xpath=/html/body/header/div/div/div[1]/div/div/div[1]/div[1]/div/div/form/input[1]")
    box = search_input.bounding_box()
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    search_input.hover()
    page.mouse.up()
    expect(search_input).to_have_value(re.compile("news"))
