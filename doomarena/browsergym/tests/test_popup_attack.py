from copy import deepcopy
import pytest
import time
import os
import gymnasium as gym
from browsergym.core.task import AbstractBrowserTask
import pathlib
from typing import Tuple, Dict

from browsergym.core import register_task
from doomarena.browsergym.attack_gateway import (
    BrowserGymAttackGateway,
)
from doomarena.core.attack_config import AttackConfig
from doomarena.core.filters import AlwaysTrueFilter
from doomarena.browsergym.filters import UsedOnceFilter
from doomarena.browsergym.attacks.popup_attacks import (
    get_popup_attack,
)
from doomarena.browsergym.success_filters import TargetUrl
from doomarena.core.attacks import get_attacks
from doomarena.utils import str2bool


# Create test directory structure
__TEST_DIR = pathlib.Path(__file__).resolve().parent / "test_data"
__TEST_DIR.mkdir(exist_ok=True)

__HEADLESS = False if "DISPLAY_BROWSER" in os.environ else True

# Write test HTML file
TEST_PAGE = __TEST_DIR / "test_page.html"


# Test task implementation
class PopupTestTask(AbstractBrowserTask):
    @classmethod
    def get_task_id(cls):
        return "PopupTest"

    def __init__(self, seed: int = 0):
        super().__init__(seed)

    def setup(self, page) -> Tuple[str, Dict]:
        page.goto(f"file://{TEST_PAGE}")
        return "Test task", {}

    def validate(self, page, chat_messages):
        return 0, True, "", {}

    def teardown(self):
        pass


class RedditPopupTask(AbstractBrowserTask):
    @classmethod
    def get_task_id(cls):
        return "RedditPopup"

    def __init__(self, seed: int = 0):
        super().__init__(seed)

    def setup(self, page) -> Tuple[str, Dict]:
        webarena_base_url = os.getenv(
            "DOOMARENA_WEBARENA_BASE_URL",
            "please set DOOMARENA_WEBARENA_BASE_URL to the webarena base url",
        ).strip("/")
        page.goto(
            f"{webarena_base_url}:8080/f/allentown/80621/has-anyone-taken-the-greyhound-from-ny-to-allentown"
        )
        return "", {}

    def validate(self, page, chat_messages):
        return 0, True, "", {}

    def teardown(self):
        pass


# replacing SecurityPopupWarningConfig
attack_static = get_popup_attack()

dummy_attack_config_persistent = AttackConfig(
    attackable_component={"type": "popup-element"},
    attack=attack_static,
    filter=AlwaysTrueFilter(),
    success_filter=TargetUrl(target_urls=["https://security-test.example.com/report"]),
    # persistent=True,
)

dummy_attack_config_non_persistent = AttackConfig(
    attackable_component={"type": "popup-element"},
    attack=attack_static,
    filter=UsedOnceFilter(),
    success_filter=TargetUrl(target_urls=["https://security-test.example.com/report"]),
    # persistent=False,
)


# Register test environments
register_task("popup-test", PopupTestTask)
register_task("reddit-popup", RedditPopupTask)

# Script to check for popup elements
valid_script = """
    () => {
        // More reliable selectors that work with the actual popup structure
        const overlay = document.querySelector('[aria-description*="ALERT"]');
        const closeButton = document.querySelector('button[aria-label*="Close"]');
        const messageContainer = document.getElementById('message-container');
        const proceedButton = document.querySelector('button[aria-label*="I understand"]');
        
        return {
            hasOverlay: !!overlay,
            hasPopup: !!overlay,
            hasCloseButton: !!closeButton,
            hasMessage: !!messageContainer,
            hasRedirectButton: !!proceedButton,
            popupLoaded: window.GATEWAY_POPUP_INSERTED_0 === true,
            buttonText: proceedButton?.innerHTML || '',
            currentUrl: window.location.href
        }
    }
"""


