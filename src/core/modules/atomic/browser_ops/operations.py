"""
Browser Automation Modules

Provides browser automation capabilities using Playwright.
All modules use i18n keys for multi-language support.
"""
from typing import Any, Dict
from ...base import BaseModule
from ...registry import register_module


@register_module(
    module_id='core.browser.launch',
    version='1.0.0',
    category='browser',
    tags=['browser', 'automation', 'setup'],
    label='Launch Browser',
    label_key='modules.browser.launch.label',
    description='Launch a new browser instance with Playwright',
    description_key='modules.browser.launch.description',
    icon='Monitor',
    color='#4A90E2',

    # Connection types
    input_types=['any'],
    output_types=['any'],

    # Phase 2: Execution settings
    timeout=10,  # Browser launch should complete within 10s
    retryable=True,  # Can retry if browser fails to launch
    max_retries=2,  # Don't retry too many times (resource intensive)
    concurrent_safe=False,  # Browser instances should not launch in parallel

    # Phase 2: Security settings
    requires_credentials=False,
    handles_sensitive_data=False,
    required_permissions=['browser.launch', 'system.process'],

    params_schema={
        'headless': {
            'type': 'boolean',
            'label': 'Headless Mode',
            'label_key': 'modules.browser.launch.params.headless.label',
            'description': 'Run browser in headless mode (no UI)',
            'description_key': 'modules.browser.launch.params.headless.description',
            'default': False,
            'required': False
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'message': {'type': 'string'}
    },
    examples=[
        {
            'name': 'Launch headless browser',
            'params': {'headless': True}
        },
        {
            'name': 'Launch visible browser',
            'params': {'headless': False}
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class BrowserLaunchModule(BaseModule):
    """Launch Browser Module"""

    module_name = "Launch Browser"
    module_description = "Launch a new browser instance"
    required_permission = "browser.launch"

    def validate_params(self):
        self.headless = self.params.get('headless', False)

    async def execute(self) -> Any:
        from src.core.browser.driver import BrowserDriver

        driver = BrowserDriver(headless=self.headless)
        await driver.launch()

        # Store in context for later use
        self.context['browser'] = driver

        return {"status": "success", "message": "Browser launched successfully"}


@register_module(
    module_id='core.browser.goto',
    version='1.0.0',
    category='browser',
    tags=['browser', 'navigation', 'url'],
    label='Go to URL',
    label_key='modules.browser.goto.label',
    description='Navigate to a specific URL',
    description_key='modules.browser.goto.description',
    icon='Globe',
    color='#5CB85C',
    params_schema={
        'url': {
            'type': 'string',
            'label': 'URL',
            'label_key': 'modules.browser.goto.params.url.label',
            'placeholder': 'https://example.com',
            'description': 'The URL to navigate to',
            'description_key': 'modules.browser.goto.params.url.description',
            'required': True
        },
        'wait_until': {
            'type': 'select',
            'label': 'Wait Condition',
            'label_key': 'modules.browser.goto.params.wait_until.label',
            'options': [
                {
                    'value': 'load',
                    'label': 'Page Load Complete',
                    'label_key': 'modules.browser.goto.params.wait_until.options.load'
                },
                {
                    'value': 'networkidle',
                    'label': 'Network Idle',
                    'label_key': 'modules.browser.goto.params.wait_until.options.networkidle'
                },
                {
                    'value': 'domcontentloaded',
                    'label': 'DOM Content Loaded',
                    'label_key': 'modules.browser.goto.params.wait_until.options.domcontentloaded'
                }
            ],
            'default': 'networkidle',
            'description': 'Condition to wait for page loading',
            'description_key': 'modules.browser.goto.params.wait_until.description',
            'required': False
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'url': {'type': 'string'}
    },
    examples=[
        {
            'name': 'Navigate to Google',
            'params': {
                'url': 'https://www.google.com',
                'wait_until': 'networkidle'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class BrowserGotoModule(BaseModule):
    """Navigate to URL Module"""

    module_name = "Go to URL"
    module_description = "Navigate to a specific URL"
    required_permission = "browser.navigate"

    def validate_params(self):
        if 'url' not in self.params:
            raise ValueError("Missing required parameter: url")
        self.url = self.params['url']

    async def execute(self) -> Any:
        browser = self.context.get('browser')
        if not browser:
            raise RuntimeError("Browser not launched. Please run browser.launch first")

        await browser.goto(self.url)
        return {"status": "success", "url": self.url}


@register_module(
    module_id='core.browser.click',
    version='1.0.0',
    category='browser',
    tags=['browser', 'interaction', 'click'],
    label='Click Element',
    label_key='modules.browser.click.label',
    description='Click an element on the page',
    description_key='modules.browser.click.description',
    icon='MousePointerClick',
    color='#F0AD4E',
    params_schema={
        'selector': {
            'type': 'string',
            'label': 'CSS Selector',
            'label_key': 'modules.browser.click.params.selector.label',
            'placeholder': '#button-id or .button-class',
            'description': 'CSS selector of the element to click',
            'description_key': 'modules.browser.click.params.selector.description',
            'required': True
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'selector': {'type': 'string'}
    },
    examples=[
        {
            'name': 'Click submit button',
            'params': {'selector': '#submit-button'}
        },
        {
            'name': 'Click first link',
            'params': {'selector': 'a.link-class'}
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class BrowserClickModule(BaseModule):
    """Click Element Module"""

    module_name = "Click Element"
    module_description = "Click an element on the page"
    required_permission = "browser.interact"

    def validate_params(self):
        if 'selector' not in self.params:
            raise ValueError("Missing required parameter: selector")
        self.selector = self.params['selector']

    async def execute(self) -> Any:
        browser = self.context.get('browser')
        if not browser:
            raise RuntimeError("Browser not launched. Please run browser.launch first")

        await browser.click(self.selector)
        return {"status": "success", "selector": self.selector}


@register_module(
    module_id='core.browser.type',
    version='1.0.0',
    category='browser',
    tags=['browser', 'interaction', 'input', 'keyboard'],
    label='Type Text',
    label_key='modules.browser.type.label',
    description='Type text into an input field',
    description_key='modules.browser.type.description',
    icon='Keyboard',
    color='#5BC0DE',
    params_schema={
        'selector': {
            'type': 'string',
            'label': 'CSS Selector',
            'label_key': 'modules.browser.type.params.selector.label',
            'placeholder': 'input[name="email"]',
            'description': 'CSS selector of the input field',
            'description_key': 'modules.browser.type.params.selector.description',
            'required': True
        },
        'text': {
            'type': 'string',
            'label': 'Text Content',
            'label_key': 'modules.browser.type.params.text.label',
            'placeholder': 'Text to type',
            'description': 'The text to type into the field',
            'description_key': 'modules.browser.type.params.text.description',
            'required': True
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'selector': {'type': 'string'}
    },
    examples=[
        {
            'name': 'Type email address',
            'params': {
                'selector': 'input[type="email"]',
                'text': 'user@example.com'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class BrowserTypeModule(BaseModule):
    """Type Text Module"""

    module_name = "Type Text"
    module_description = "Type text into an input field"
    required_permission = "browser.interact"

    def validate_params(self):
        if 'selector' not in self.params:
            raise ValueError("Missing required parameter: selector")
        if 'text' not in self.params:
            raise ValueError("Missing required parameter: text")

        self.selector = self.params['selector']
        self.text = self.params['text']

    async def execute(self) -> Any:
        browser = self.context.get('browser')
        if not browser:
            raise RuntimeError("Browser not launched. Please run browser.launch first")

        await browser.type_text(self.selector, self.text)
        return {"status": "success", "selector": self.selector}


@register_module(
    module_id='core.browser.screenshot',
    version='1.0.0',
    category='browser',
    tags=['browser', 'screenshot', 'capture', 'image'],
    label='Take Screenshot',
    label_key='modules.browser.screenshot.label',
    description='Take a screenshot of the current page',
    description_key='modules.browser.screenshot.description',
    icon='Camera',
    color='#9B59B6',
    params_schema={
        'path': {
            'type': 'string',
            'label': 'File Path',
            'label_key': 'modules.browser.screenshot.params.path.label',
            'placeholder': 'screenshot.png',
            'description': 'Path to save the screenshot',
            'description_key': 'modules.browser.screenshot.params.path.description',
            'default': 'screenshot.png',
            'required': False
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'filepath': {'type': 'string'}
    },
    examples=[
        {
            'name': 'Take screenshot',
            'params': {'path': 'output/page.png'}
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class BrowserScreenshotModule(BaseModule):
    """Screenshot Module"""

    module_name = "Take Screenshot"
    module_description = "Take a screenshot of the current page"
    required_permission = "browser.screenshot"

    def validate_params(self):
        self.path = self.params.get('path', 'screenshot.png')

    async def execute(self) -> Any:
        browser = self.context.get('browser')
        if not browser:
            raise RuntimeError("Browser not launched. Please run browser.launch first")

        filepath = await browser.screenshot(self.path)
        return {"status": "success", "filepath": filepath}


@register_module(
    module_id='core.browser.wait',
    version='1.0.0',
    category='browser',
    tags=['browser', 'wait', 'delay', 'selector'],
    label='Wait',
    label_key='modules.browser.wait.label',
    description='Wait for a duration or until an element appears',
    description_key='modules.browser.wait.description',
    icon='Clock',
    color='#95A5A6',
    params_schema={
        'duration': {
            'type': 'number',
            'label': 'Duration (seconds)',
            'label_key': 'modules.browser.wait.params.duration.label',
            'placeholder': '1',
            'description': 'Time to wait in seconds',
            'description_key': 'modules.browser.wait.params.duration.description',
            'default': 1,
            'required': False
        },
        'selector': {
            'type': 'string',
            'label': 'CSS Selector',
            'label_key': 'modules.browser.wait.params.selector.label',
            'placeholder': '.element-to-wait-for',
            'description': 'Wait for this element to appear (overrides duration)',
            'description_key': 'modules.browser.wait.params.selector.description',
            'required': False
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'selector': {'type': 'string', 'optional': True},
        'duration': {'type': 'number', 'optional': True}
    },
    examples=[
        {
            'name': 'Wait 2 seconds',
            'params': {'duration': 2}
        },
        {
            'name': 'Wait for element',
            'params': {'selector': '#loading-complete'}
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class BrowserWaitModule(BaseModule):
    """Wait Module"""

    module_name = "Wait"
    module_description = "Wait for a duration or element to appear"
    required_permission = "browser.interact"

    def validate_params(self):
        self.duration = self.params.get('duration', 1)
        self.selector = self.params.get('selector')

    async def execute(self) -> Any:
        import asyncio

        browser = self.context.get('browser')
        if not browser:
            raise RuntimeError("Browser not launched. Please run browser.launch first")

        if self.selector:
            # Wait for element to appear
            await browser.wait_for_selector(self.selector)
            return {"status": "success", "selector": self.selector}
        else:
            # Wait for specified duration
            await asyncio.sleep(self.duration)
            return {"status": "success", "duration": self.duration}


@register_module(
    module_id='core.browser.extract',
    version='1.0.0',
    category='browser',
    tags=['browser', 'scraping', 'data', 'extract'],
    label='Extract Data',
    label_key='modules.browser.extract.label',
    description='Extract structured data from the page',
    description_key='modules.browser.extract.description',
    icon='Database',
    color='#E74C3C',
    params_schema={
        'selector': {
            'type': 'string',
            'label': 'Container Selector',
            'label_key': 'modules.browser.extract.params.selector.label',
            'placeholder': '.result-item',
            'description': 'CSS selector for container elements',
            'description_key': 'modules.browser.extract.params.selector.description',
            'required': True
        },
        'limit': {
            'type': 'number',
            'label': 'Limit',
            'label_key': 'modules.browser.extract.params.limit.label',
            'placeholder': '10',
            'description': 'Maximum number of items to extract',
            'description_key': 'modules.browser.extract.params.limit.description',
            'required': False
        },
        'fields': {
            'type': 'object',
            'label': 'Fields to Extract',
            'label_key': 'modules.browser.extract.params.fields.label',
            'description': 'Define fields to extract from each item',
            'description_key': 'modules.browser.extract.params.fields.description',
            'required': False
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'data': {'type': 'array'},
        'count': {'type': 'number'}
    },
    examples=[
        {
            'name': 'Extract Google search results',
            'params': {
                'selector': '.g',
                'limit': 10,
                'fields': {
                    'title': {'selector': 'h3', 'type': 'text'},
                    'url': {'selector': 'a', 'type': 'attribute', 'attribute': 'href'}
                }
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class BrowserExtractModule(BaseModule):
    """Extract Data Module"""

    module_name = "Extract Data"
    module_description = "Extract structured data from the page"
    required_permission = "browser.interact"

    def validate_params(self):
        if 'selector' not in self.params:
            raise ValueError("Missing required parameter: selector")

        self.selector = self.params['selector']

        # Handle limit parameter - convert string to integer
        limit_param = self.params.get('limit', None)
        if limit_param is not None:
            self.limit = int(limit_param) if isinstance(limit_param, str) else limit_param
        else:
            self.limit = None

        self.fields = self.params.get('fields', {})

    async def execute(self) -> Any:
        browser = self.context.get('browser')
        if not browser:
            raise RuntimeError("Browser not launched. Please run browser.launch first")

        # Use playwright to extract data
        elements = await browser.page.query_selector_all(self.selector)

        if self.limit:
            elements = elements[:self.limit]

        results = []
        for element in elements:
            item = {}
            for field_name, field_config in self.fields.items():
                try:
                    # Support new format: {'selector': 'h3', 'type': 'text', 'attribute': 'href'}
                    # Or old format: 'h3'
                    if isinstance(field_config, dict):
                        field_selector = field_config.get('selector', '')
                        field_type = field_config.get('type', 'text')
                        attribute_name = field_config.get('attribute', 'href')
                    else:
                        field_selector = field_config
                        field_type = 'text'
                        attribute_name = 'href'

                    # Support comma-separated multiple selectors (fallback mechanism)
                    selectors = [s.strip() for s in field_selector.split(',')]
                    field_value = None

                    for selector in selectors:
                        field_element = await element.query_selector(selector)
                        if field_element:
                            if field_type == 'attribute':
                                field_value = await field_element.get_attribute(attribute_name)
                            else:  # type == 'text'
                                field_value = await field_element.inner_text()
                            break  # Stop when found

                    item[field_name] = field_value
                except Exception:
                    item[field_name] = None
            results.append(item)

        return {"status": "success", "data": results, "count": len(results)}


@register_module(
    module_id='core.browser.press',
    version='1.0.0',
    category='browser',
    tags=['browser', 'keyboard', 'interaction', 'key'],
    label='Press Key',
    label_key='modules.browser.press.label',
    description='Press a keyboard key',
    description_key='modules.browser.press.description',
    icon='Command',
    color='#34495E',
    params_schema={
        'key': {
            'type': 'string',
            'label': 'Key',
            'label_key': 'modules.browser.press.params.key.label',
            'placeholder': 'Enter',
            'description': 'The key to press (e.g., Enter, Escape, Tab)',
            'description_key': 'modules.browser.press.params.key.description',
            'required': True
        }
    },
    output_schema={
        'status': {'type': 'string'},
        'key': {'type': 'string'}
    },
    examples=[
        {
            'name': 'Press Enter key',
            'params': {'key': 'Enter'}
        },
        {
            'name': 'Press Escape key',
            'params': {'key': 'Escape'}
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
class BrowserPressModule(BaseModule):
    """Press Key Module"""

    module_name = "Press Key"
    module_description = "Press a keyboard key"
    required_permission = "browser.interact"

    def validate_params(self):
        if 'key' not in self.params:
            raise ValueError("Missing required parameter: key")
        self.key = self.params['key']

    async def execute(self) -> Any:
        browser = self.context.get('browser')
        if not browser:
            raise RuntimeError("Browser not launched. Please run browser.launch first")

        await browser.page.keyboard.press(self.key)
        return {"status": "success", "key": self.key}
