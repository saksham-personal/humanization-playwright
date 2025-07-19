# tests/test_core.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from humanizer import Humanizer, HumanizerConfig
from playwright.async_api import Page, Locator  

@pytest.mark.asyncio
async def test_config_defaults():
    config = HumanizerConfig()
    assert config.fast is True
    assert config.humanize is True
    assert config.stealth_mode is True
    assert config.characters_per_minute == 600

def test_cubic_bezier():
    # Test pure math function
    h = Humanizer(None)  # Page can be None for non-browser tests
    p0 = (0, 0)
    p1 = (100, 100)
    p2 = (200, 200)
    p3 = (300, 300)
    # At t=0.5, should be midpoint on linear but curved here
    point = h.cubic_bezier(0.5, p0, p1, p2, p3)
    assert point == (150.0, 150.0)  # Expected for this control setup

def test_generate_bezier_points():
    h = Humanizer(None)
    p0 = (0, 0)
    p3 = (100, 100)
    points = h.generate_bezier_points(p0, p3, steps=3)
    assert len(points) == 3
    assert points[0] == (0, 0)  # Start
    assert points[-1] == (100, 100)  # End
    # Middle point should be somewhere in between with offset

@pytest.fixture
def mock_page():
    page = AsyncMock(spec=Page)
    page.mouse = AsyncMock()
    page.keyboard = AsyncMock()
    page.evaluate = AsyncMock(return_value={"x": 0, "y": 0, "w": 1000, "h": 1000})
    return page

@pytest.fixture
def mock_locator():
    locator = MagicMock(spec=Locator)
    locator.bounding_box = AsyncMock(return_value={"x": 10, "y": 10, "width": 100, "height": 50})
    return locator

@pytest.mark.asyncio
async def test_move_to(mock_page, mock_locator):
    config = HumanizerConfig(fast=True)
    h = Humanizer(mock_page, config)
    target = await h.move_to(mock_locator)
    assert isinstance(target, tuple)
    assert len(target) == 2
    # Check if mouse.move was called multiple times
    assert mock_page.mouse.move.call_count > 1

@pytest.mark.asyncio
async def test_type_at(mock_page, mock_locator):
    config = HumanizerConfig()
    h = Humanizer(mock_page, config)
    await h.type_at(mock_locator, "test")
    # Verify keyboard presses
    assert mock_page.keyboard.press.call_count == 4  # One per char

# Add more tests for other methods like click_at, drag_to, etc.

@pytest.mark.skip("Requires real browser; run locally")
@pytest.mark.asyncio
async def test_undetected_launch():
    config = HumanizerConfig()
    h = await Humanizer.undetected_launch("/tmp/test_user_data", config)
    assert h.page is not None
    await h.page.context.close()