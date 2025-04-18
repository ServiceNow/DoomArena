import pytest
import os
import gymnasium as gym
from browsergym.core.task import AbstractBrowserTask
import pathlib
from typing import Tuple, Dict
from doomarena.browsergym.attack_gateway import (
    BrowserGymAttackGateway,
)
from doomarena.core.attacks import get_attacks
from doomarena.browsergym.attacks.banner_attacks import (
    get_svg_banner_attack,
)
from browsergym.core import register_task
from doomarena.browsergym.attacks import svg_attack_configs
from doomarena.core.attack_config import AttackConfig
from doomarena.core.filters import AlwaysTrueFilter
from doomarena.core.success_filters import AlwaysTrueSuccessFilter
from doomarena.utils import str2bool
from .utils import DummyBannerAttack, LEFT_BANNER_URI, RIGHT_BANNER_URI


# Create test directory structure
__TEST_DIR = pathlib.Path(__file__).resolve().parent / "test_data"

__HEADLESS = not (str2bool(os.getenv("DISPLAY_BROWSER", False)))


# Write test HTML file
TEST_PAGE = __TEST_DIR / "test_page.html"


# Test task implementation
class BannerTestTask(AbstractBrowserTask):
    @classmethod
    def get_task_id(cls):
        return "BannerTest"

    def __init__(self, seed: int = 0):
        super().__init__(seed)

    def setup(self, page) -> Tuple[str, Dict]:
        page.goto(f"file://{TEST_PAGE}")
        return "Test task", {}

    def validate(self, page, chat_messages):
        return 0, True, "", {}

    def teardown(self):
        pass


class RedditBannerTask(AbstractBrowserTask):
    @classmethod
    def get_task_id(cls):
        return "RedditComment"

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


# w as BannerInjectionConfig
dummy_attack_config = AttackConfig(
    attackable_component={"type": "banner"},
    attack=DummyBannerAttack(),
    filter=AlwaysTrueFilter(),
    success_filter=AlwaysTrueSuccessFilter(),
)

# Register test environments
register_task("banner-test", BannerTestTask)
register_task("reddit-banners", RedditBannerTask)

# script to check for banner elements
valid_script = """
        () => {
            const banners = document.querySelectorAll('.gateway-banner');
            const leftBanner = document.querySelector('.gateway-banner.left');
            const rightBanner = document.querySelector('.gateway-banner.right');
            return {
                totalBanners: banners.length,
                hasLeftBanner: !!leftBanner,
                hasRightBanner: !!rightBanner,
                bannerLoaded: window.GATEWAY_BANNER_LOADED === true || window.GATEWAY_BANNER_UPDATED === true,
            }
        }
    """


def test_security_warning_banner_config():
    """Test that the security warning banner is properly configured."""
    env = gym.make("browsergym/banner-test", headless=__HEADLESS)
    alt_texts = [
        ("left_banner_content_1", "right_banner_content_1"),
        ("left_banner_content_2", "right_banner_content_2"),
    ]
    attack_config = AttackConfig(
        attackable_component={"type": "banner"},
        attack=get_svg_banner_attack(
            banner_configs=svg_attack_configs,
        ),
        filter=AlwaysTrueFilter(),
        success_filter=AlwaysTrueSuccessFilter(),
    )
    gateway = BrowserGymAttackGateway(env, [attack_config], task_name="test_task")
    gateway.reset()
    # Check for banner elements
    has_banners = gateway.env.unwrapped.page.evaluate(valid_script)

    assert has_banners["totalBanners"] == 2, "Should have exactly 2 banners"
    assert has_banners["bannerLoaded"], "Banner loaded flag should be set"
    assert has_banners["hasLeftBanner"], "Left image should be loaded"
    assert has_banners["hasRightBanner"], "Right image should be loaded"
    gateway.close()


@pytest.mark.local
def test_reddit_banners():
    """Test that banners are properly injected into the page."""
    env = gym.make("browsergym/reddit-banners", headless=__HEADLESS)
    gateway = BrowserGymAttackGateway(env, [dummy_attack_config], task_name="test_task")
    gateway.reset()

    # Check for banner elements
    has_banners = gateway.env.unwrapped.page.evaluate(valid_script)

    assert has_banners["totalBanners"] == 2, "Should have exactly 2 banners"
    assert has_banners["bannerLoaded"], "Banner loaded flag should be set"
    assert has_banners["hasLeftBanner"], "Left image should be loaded"
    assert has_banners["hasRightBanner"], "Right image should be loaded"

    gateway.step("goto('http://google.com')")
    # Check for banner elements
    has_banners = gateway.env.unwrapped.page.evaluate(valid_script)

    assert has_banners["totalBanners"] == 2, "Should have exactly 2 banners"
    assert has_banners["bannerLoaded"], "Banner loaded flag should be set"
    assert has_banners["hasLeftBanner"], "Left image should be loaded"
    assert has_banners["hasRightBanner"], "Right image should be loaded"

    gateway.close()


