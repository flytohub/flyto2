"""
OpenAI Integration - Third-party integration for OpenAI services

This is an optional integration. Install with:
    pip install openai

Then import this module to register OpenAI modules.
"""
import logging
import os
from typing import Any, Dict, List, Optional
from src.core.modules.base import BaseModule
from src.core.modules.registry import register_module


# Check if OpenAI is available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not installed. Install with: pip install openai")


logger = logging.getLogger(__name__)


@register_module(
    module_id='core.ai.openai.chat',
    version='1.0.0',
    category='ai',
    tags=['ai', 'openai', 'chat', 'llm'],
    label='OpenAI Chat',
    label_key='modules.ai.openai_chat.label',
    description='Send messages to OpenAI chat models (GPT-4, GPT-3.5, etc.)',
    description_key='modules.ai.openai_chat.description',
    author='Flyto2 Team',
    license='MIT'
)
class OpenAIChatModule(BaseModule):
    """
    Send chat messages to OpenAI models

    Params:
        model: Model name (e.g., 'gpt-4', 'gpt-3.5-turbo')
        messages: List of message objects with 'role' and 'content'
                 Example: [{'role': 'user', 'content': 'Hello'}]
        system_prompt: Optional system prompt
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate
        api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)

    Output:
        {
            'content': str,           # Response content
            'model': str,             # Model used
            'usage': {                # Token usage
                'prompt_tokens': int,
                'completion_tokens': int,
                'total_tokens': int
            }
        }
    """

    module_name = "OpenAI Chat"
    module_description = "Send messages to OpenAI chat models"

    def validate_params(self):
        if 'messages' not in self.params or not self.params['messages']:
            raise ValueError("Missing required parameter: messages")

    async def execute(self) -> Any:
        try:
            import openai
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )

        # Get parameters
        model = self.params.get('model', 'gpt-4')
        messages = self.params.get('messages', [])
        system_prompt = self.params.get('system_prompt')
        temperature = self.params.get('temperature', 0.7)
        max_tokens = self.params.get('max_tokens')
        api_key = self.params.get('api_key') or os.getenv('OPENAI_API_KEY')

        if not api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY env var or pass api_key param.")

        if not messages:
            raise ValueError("No messages provided")

        # Build message list
        message_list = []

        # Add system prompt if provided
        if system_prompt:
            message_list.append({
                'role': 'system',
                'content': system_prompt
            })

        # Add user messages
        message_list.extend(messages)

        logger.info(f"Calling OpenAI {model} with {len(message_list)} messages")

        # Create client
        client = openai.AsyncOpenAI(api_key=api_key)

        # Make API call
        kwargs = {
            'model': model,
            'messages': message_list,
            'temperature': temperature
        }

        if max_tokens:
            kwargs['max_tokens'] = max_tokens

        response = await client.chat.completions.create(**kwargs)

        # Extract response
        content = response.choices[0].message.content
        usage = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }

        logger.info(f"OpenAI response received (tokens: {usage['total_tokens']})")

        return {
            'content': content,
            'model': model,
            'usage': usage
        }


@register_module(
    module_id='core.ai.analyze_text',
    version='1.0.0',
    category='ai',
    tags=['ai', 'analysis', 'text'],
    label='Analyze Text',
    label_key='modules.ai.analyze_text.label',
    description='Analyze text with AI and extract structured information',
    description_key='modules.ai.analyze_text.description',
    author='Flyto2 Team',
    license='MIT'
)
class AnalyzeTextModule(BaseModule):
    """
    Analyze text content using AI

    Params:
        text: Text to analyze
        prompt: Analysis instructions
        model: AI model to use
        output_format: Expected output format ('json', 'text')

    Output:
        Analyzed content based on prompt
    """

    module_name = "Analyze Text"
    module_description = "Analyze text with AI and extract structured information"

    def validate_params(self):
        if 'text' not in self.params:
            raise ValueError("Missing required parameter: text")
        if 'prompt' not in self.params:
            raise ValueError("Missing required parameter: prompt")

    async def execute(self) -> Any:
        text = self.params.get('text', '')
        prompt = self.params.get('prompt', '')
        model = self.params.get('model', 'gpt-4')
        output_format = self.params.get('output_format', 'text')

        if not text:
            raise ValueError("No text provided for analysis")

        if not prompt:
            raise ValueError("No analysis prompt provided")

        # Build analysis message
        analysis_prompt = f"{prompt}\n\nText to analyze:\n{text}"

        if output_format == 'json':
            analysis_prompt += "\n\nProvide output as valid JSON only."

        # Use OpenAI chat module
        from src.core.modules.registry import ModuleRegistry

        chat_module_class = ModuleRegistry.get('core.ai.openai.chat')
        chat_module = chat_module_class(
            {
                'model': model,
                'messages': [
                    {'role': 'user', 'content': analysis_prompt}
                ]
            },
            self.context
        )

        result = await chat_module.run()

        # Parse JSON if requested
        if output_format == 'json':
            import json
            try:
                content = result['content']
                # Try to extract JSON from markdown code blocks
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()

                parsed = json.loads(content)
                return {
                    'analysis': parsed,
                    'format': 'json',
                    'model': model
                }
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON: {str(e)}")
                return {
                    'analysis': result['content'],
                    'format': 'text',
                    'model': model,
                    'parse_error': str(e)
                }
        else:
            return {
                'analysis': result['content'],
                'format': 'text',
                'model': model
            }


@register_module(
    module_id='core.ai.summarize',
    version='1.0.0',
    category='ai',
    tags=['ai', 'summarization', 'text'],
    label='Summarize Text',
    label_key='modules.ai.summarize.label',
    description='Summarize long text into concise summary',
    description_key='modules.ai.summarize.description',
    author='Flyto2 Team',
    license='MIT'
)
class SummarizeTextModule(BaseModule):
    """
    Summarize text content

    Params:
        text: Text to summarize
        max_length: Maximum summary length in words
        model: AI model to use

    Output:
        {
            'summary': str,
            'original_length': int,
            'summary_length': int
        }
    """

    module_name = "Summarize Text"
    module_description = "Summarize long text into concise summary"

    def validate_params(self):
        if 'text' not in self.params:
            raise ValueError("Missing required parameter: text")

    async def execute(self) -> Any:
        text = self.params.get('text', '')
        max_length = self.params.get('max_length', 100)
        model = self.params.get('model', 'gpt-3.5-turbo')

        if not text:
            raise ValueError("No text provided for summarization")

        # Build summarization prompt
        summary_prompt = f"Summarize the following text in no more than {max_length} words. Be concise and capture the key points.\n\nText:\n{text}"

        # Use OpenAI chat module
        from src.core.modules.registry import ModuleRegistry

        chat_module_class = ModuleRegistry.get('core.ai.openai.chat')
        chat_module = chat_module_class(
            {
                'model': model,
                'messages': [
                    {'role': 'user', 'content': summary_prompt}
                ],
                'temperature': 0.3
            },
            self.context
        )

        result = await chat_module.run()

        summary = result['content']

        return {
            'summary': summary,
            'original_length': len(text.split()),
            'summary_length': len(summary.split()),
            'model': model
        }
