import pytest
from playwright.sync_api import Page, Locator, expect
from pathlib import Path

REQUIRED_FIELDS = [
    "last_name",
    "phone",
    "email",
    "password",
]
VALID_DATA = {
    "first_name": "test",
    "last_name": "last",
    "phone": "0987654321",
    "email": "test@test.com",
    "password": "testme1234567",
    "country": "Taiwan",
}
# --- Fixtures for page and elements ---

@pytest.fixture
def form_page(page: Page) -> Page:
    # page.goto("https://qa-practice.netlify.app/bugs-form")
    # correct HTML
    page.goto(f"file://{Path(__name__).parent.resolve()}/form/index.html")
    return page


@pytest.fixture
def first_name(form_page: Page) -> Locator:
    return form_page.get_by_placeholder("Enter first name")


@pytest.fixture
def last_name(form_page: Page) -> Locator:
    return form_page.get_by_placeholder("Enter last name")


@pytest.fixture
def phone(form_page: Page) -> Locator:
    return form_page.get_by_placeholder("Enter phone number")


@pytest.fixture
def email(form_page: Page) -> Locator:
    return form_page.get_by_placeholder("Enter email")


@pytest.fixture
def password(form_page: Page) -> Locator:
    return form_page.get_by_placeholder("Password")


@pytest.fixture
def register_button(form_page: Page) -> Locator:
    return form_page.get_by_role("button", name="Register")


@pytest.fixture
def term_checkbox(form_page: Page) -> Locator:
    return form_page.get_by_label("I agree with the terms and")

# --- Fixture for test input data ---

@pytest.fixture
def form_input_data() -> dict:
    return VALID_DATA


@pytest.fixture
def country(form_page: Page) -> Locator:
    return form_page.locator("#countries_dropdown_menu")


@pytest.fixture
def form_locator_map(
    first_name: Locator,
    last_name: Locator,
    phone: Locator,
    email: Locator,
    password: Locator,
    country: Locator,
) -> dict:
    return {
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "email": email,
        "password": password,
        "country": country,
    }


@pytest.fixture
def form_filled_page(
    form_page: Page,
    first_name: Locator,
    last_name: Locator,
    phone: Locator,
    email: Locator,
    password: Locator,
    country: Locator,
    register_button: Locator,
    form_input_data: dict,
    form_locator_map: dict,
) -> Page:
    for fill_key in ["first_name", "last_name", "phone", "email", "password"]:
        locator = form_locator_map.get(fill_key)
        data = form_input_data.get(fill_key)
        if locator and data:
            locator.fill(data)

    if "country" in form_input_data:
        country.select_option(form_input_data["country"])

    return form_page

# --- Test using input data fixture ---

def test_submit_success(
    form_filled_page: Page,
    register_button: Locator,
    term_checkbox: Locator,
    form_input_data: dict,
):
    term_checkbox.check()
    register_button.click()

    expect(form_filled_page.locator("#message")).to_contain_text("Successfully registered the following information")
    expect(form_filled_page.locator("#resultFn")).to_contain_text(f"First Name: {form_input_data['first_name']}")
    expect(form_filled_page.locator("#resultLn")).to_contain_text(f"Last Name: {form_input_data['last_name']}")
    expect(form_filled_page.locator("#resultPhone")).to_contain_text(f"Phone Number: {form_input_data['phone']}")
    expect(form_filled_page.locator("#country")).to_contain_text(f"Country: {form_input_data['country']}")
    expect(form_filled_page.locator("#resultEmail")).to_contain_text(f"Email: {form_input_data['email']}")

    class_attr = form_filled_page.locator("#message").get_attribute("class")
    assert "alert-success" in class_attr.split()
    assert "alert-danger" not in class_attr.split()


def test_term_checked_form_is_submittable(
    form_filled_page: Page,
    register_button: Locator,
    term_checkbox: Locator,
):
    term_checkbox.check()
    assert register_button.is_visible()
    assert register_button.is_enabled()


