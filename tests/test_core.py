# tests/test_core.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from humanization.core import Humanization, HumanizationConfig
from playwright.async_api import Page, Locator  

@pytest.mark.asyncio
async def test_config_defaults():
    config = HumanizationConfig()
    assert config.fast is True
    assert config.humanize is True
    assert config.stealth_mode is True
    assert config.characters_per_minute == 600

def test_cubic_bezier():
    # Test pure math function
    h = Humanization(None)  # Page can be None for non-browser tests
    p0 = (0, 0)
    p1 = (100, 100)
    p2 = (200, 200)
    p3 = (300, 300)
    # At t=0.5, should be midpoint on linear but curved here
    point = h.cubic_bezier(0.5, p0, p1, p2, p3)
    assert point == (150.0, 150.0)

def test_generate_bezier_points():
    h = Humanization(None)
    p0 = (0, 0)
    p3 = (100, 100)
    points = h.generate_bezier_points(p0, p3, steps=3)
    assert len(points) == 3
    assert points[0] == (0, 0)
    assert points[-1] == (100, 100)
    # Middle point should be between start and end
    mid = points[1]
    assert 0 < mid[0] < 100
    assert 0 < mid[1] < 100

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
    config = HumanizationConfig(fast=True)
    h = Humanization(mock_page, config)
    target = await h.move_to(mock_locator)
    assert isinstance(target, tuple)
    assert len(target) == 2
    # Should have moved the mouse multiple times
    assert mock_page.mouse.move.call_count > 1

@pytest.mark.asyncio
async def test_type_at(mock_page, mock_locator):
    config = HumanizationConfig()
    h = Humanization(mock_page, config)
    await h.type_at(mock_locator, "test")
    # One press per character
    assert mock_page.keyboard.press.call_count == 4

# Optional: tests for click_at, backspace_at, hover_at, etc.

@pytest.mark.skip("Requires real browser; run locally")
@pytest.mark.asyncio
async def test_undetected_launch():
    config = HumanizationConfig()
    h = await Humanization.undetected_launch("/tmp/user_data", config)
    assert h.page is not None
    await h.page.context.close()