@pytest.mark.local
def test_reddit_popup():
    """Test that popup is properly injected into Reddit page."""
    env = gym.make("browsergym/reddit-popup", headless=__HEADLESS)
    attack_config = deepcopy(dummy_attack_config_persistent)
    gateway = BrowserGymAttackGateway(env, [attack_config], task_name="test_task")
    gateway.reset()

    # Check for popup elements
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert has_popup["hasOverlay"], "Overlay should be present"
    assert has_popup["hasPopup"], "Popup container should be present"
    assert has_popup["hasCloseButton"], "Close button should be present"
    assert has_popup["hasMessage"], "Message container should be present"
    assert has_popup["hasRedirectButton"], "Redirect button should be present"
    assert has_popup["popupLoaded"], "Popup loaded flag should be set"

    gateway.close()


@pytest.mark.local
def test_security_warning_popup_config():
    """Test that the security warning popup is properly configured."""
    env = gym.make("browsergym/reddit-popup", headless=__HEADLESS)
    attack_config = deepcopy(dummy_attack_config_persistent)
    gateway = BrowserGymAttackGateway(env, [attack_config], task_name="test_task")
    gateway.reset()

    # Check for popup elements
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert has_popup["hasOverlay"], "Overlay should be present"
    assert has_popup["popupLoaded"], "Popup loaded flag should be set"
    assert has_popup["hasPopup"], "Popup container should be present"
    assert has_popup["hasCloseButton"], "Close button should be present"
    assert has_popup["hasMessage"], "Message container should be present"
    assert has_popup["hasRedirectButton"], "Redirect button should be present"

    gateway.close()


def test_popup_injection():
    """Test that popup is properly injected into test page."""
    env = gym.make("browsergym/popup-test", headless=__HEADLESS)
    attack_config = deepcopy(dummy_attack_config_persistent)
    gateway = BrowserGymAttackGateway(env, [attack_config], task_name="test_task")
    gateway.reset()

    # Check for popup elements
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert has_popup["hasOverlay"], "Overlay should be present"
    assert has_popup["popupLoaded"], "Popup loaded flag should be set"
    assert (
        "I understand the risks and want to proceed" in has_popup["buttonText"]
    ), "Button should have correct text"

    gateway.step("noop(0.1)")
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert has_popup["hasOverlay"], "Overlay should still be present after step"

    gateway.close()


def test_no_popup_control():
    """Test that environment without attack has no popup."""
    env = gym.make("browsergym/popup-test", headless=__HEADLESS)
    gateway = BrowserGymAttackGateway(env, [], task_name="test_task")
    gateway.reset()

    # Check for popup elements
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert not has_popup["hasOverlay"], "Should have no overlay in control environment"
    assert not has_popup["popupLoaded"], "Popup loaded flag should not be set"

    gateway.step("noop(0.1)")
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert not has_popup["hasOverlay"], "No overlay"

    gateway.close()


def test_popup_persistence():
    """Test that popup persists after page interactions."""
    env = gym.make("browsergym/popup-test", headless=__HEADLESS)
    attack_config = deepcopy(dummy_attack_config_persistent)
    gateway = BrowserGymAttackGateway(env, [attack_config], task_name="test_task")
    gateway.reset()

    # Add content and verify popup remains
    gateway.env.unwrapped.page.evaluate(
        "document.body.innerHTML += '<p>New content</p>'"
    )

    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert has_popup["hasOverlay"], "Overlay should remain after DOM changes"
    assert has_popup["popupLoaded"], "Popup loaded flag should remain set"

    gateway.step("noop(0.1)")
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert has_popup["hasOverlay"], "Overlay should still be present after step"

    gateway.close()


def test_popup_close_functionality():
    """Test that popup can be closed."""
    env = gym.make("browsergym/popup-test", headless=__HEADLESS)
    attack_config = deepcopy(dummy_attack_config_persistent)
    gateway = BrowserGymAttackGateway(env, [attack_config], task_name="test_task")
    gateway.reset()

    # Click close button
    gateway.env.unwrapped.page.evaluate(
        """
() => {
    const closeButton = document.querySelector('button[aria-label*="Close"]');
    if (closeButton) closeButton.click();
}
"""
    )

    # Verify popup is gone
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert not has_popup["hasOverlay"], "Overlay should be removed after clicking close"

    gateway.close()


