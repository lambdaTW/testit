import re
import uuid
from playwright.sync_api import Page, expect
import pytest


def create_todo_item(page, todo_text: str):
    page.get_by_role("textbox", name="What needs to be done?").click()
    page.get_by_role("textbox", name="What needs to be done?").fill(todo_text)
    page.get_by_role("textbox", name="What needs to be done?").press("Enter")


def test_second_todo_in_list(page: Page):
    # 新增兩個項目到列表
    page.goto("https://demo.playwright.dev/todomvc/#/")
    todo_input =  page.get_by_role("textbox", name="What needs to be done?")
    create_todo_item(page, "xxxxx")
    expect(page.get_by_test_id("todo-title")).to_contain_text("xxxxx")
    create_todo_item(page, "test2")
    expect(page.locator("body")).to_contain_text("test2")

@pytest.fixture
def create_and_check(page: Page):
    page.goto("https://demo.playwright.dev/todomvc/#/")
    create_todo_item(page, "test todo")
    page.get_by_role("checkbox", name="Toggle Todo").check()


def test_checked_item_in_all_list(page: Page, create_and_check) -> None:
    expect(page.get_by_test_id("todo-title")).to_contain_text("test todo")


def test_checked_item_in_completed_list(page: Page, create_and_check) -> None:
    page.get_by_role("link", name="Completed").click()
    expect(page.get_by_test_id("todo-title")).to_contain_text("test todo")
    # page.get_by_role("link", name="Active").click()


def test_checked_item_not_in_active_list(page: Page, create_and_check) -> None:
    page.get_by_role("link", name="Active").click()
    # 不顯示
    expect(page.locator("html")).not_to_contain_text("test todo")


def test_removed_item_not_in_all_list(page: Page, create_and_check) -> None:
    page.get_by_role("button", name="Clear completed").click()
    # 不顯示
    expect(page.locator("html")).not_to_contain_text("test todo")


def test_removed_item_not_in_active_list(page: Page, create_and_check) -> None:
    page.get_by_role("link", name="Active").click()
    page.get_by_role("button", name="Clear completed").click()
    # 不顯示
    expect(page.locator("html")).not_to_contain_text("test todo")


def test_removed_item_not_in_completed_list(page: Page, create_and_check) -> None:
    page.get_by_role("link", name="Completed").click()
    page.get_by_role("button", name="Clear completed").click()
    # 不顯示
    expect(page.locator("html")).not_to_contain_text("test todo")


def test_check_all_button(page: Page) -> None:
    page.goto("https://demo.playwright.dev/todomvc/#/")
    for _ in range(10):
        create_todo_item(page, "test todo")
    page.locator("body > section > div > section > label").click()

    count = 0
    for item_locator in page.locator("xpath=/html/body/section/div/section/ul/li/div/input").all():
        expect(item_locator).to_be_checked()
        count += 1
    assert count == 10


def test_checked_item_will_not_be_affected_by_check_all_when_unchecked_item_exists(page: Page, create_and_check) -> None:
    create_todo_item(page, "xxxxx")
    check_all_button = page.locator("body > section > div > section > label")
    check_all_button.click()
    count = 0
    for item_locator in page.locator("xpath=/html/body/section/div/section/ul/li/div/input").all():
        expect(item_locator).to_be_checked()
        count += 1
    assert count == 2

def test_uncheck_all_button(page: Page, create_and_check) -> None:
    # while all items are checked the `check all button` would be `uncheck all button`
    check_all_button = page.locator("body > section > div > section > label")
    check_all_button.click()
    count = 0
    for item_locator in page.locator("xpath=/html/body/section/div/section/ul/li/div/input").all():
        expect(item_locator).not_to_be_checked()
        count += 1
    assert count == 1


def test_remove_button(page: Page, create_and_check) -> None:
    page.get_by_label("Delete").click()
    expect(page.locator("html")).not_to_contain_text("test todo")


def test_remove_checked_item(page: Page, create_and_check) -> None:
    create_todo_item(page, "new item")
    page.get_by_test_id("todo-title").first.hover()
    page.get_by_label("Delete").first.click()
    expect(page.locator("html")).not_to_contain_text("test todo")
    expect(page.locator("html")).to_contain_text("new item")

def test_remove_unchecked_item(page: Page) -> None:
    page.goto("https://demo.playwright.dev/todomvc/#/")
    create_todo_item(page, "first item")
    create_todo_item(page, "new item")
    page.get_by_test_id("todo-title").first.hover()
    page.get_by_label("Delete").first.click()
    expect(page.locator("html")).not_to_contain_text("first item")
    expect(page.locator("html")).to_contain_text("new item")


@pytest.mark.parametrize("tab", ["All", "Completed", "Active"])
def test_counting_with_checked(page: Page, create_and_check, tab: str) -> None:
    for _ in range(8):
        create_todo_item(page, str(uuid.uuid4()))

    counter_locator = page.locator("xpath=/html/body/section/div/footer/span/strong")
    page.get_by_role("link", name=tab).click()
    assert counter_locator.inner_text() == "8"

@pytest.mark.parametrize("tab", ["All", "Completed", "Active"])
def test_counting_with_removed(page: Page, tab: str) -> None:
    page.goto("https://demo.playwright.dev/todomvc/#/")
    for _ in range(8):
        create_todo_item(page, str(uuid.uuid4()))

    page.get_by_test_id("todo-title").last.hover()
    page.get_by_label("Delete").last.click()
    page.get_by_role("link", name=tab).click()
    counter_locator = page.locator("xpath=/html/body/section/div/footer/span/strong")
    assert counter_locator.inner_text() == "7"
# 完成項目 (checked)
#  > 在 all 的頁面，會顯示 -> test_checked_item_in_all_list
#  > 在 completed 的頁面，會顯示 -> test_checked_item_in_completed_list
#  > 在 active 的頁面，不該顯示 -> test_checked_item_not_in_active_list
#  > 清除完成項目
#    > 在 all 的頁面，不該顯示 -> test_removed_item_not_in_all_list
#    > 在 completed 的頁面，不該顯示 -> test_removed_item_not_in_active_list
#    > 在 active 的頁面，不該顯示 -> test_removed_item_not_in_completed_list
# 完成所有項目 button
# 1 todo
# 多 todo -> test_check_all_button
# 已經有被勾選，不受影響 (checked)
#  > unchecked exist -> test_checked_item_will_not_be_affected_by_check_all_when_unchecked_item_exists
#  > unchecked not exist (當所有的 item 都被 check 時，該按鈕會變成 uncheck all) -> test_uncheck_all_button
# 1~N
# 刪除
# 1 (畫面有多個)
#  > checked，不該顯示 -> test_remove_checked_item
#  > unchecked，不該顯示 -> test_remove_unchecked_item
# 計數
# 新增要 +1
# 刪除要 -1
# checked 要 -1