def test_banner_injection():
    """Test that banners are properly injected into the page."""
    env = gym.make("browsergym/banner-test", headless=__HEADLESS)
    gateway = BrowserGymAttackGateway(env, [dummy_attack_config], task_name="test_task")
    gateway.reset()

    # Check for banner elements
    has_banners = gateway.env.unwrapped.page.evaluate(valid_script)

    assert has_banners["totalBanners"] == 2, "Should have exactly 2 banners"
    assert has_banners["bannerLoaded"], "Banner loaded flag should be set"
    assert has_banners["hasLeftBanner"], "Left image should be loaded"
    assert has_banners["hasRightBanner"], "Right image should be loaded"

    gateway.step("noop(0.1)")
    # Check for banner elements
    has_banners = gateway.env.unwrapped.page.evaluate(valid_script)

    assert has_banners["totalBanners"] == 2, "Should have exactly 2 banners"
    assert has_banners["bannerLoaded"], "Banner loaded flag should be set"
    assert has_banners["hasLeftBanner"], "Left image should be loaded"
    assert has_banners["hasRightBanner"], "Right image should be loaded"

    gateway.close()


def test_no_banner_control():
    """Test that environment without attack has no banners."""
    env = gym.make("browsergym/banner-test", headless=__HEADLESS)
    gateway = BrowserGymAttackGateway(env, [], task_name="test_task")
    gateway.reset()

    # Check for banner elements
    has_banners = gateway.env.unwrapped.page.evaluate(valid_script)

    assert (
        has_banners["totalBanners"] == 0
    ), "Should have no banners in control environment"
    assert not has_banners["bannerLoaded"], "Banner loaded flag should not be set"
    assert not has_banners["hasLeftBanner"], "Left banner should not exist"
    assert not has_banners["hasRightBanner"], "Right banner should not exist"

    gateway.step("noop(0.1)")
    has_banners = gateway.env.unwrapped.page.evaluate(valid_script)

    assert has_banners["totalBanners"] == 0, "Should still have no banners after step"
    gateway.close()


def test_banner_persistence():
    """Test that banners persist after page interactions."""
    env = gym.make("browsergym/banner-test", headless=__HEADLESS)
    gateway = BrowserGymAttackGateway(env, [dummy_attack_config], task_name="test_task")
    gateway.reset()

    # Add content and verify banners remain
    gateway.env.unwrapped.page.evaluate(
        "document.body.innerHTML += '<p>New content</p>'"
    )

    has_banners = gateway.env.unwrapped.page.evaluate(valid_script)
    assert has_banners["totalBanners"] == 2, "Should retain 2 banners after DOM changes"
    assert has_banners["bannerLoaded"], "Banner loaded flag should remain set"
    assert has_banners["hasLeftBanner"], "Left banner should remain"
    assert has_banners["hasRightBanner"], "Right banner should remain"

    gateway.step("noop(0.1)")
    has_banners = gateway.env.unwrapped.page.evaluate(valid_script)

    assert has_banners["totalBanners"] == 2, "Should still have 2 banners after step"
    assert has_banners["bannerLoaded"], "Banner loaded flag should still be set"
    assert has_banners["hasLeftBanner"], "Left banner should still exist"
    assert has_banners["hasRightBanner"], "Right banner should still exist"

    gateway.close()


def test_get_elements_by_class_name():
    """Test that get_attackable_banner_elements returns correct elements."""
    env = gym.make("browsergym/banner-test", headless=__HEADLESS)
    gateway = BrowserGymAttackGateway(env, [dummy_attack_config], task_name="test_task")
    gateway.reset()

    attacked_elements = gateway.get_elements_by_class_name("gateway-banner")
    assert len(attacked_elements) == 2, "Should identify 2 attackable elements"

    gateway.step("noop(0.1)")
    attacked_elements = gateway.get_elements_by_class_name("gateway-banner")
    assert (
        len(attacked_elements) == 2
    ), "Should still identify 2 attackable elements after step"

    gateway.close()