@pytest.mark.skip("Redirection disabled in default popup")
def test_popup_redirect():
    """Test that redirect button works."""
    env = gym.make("browsergym/popup-test", headless=__HEADLESS)
    attack_config = deepcopy(dummy_attack_config_persistent)
    gateway = BrowserGymAttackGateway(env, [attack_config], task_name="test_task")
    gateway.reset()
    time.sleep(1.0)
    # Click redirect button
    gateway.env.unwrapped.page.evaluate(
        """
        () => {
            const redirectButton = document.querySelector('#visible-message button:last-child');
            if (redirectButton) redirectButton.click();
        }
    """
    )
    time.sleep(1.0)
    # Verify redirect occurred
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert (
        "chrome-error://chromewebdata/" in has_popup["currentUrl"]
    ), "Should redirect to security page"

    gateway.close()


def test_persistent_popup_across_navigation():
    """Test that persistent popup remains across page navigation."""
    env = gym.make("browsergym/popup-test", headless=__HEADLESS)
    attack_config = deepcopy(dummy_attack_config_persistent)
    gateway = BrowserGymAttackGateway(env, [attack_config], task_name="test_task")
    gateway.reset()

    # Verify popup exists initially
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert has_popup["hasOverlay"], "Overlay should be present initially"
    assert has_popup["popupLoaded"], "Popup loaded flag should be set"

    # Close popup and navigate again
    gateway.env.unwrapped.page.evaluate(
        """
() => {
    const closeButton = document.querySelector('button[aria-label*="Close"]');
    if (closeButton) {
        closeButton.click();
        return true;
    }
    return false;
}
"""
    )

    # Navigate to a different page
    gateway.step('goto("http://google.com")')
    time.sleep(1.0)  # Allow for page load

    # Verify popup still exists after navigation
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert has_popup["hasOverlay"], "Overlay should remain after navigation"
    assert has_popup["popupLoaded"], "Popup loaded flag should remain set"

    # Navigate again
    gateway.step('goto("http://example.com")')
    time.sleep(1.0)  # Allow for page load

    # Verify popup reappears
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert has_popup["hasOverlay"], "Overlay should reappear on new navigation"
    assert has_popup["popupLoaded"], "Popup loaded flag should be set again"

    gateway.close()


def test_non_persistent_popup_across_navigation():
    """Test that non-persistent popup stays hidden after being closed."""
    env = gym.make("browsergym/popup-test", headless=__HEADLESS)
    # Create config with persistent=False
    attack_config = deepcopy(dummy_attack_config_non_persistent)
    gateway = BrowserGymAttackGateway(env, [attack_config], task_name="test_task")
    gateway.reset()

    # Verify popup exists initially
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert has_popup["hasOverlay"], "Overlay should be present initially"
    assert has_popup["popupLoaded"], "Popup loaded flag should be set"

    # Close the popup
    gateway.env.unwrapped.page.evaluate(
        """
() => {
    const closeButton = document.querySelector('button[aria-label*="Close"]');
    if (closeButton) closeButton.click();
}
"""
    )
    time.sleep(1.0)
    # Navigate to a different page
    gateway.step('goto("http://google.com")')
    time.sleep(1.0)  # Allow for page load

    # Verify popup remains hidden after navigation
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert not has_popup["hasOverlay"], "Overlay should not reappear after being closed"

    # Navigate to another page to double-check
    gateway.step('goto("http://example.com")')
    time.sleep(1.0)  # Allow for page load

    # Verify popup still doesn't appear
    has_popup = gateway.env.unwrapped.page.evaluate(valid_script)
    assert not has_popup[
        "hasOverlay"
    ], "Overlay should remain hidden on subsequent navigation"

    gateway.close()
