"""
Prompt Loader - Atomic module for loading prompts from markdown files
Zero coupling, single responsibility: Load and format prompts
"""
from pathlib import Path
from typing import Dict, Optional


class PromptLoader:
    """
    Atomic prompt loader with zero external dependencies.

    Loads prompts from markdown files and provides simple formatting.
    """

    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialize prompt loader.

        Args:
            prompts_dir: Path to prompts directory. Defaults to src/core/meta/prompts/
        """
        if prompts_dir is None:
            self.prompts_dir = Path(__file__).parent / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)

    def load_prompt(self, prompt_name: str) -> str:
        """
        Load a prompt file by name.

        Args:
            prompt_name: Name of the prompt file (without .md extension)

        Returns:
            Content of the prompt file

        Raises:
            FileNotFoundError: If prompt file does not exist
        """
        prompt_path = self.prompts_dir / f"{prompt_name}.md"

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        return prompt_path.read_text(encoding="utf-8")

    def format_prompt(self, prompt_template: str, **kwargs) -> str:
        """
        Format a prompt template with provided variables.

        Args:
            prompt_template: Prompt string with {variable} placeholders
            **kwargs: Variables to replace in template

        Returns:
            Formatted prompt string
        """
        return prompt_template.format(**kwargs)

    def load_and_format(self, prompt_name: str, **kwargs) -> str:
        """
        Load and format a prompt in one step.

        Args:
            prompt_name: Name of the prompt file (without .md extension)
            **kwargs: Variables to replace in template

        Returns:
            Loaded and formatted prompt string
        """
        template = self.load_prompt(prompt_name)
        return self.format_prompt(template, **kwargs)

    def extract_section(self, content: str, section_title: str) -> Optional[str]:
        """
        Extract a specific section from markdown content.

        Args:
            content: Full markdown content
            section_title: Title of section to extract (e.g., "## MISSION")

        Returns:
            Section content or None if not found
        """
        lines = content.split("\n")
        section_lines = []
        in_section = False

        for line in lines:
            if line.strip().startswith("#") and section_title in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith("#"):
                # Hit next section, stop
                break
            elif in_section:
                section_lines.append(line)

        if section_lines:
            return "\n".join(section_lines).strip()
        return None
