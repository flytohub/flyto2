"""
String Operation Modules
String processing and manipulation
"""

from typing import Any, Dict
from ...base import BaseModule
from ...registry import register_module
import re


@register_module(
    module_id='string.split',
    version='1.0.0',
    category='atomic',
    subcategory='string',
    tags=['string', 'text', 'split', 'atomic'],
    label='Split String',
    label_key='modules.string.split.label',
    description='Split a string into array by delimiter',
    description_key='modules.string.split.description',
    icon='Split',
    color='#8B5CF6',
    params_schema={
        'text': {
            'type': 'string',
            'label': 'Text',
            'label_key': 'modules.string.split.params.text.label',
            'description': 'Text to split',
            'description_key': 'modules.string.split.params.text.description',
            'required': True,
            'multiline': True
        },
        'delimiter': {
            'type': 'string',
            'label': 'Delimiter',
            'label_key': 'modules.string.split.params.delimiter.label',
            'description': 'Delimiter to split by',
            'description_key': 'modules.string.split.params.delimiter.description',
            'default': ',',
            'required': False
        },
        'trim': {
            'type': 'boolean',
            'label': 'Trim Whitespace',
            'label_key': 'modules.string.split.params.trim.label',
            'description': 'Trim whitespace from each part',
            'description_key': 'modules.string.split.params.trim.description',
            'default': True,
            'required': False
        }
    },
    output_schema={
        'parts': {
            'type': 'array',
            'description': 'Array of split parts'
        },
        'count': {
            'type': 'number',
            'description': 'Number of parts'
        }
    },
    examples=[
        {
            'title': 'Split CSV',
            'title_key': 'modules.string.split.examples.csv.title',
            'params': {
                'text': 'apple,banana,orange',
                'delimiter': ',',
                'trim': True
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
async def string_split(context):
    """Split string by delimiter"""
    params = context['params']
    text = params['text']
    delimiter = params.get('delimiter', ',')
    trim = params.get('trim', True)

    parts = text.split(delimiter)

    if trim:
        parts = [part.strip() for part in parts]

    return {
        'parts': parts,
        'count': len(parts)
    }


@register_module(
    module_id='string.replace',
    version='1.0.0',
    category='atomic',
    subcategory='string',
    tags=['string', 'text', 'replace', 'atomic'],
    label='Replace String',
    label_key='modules.string.replace.label',
    description='Replace text in a string',
    description_key='modules.string.replace.description',
    icon='Replace',
    color='#8B5CF6',
    params_schema={
        'text': {
            'type': 'string',
            'label': 'Text',
            'label_key': 'modules.string.replace.params.text.label',
            'description': 'Original text',
            'description_key': 'modules.string.replace.params.text.description',
            'required': True,
            'multiline': True
        },
        'search': {
            'type': 'string',
            'label': 'Search',
            'label_key': 'modules.string.replace.params.search.label',
            'description': 'Text to search for',
            'description_key': 'modules.string.replace.params.search.description',
            'required': True
        },
        'replace': {
            'type': 'string',
            'label': 'Replace With',
            'label_key': 'modules.string.replace.params.replace.label',
            'description': 'Text to replace with',
            'description_key': 'modules.string.replace.params.replace.description',
            'required': True
        },
        'case_sensitive': {
            'type': 'boolean',
            'label': 'Case Sensitive',
            'label_key': 'modules.string.replace.params.case_sensitive.label',
            'description': 'Case sensitive search',
            'description_key': 'modules.string.replace.params.case_sensitive.description',
            'default': True,
            'required': False
        }
    },
    output_schema={
        'result': {
            'type': 'string',
            'description': 'Text after replacement'
        },
        'count': {
            'type': 'number',
            'description': 'Number of replacements'
        }
    },
    examples=[
        {
            'title': 'Replace text',
            'title_key': 'modules.string.replace.examples.simple.title',
            'params': {
                'text': 'Hello World',
                'search': 'World',
                'replace': 'Flyto2'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
async def string_replace(context):
    """Replace text in string"""
    params = context['params']
    text = params['text']
    search = params['search']
    replace_with = params['replace']
    case_sensitive = params.get('case_sensitive', True)

    if case_sensitive:
        result = text.replace(search, replace_with)
        count = text.count(search)
    else:
        import re
        pattern = re.compile(re.escape(search), re.IGNORECASE)
        result = pattern.sub(replace_with, text)
        count = len(pattern.findall(text))

    return {
        'result': result,
        'count': count
    }


@register_module(
    module_id='string.regex_match',
    version='1.0.0',
    category='atomic',
    subcategory='string',
    tags=['string', 'regex', 'pattern', 'atomic'],
    label='Regex Match',
    label_key='modules.string.regex_match.label',
    description='Match text using regular expression',
    description_key='modules.string.regex_match.description',
    icon='Search',
    color='#8B5CF6',
    params_schema={
        'text': {
            'type': 'string',
            'label': 'Text',
            'label_key': 'modules.string.regex_match.params.text.label',
            'description': 'Text to search',
            'description_key': 'modules.string.regex_match.params.text.description',
            'required': True,
            'multiline': True
        },
        'pattern': {
            'type': 'string',
            'label': 'Pattern',
            'label_key': 'modules.string.regex_match.params.pattern.label',
            'description': 'Regular expression pattern',
            'description_key': 'modules.string.regex_match.params.pattern.description',
            'required': True,
            'placeholder': r'\d+'
        },
        'flags': {
            'type': 'array',
            'label': 'Flags',
            'label_key': 'modules.string.regex_match.params.flags.label',
            'description': 'Regex flags',
            'description_key': 'modules.string.regex_match.params.flags.description',
            'required': False,
            'items': {
                'type': 'string',
                'enum': ['IGNORECASE', 'MULTILINE', 'DOTALL']
            }
        }
    },
    output_schema={
        'matches': {
            'type': 'array',
            'description': 'Array of matches'
        },
        'count': {
            'type': 'number',
            'description': 'Number of matches'
        },
        'matched': {
            'type': 'boolean',
            'description': 'Whether any match was found'
        }
    },
    examples=[
        {
            'title': 'Extract numbers',
            'title_key': 'modules.string.regex_match.examples.numbers.title',
            'params': {
                'text': 'Price is 100 dollars and 50 cents',
                'pattern': r'\d+'
            }
        },
        {
            'title': 'Extract emails',
            'title_key': 'modules.string.regex_match.examples.emails.title',
            'params': {
                'text': 'Contact: john@example.com or jane@test.com',
                'pattern': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            }
        }
    ],
    author='Flyto2 Team',
    license='MIT'
)
async def string_regex_match(context):
    """Match text using regex"""
    params = context['params']
    text = params['text']
    pattern = params['pattern']
    flags = params.get('flags', [])

    # Build regex flags
    regex_flags = 0
    if 'IGNORECASE' in flags:
        regex_flags |= re.IGNORECASE
    if 'MULTILINE' in flags:
        regex_flags |= re.MULTILINE
    if 'DOTALL' in flags:
        regex_flags |= re.DOTALL

    # Find all matches
    compiled_pattern = re.compile(pattern, regex_flags)
    matches = compiled_pattern.findall(text)

    return {
        'matches': matches,
        'count': len(matches),
        'matched': len(matches) > 0
    }
