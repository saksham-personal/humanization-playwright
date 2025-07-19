# Humanization-Patchright

[![PyPI version](https://badge.fury.io/py/Humanization-patchright.svg)](https://badge.fury.io/py/Humanization-patchright)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  

A Python library for simulating human-like browser interactions (mouse movements, typing, clicking, etc.) in automation scripts. Built on top of [Patchright](https://pypi.org/project/patchright/), a patched and undetected version of Playwright, this library helps evade bot detection by adding randomness, Bezier curve-based mouse paths, variable delays, and other human-mimicking behaviors. Ideal for web scraping, testing, or automation tasks requiring stealth.

## Features

- **Human-like Mouse Movements**: Uses cubic Bezier curves with jitter and pauses for natural paths.
- **Typing and Backspacing**: Variable speeds, pauses after spaces, and occasional hesitations.
- **Clicking and Hovering**: Supports left/right/middle clicks with delays.
- **Scrolling and Dragging**: Smooth, inertia-based scrolling and drag-and-drop.
- **Stealth Integration**: Leverages Patchright's patches for undetection (e.g., Runtime.enable leak fixes).
- **Configurable**: Adjust speed, humanization level, typing CPM, and stealth mode.
- **Async Support**: Fully asynchronous for efficient Playwright/Patchright usage.
- **New Additions**: Human waits, mouse overshoot corrections, and more for enhanced realism.

This library is designed as a drop-in enhancement for Patchright scripts, focusing on Chromium-based browsers (Firefox/Webkit not supported).

## Installation

Install via PyPI:

```bash
pip install Humanization-patchright
```

After installation, set up Patchright's browser for optimal undetection:

```bash
patchright install chrome  # Recommended for better stealth than Chromium
```

**Requirements**:
- Python 3.8+
- Patchright (automatically installed as a dependency)
- Loguru (for logging, also a dependency)

No additional packages needed; avoid installing extras to maintain stealth.

## Usage

### Basic Example

Launch a stealthy browser and perform human-like actions:

```python
import asyncio
from Humanization import Humanization, HumanizationConfig

async def main():
    # Configure for slow, highly humanized actions with stealth
    config = HumanizationConfig(
        fast=False,
        humanize=True,
        characters_per_minute=400,
        backspace_cpm=800,
        timeout=10000,
        stealth_mode=True
    )
    
    # Launch undetected context (uses Patchright recommendations)
    Humanization = await Humanization.undetected_launch("/path/to/user_data_dir", config)
    
    # Navigate to a site
    await Humanization.page.goto("https://example.com")
    
    # Locate an element
    search_input = Humanization.page.locator("input#search")
    
    # Human-like typing
    await Humanization.type_at(search_input, "Hello, world!")
    
    # Human-like click
    submit_button = Humanization.page.locator("button#submit")
    await Humanization.click_at(submit_button)
    
    # Scroll down with inertia
    await Humanization.scroll_to(delta_y=500)
    
    # Drag-and-drop example
    draggable = Humanization.page.locator("#draggable")
    dropzone = Humanization.page.locator("#dropzone")
    await Humanization.drag_to(draggable, dropzone)
    
    # Random human pause
    await Humanization.human_wait(min_sec=2, max_sec=5)
    
    # Close the context
    await Humanization.page.context.close()

asyncio.run(main())
```

### Advanced Configuration

The `HumanizationConfig` dataclass allows fine-tuning:

- `fast`: bool - Use fewer steps and shorter delays for quicker actions (default: True).
- `humanize`: bool - Add jitter, pauses, and hesitations (default: True).
- `characters_per_minute`: float - Typing speed (default: 600).
- `backspace_cpm`: float - Backspacing speed (default: 1200).
- `timeout`: float - Milliseconds for element visibility/focus checks (default: 5000).
- `stealth_mode`: bool - Apply Patchright's undetection defaults (default: True).

Pass custom params to methods, e.g.:

```python
await Humanization.move_to(locator, offset_x=10, offset_y=20, input_mode=True)
```

### Stealth Best Practices

- Always use `Humanization.undetected_launch` for persistent contexts.
- Run headless=False and avoid custom user agents/headers.
- Combine with Patchright's Chrome channel for maximum undetection.
- Test on anti-bot sites to verify.

## API Reference

### Core Class: `Humanization`

- `__init__(self, page: Page, config: Optional[HumanizationConfig] = None)`
- `undetected_launch(cls, user_data_dir: str, config: Optional[HumanizationConfig] = None)`: Class method for stealth launch.

### Key Methods

- `move_to(locator: Locator, offset_x: Optional[int] = None, offset_y: Optional[int] = None, input_mode: bool = False) -> Tuple[float, float]`: Move mouse to element.
- `click_at(locator: Locator, clicktype: str = "left", input_mode: bool = False)`: Click after moving.
- `type_at(locator: Locator, text: str, ...)`: Type text human-like.
- `backspace_at(locator: Locator, num_chars: int, ...)`: Backspace characters.
- `hover_at(locator: Locator, dwell_time: float = 0.5)`: Hover with dwell.
- `scroll_to(locator: Optional[Locator] = None, delta_y: Optional[int] = None)`: Scroll to element or by delta.
- `human_wait(min_sec: float = 1.0, max_sec: float = 3.0)`: Random pause.
- `drag_to(source_locator: Locator, target_locator: Locator)`: Drag and drop.
- `human_correct(locator: Locator, overshoot_factor: float = 1.2)`: Overshoot and correct mouse.
- `random_delay() -> float`: Utility for 0.7-1.0s delay.
- `get_box(locator: Locator) -> Dict[str, float]`: Get element bounding box.
- `get_page_dimensions() -> Dict[str, float]`: Get page size.

Full docs in code comments.

## Logging

Uses Loguru for debug/info/error logs. Logs to `Humanization.log` by default (rotates at 10 MB).

## Development and Contributing

1. Clone the repo: `git clone https://github.com/yourusername/Humanization-patchright.git`
2. Install editable: `pip install -e .`
3. Run tests: `pytest` (add dev deps like pytest if needed).
4. Build: `python -m build`

Contributions welcome! Open issues/PRs on GitHub for bugs/features.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