def test_term_unchecked_form_is_not_submittable(
    form_filled_page: Page,
    register_button: Locator,
):
    assert register_button.is_visible()
    assert not register_button.is_enabled()


@pytest.mark.parametrize("form_input_data,missing_field", [
    ({
        k: v for k, v in VALID_DATA.items()
        if k != missing_field
    }, missing_field)
    for missing_field in REQUIRED_FIELDS
])
def test_required_field_not_given_will_not_allow_submit(
    form_filled_page: Page,
    register_button: Locator,
    term_checkbox: Locator,
    missing_field: str,
    form_locator_map: dict,
):
    term_checkbox.check()
    register_button.click()

    locator = form_locator_map[missing_field]

    is_valid = locator.evaluate("el => el.checkValidity()")
    validation_message = locator.evaluate("el => el.validationMessage")
    assert not is_valid
    assert "fill out this field" in validation_message.lower()


def test_password_is_secret(
    form_filled_page: Page,
    password: Locator,
):
    expect(password).to_have_attribute("type", "password")


@pytest.mark.parametrize("form_input_data", [
    VALID_DATA | {
        "password": invalid_password
    }
    for invalid_password in [
        "12345",                # less than 6
        "12345678901234567890"  # more than 19
    ]
])
def test_invalid_password(
    form_filled_page: Page,
    form_input_data: dict,
    register_button: Locator,
    term_checkbox: Locator,
):
    term_checkbox.check()
    register_button.click()

    expect(form_filled_page.locator("#message")).not_to_contain_text("Successfully registered the following information")
    expect(form_filled_page.locator("#message")).to_contain_text("The password should contain between [6,20] characters!")
    class_attr = form_filled_page.locator("#message").get_attribute("class")
    assert "alert-success" not in class_attr.split()
    assert "alert-danger" in class_attr.split()


@pytest.mark.parametrize("form_input_data", [
    VALID_DATA | {
        "phone": invalid_phone
    }
    for invalid_phone in [
        "12345",                # less than 10
        "test1234567890",       # not digits
    ]
])
def test_invalid_phone_number(
    form_filled_page: Page,
    form_input_data: dict,
    register_button: Locator,
    term_checkbox: Locator,
):
    term_checkbox.check()
    register_button.click()

    expect(form_filled_page.locator("#message")).not_to_contain_text("Successfully registered the following information")
    expect(form_filled_page.locator("#message")).to_contain_text(
        "The phone number should contain at least 10 characters and with correct format (ex: 0987654321, +886987654321, +886-987-654-321)"
    )
    class_attr = form_filled_page.locator("#message").get_attribute("class")
    assert "alert-success" not in class_attr.split()
    assert "alert-danger" in class_attr.split()


@pytest.mark.parametrize("form_input_data", [
    VALID_DATA | {
        "email": invalid_email
    }
    for invalid_email in [
        "testme",               # no @domain
        "testme@com",           # only support level 2 domain, ex: testme@domain.com
        "testme@.com",          # domain cannot starts with `.`
        "testme.com",           # no username@
    ]
])
def test_invalid_email(
    form_filled_page: Page,
    form_input_data: dict,
    register_button: Locator,
    term_checkbox: Locator,
):
    term_checkbox.check()
    register_button.click()

    expect(form_filled_page.locator("#message")).not_to_contain_text("Successfully registered the following information")
    expect(form_filled_page.locator("#message")).to_contain_text(
        "Email should have username and @ and valid domain, ex: username@domain.com"
    )
    class_attr = form_filled_page.locator("#message").get_attribute("class")
    assert "alert-success" not in class_attr.split()
    assert "alert-danger" in class_attr.split()


def test_password_hint_wording(form_page: Page):
    expect(form_page.locator("#pwHelp")).to_contain_text("Password length validation: [6,20] characters")
