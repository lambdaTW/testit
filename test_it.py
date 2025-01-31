from playwright.sync_api import Page, expect
from pytest_playwright.pytest_playwright import CreateContextCallback


def test_search_google_image(page: Page) -> None:
    page.goto("https://google.com")
    page.locator("xpath=/html/body/div[1]/div[2]/div/img").hover()
    page.mouse.down()
    page.mouse.move(403, 391)
    page.locator("xpath=/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div[2]/c-wiz/div/div/div[2]/div[2]").hover()
    page.mouse.up()
    expect(
        page.locator('//*[@id="rso"]/div[1]/div/div/div/div/div/div/div[1]/div/div/div[2]/a/div/div[2]/div/div/span')
    ).to_contain_text("google", ignore_case=True)
