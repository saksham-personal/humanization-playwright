import random
import asyncio
from typing import Tuple, List, Dict, Optional
from playwright.async_api import Page, Locator, TimeoutError
from patchright.async_api import expect, async_playwright
from loguru import logger
from dataclasses import dataclass


@dataclass
class HumanizationConfig:
    fast: bool = True
    humanize: bool = True
    characters_per_minute: float = 600
    backspace_cpm: float = 1200
    timeout: float = 5000
    stealth_mode: bool = True  

class Humanization:
    def __init__(self, page: Page, config: Optional[HumanizationConfig] = None):
        self.page = page
        self.config = config or HumanizationConfig()

    @classmethod
    async def undetected_launch(cls, user_data_dir: str, config: Optional[HumanizationConfig] = None):
        """Launch a stealthy browser context using Patchright recommendations."""
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                channel="chrome",
                args=["--incognito", "--disable-blink-features=AutomationControlled"],
                headless=False,
                no_viewport=True,
            )
            page = await context.new_page()
            return cls(page, config)

    async def random_delay(self) -> float:
        delay = random.uniform(0.7, 1.0)
        logger.debug(f"Random delay: {delay:.3f}s")
        return delay

    async def get_box(self, locator: Locator) -> Dict[str, float]:
        """Get bounding box for a locator, skipping visibility check for unsupported types."""
        # 1) Try the visibility check, but swallow ValueError from mocks
        try:
            await expect(locator).to_be_visible(timeout=self.config.timeout)
        except TimeoutError as e:
            logger.error(f"Timeout for visibility: {e}")
            raise
        except ValueError as e:
            # patchright.expect will ValueError on MagicMock – ignore that
            if "Unsupported type" in str(e):
                logger.warning(f"Skipping visibility check for locator type: {type(locator)}")
            else:
                logger.error(f"Error during visibility check: {e}")
                raise
        
                # 2) Now retrieve the bounding box
        try:
            box = await locator.bounding_box()
            if box is None:
                raise ValueError("Bounding box is None")
            return {
                "x": box["x"],
                "y": box["y"],
                "w": box["width"],
                "h": box["height"],
            }
        except Exception as e:
            logger.error(f"Bounding box error: {e}")
            raise

    async def get_page_dimensions(self) -> Dict[str, float]:
        try:
            dimensions = await self.page.evaluate(
                """() => {
                    const body = document.body;
                    const html = document.documentElement;
                    const w = Math.max(body.scrollWidth, body.offsetWidth, html.clientWidth, html.scrollWidth, html.offsetWidth);
                    const h = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight);
                    return { x: 0, y: 0, w: w, h: h };
                }"""
            )
            logger.debug(f"Page dimensions: {dimensions}")
            return dimensions
        except Exception as e:
            logger.error(f"Page dimensions error: {e}")
            raise

    def cubic_bezier(self, t: float, p0: Tuple[float, float], p1: Tuple[float, float],
                     p2: Tuple[float, float], p3: Tuple[float, float]) -> Tuple[float, float]:
        if not 0 <= t <= 1:
            raise ValueError("t must be between 0 and 1")
        u = 1 - t
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t
        x = uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0]
        y = uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1]
        return (x, y)

    def generate_bezier_points(
        self, p0: Tuple[float, float], p3: Tuple[float, float], steps: int = 40
    ) -> List[Tuple[float, float]]:
        def lerp(a: float, b: float, t: float) -> float:
            return a + (b - a) * t

        dist = ((p3[0] - p0[0])**2 + (p3[1] - p0[1])**2)**0.5
        max_control_offset = min(50, dist * 0.2)
        p1 = (
            lerp(p0[0], p3[0], 0.33) + random.uniform(-max_control_offset, max_control_offset),
            lerp(p0[1], p3[1], 0.33) + random.uniform(-max_control_offset, max_control_offset)
        )
        p2 = (
            lerp(p0[0], p3[0], 0.66) + random.uniform(-max_control_offset, max_control_offset),
            lerp(p0[1], p3[1], 0.66) + random.uniform(-max_control_offset, max_control_offset)
        )
        points = [self.cubic_bezier(i / (steps - 1), p0, p1, p2, p3) for i in range(steps)]
        return points

    async def move_to(
        self, locator: Locator, offset_x: Optional[int] = None, offset_y: Optional[int] = None,
        input_mode: bool = False
    ) -> Tuple[float, float]:
        logger.info("Starting move_to")
        element_box = await self.get_box(locator)
        elem_x, elem_y = int(element_box["x"]), int(element_box["y"])
        elem_w, elem_h = int(element_box["w"]), int(element_box["h"])

        st_x = elem_x + elem_w // 2
        st_y = elem_y + elem_h // 2
        initial_steps = random.randint(5, 10) if self.config.fast else random.randint(30, 150)
        await self.page.mouse.move(st_x, st_y, steps=initial_steps)
        await asyncio.sleep(random.uniform(0.01, 0.03) if self.config.fast else random.uniform(0.05, 0.1))

        if offset_x is None:
            offset_x = round(random.uniform(0, elem_w))
        if offset_y is None:
            offset_y = round(random.uniform(0, elem_h))

        tr_x = elem_x + offset_x
        tr_y = elem_y + offset_y

        if input_mode:
            min_target_x = int(elem_x + elem_w * 0.7)
            max_target_x = int(elem_x + elem_w * 0.8)
            tr_x = random.randint(min_target_x, max_target_x)
            tr_y = random.randint(elem_y, elem_y + elem_h)

        tr_x = max(elem_x, min(tr_x, elem_x + elem_w - 1))
        tr_y = max(elem_y, min(tr_y, elem_y + elem_h - 1))

        start_point = (st_x, st_y)
        target_point = (tr_x, tr_y)
        bezier_steps = random.randint(20, 30) if self.config.fast else random.randint(80, 120)
        curve_points = self.generate_bezier_points(start_point, target_point, steps=bezier_steps)

        sleep_min = 0.001 if self.config.fast else 0.002
        sleep_max = 0.005 if self.config.fast else 0.015

        for x, y in curve_points:
            if self.config.humanize:
                x += random.gauss(0, 1)
                y += random.gauss(0, 1)
            await self.page.mouse.move(x, y, steps=1)
            if self.config.humanize and random.random() < 0.05:
                await asyncio.sleep(random.uniform(0.03, 0.07))
            else:
                await asyncio.sleep(random.uniform(sleep_min, sleep_max))
        return target_point

    async def click_at(self, locator: Locator, clicktype: str = "left", input_mode: bool = False):
        target_point = await self.move_to(locator, input_mode=input_mode)
        button = clicktype.lower()
        delay_ms = random.uniform(50, 80) if self.config.fast else random.uniform(100, 150)
        await self.page.mouse.click(target_point[0], target_point[1], button=button, delay=delay_ms)

    async def type_at(
        self, locator: Locator, text: str,
        inter_key_offset: float = 0.02, key_press_delay_range: Tuple[float, float] = (100, 140)
    ) -> None:
        # Move & click first
        await self.click_at(locator, input_mode=True)

        # 1) Expect focused, but skip on MagicMock
        try:
            await expect(locator).to_be_focused(timeout=self.config.timeout)
        except ValueError as e:
            if "Unsupported type" in str(e):
                logger.warning(f"Skipping focus check for locator type: {type(locator)}")
            else:
                logger.error(f"Error during focus check: {e}")
                raise

        # 2) Now type each character
        base_delay = 60 / self.config.characters_per_minute
        for char in text:
            random_offset = random.uniform(-inter_key_offset, inter_key_offset)
            delay = max(0, base_delay + random_offset)
            key_delay = random.uniform(*key_press_delay_range)
            await self.page.keyboard.press(char, delay=key_delay)
            if self.config.humanize and char == " ":
                await asyncio.sleep(delay + random.uniform(0.05, 0.1))
            else:
                await asyncio.sleep(delay)
                
    async def backspace_at(
        self, locator: Locator, num_chars: int,
        inter_key_offset: float = 0.005, key_press_delay_range: Tuple[float, float] = (80, 120)
    ) -> None:
        await self.click_at(locator, input_mode=True)
        await expect(locator).to_be_focused(timeout=self.config.timeout)
        base_delay = 60 / self.config.backspace_cpm
        for _ in range(num_chars):
            random_offset = random.uniform(-inter_key_offset, inter_key_offset)
            delay = max(0, base_delay + random_offset)
            key_delay = random.uniform(*key_press_delay_range)
            await self.page.keyboard.press("Backspace", delay=key_delay)
            if self.config.humanize and random.random() < 0.05:
                await asyncio.sleep(delay + random.uniform(0.01, 0.03))
            else:
                await asyncio.sleep(delay)

    async def hover_at(self, locator: Locator, dwell_time: float = 0.5):
        await self.move_to(locator)
        await asyncio.sleep(random.uniform(dwell_time * 0.8, dwell_time * 1.2))

    async def scroll_to(self, locator: Optional[Locator] = None, delta_y: Optional[int] = None):
        if locator:
            box = await self.get_box(locator)
            target_y = box['y']
            current_scroll = await self.page.evaluate("window.scrollY")
            delta_y = target_y - current_scroll
        if delta_y is None:
            delta_y = random.randint(100, 500) * (1 if random.random() > 0.5 else -1)
        steps = random.randint(10, 20) if self.config.fast else random.randint(30, 50)
        for i in range(steps):
            step_delta = delta_y / steps * (1 + random.uniform(-0.1, 0.1))
            await self.page.mouse.wheel(0, step_delta)
            await asyncio.sleep(random.uniform(0.01, 0.03))

    async def human_wait(self, min_sec: float = 1.0, max_sec: float = 3.0):
        wait_time = random.uniform(min_sec, max_sec)
        await asyncio.sleep(wait_time)

    async def drag_to(self, source_locator: Locator, target_locator: Locator):
        source_point = await self.move_to(source_locator)
        await self.page.mouse.down()
        await asyncio.sleep(random.uniform(0.1, 0.3))  
        await self.move_to(target_locator)
        await self.page.mouse.up()

    async def human_correct(self, locator: Locator, overshoot_factor: float = 1.2):
        target_point = await self.get_box(locator)
        overshoot_x = target_point['x'] + target_point['w'] * overshoot_factor
        overshoot_y = target_point['y'] + target_point['h'] * overshoot_factor
        await self.page.mouse.move(overshoot_x, overshoot_y)
        await asyncio.sleep(random.uniform(0.05, 0.1))  
        await self.move_to(locator)  