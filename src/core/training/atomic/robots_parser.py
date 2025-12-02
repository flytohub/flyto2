"""
Robots Parser Module - Parse and analyze robots.txt files

Atomic responsibility: Parse robots.txt into structured rules
Extracted from: daily_practice.py lines 119-156
"""

from typing import Any, Dict


class RobotsParserModule:
    """
    Parse and analyze robots.txt files

    Single responsibility: Extract robots.txt rules into structured format
    """

    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """
        Parse robots.txt content

        Args:
            content: Raw robots.txt content

        Returns:
            {
                "user_agents": {
                    "agent_name": {
                        "allow": [paths...],
                        "disallow": [paths...]
                    }
                },
                "sitemaps": [urls...],
                "crawl_delay": float or None
            }
        """
        rules = {
            "user_agents": {},
            "sitemaps": [],
            "crawl_delay": None
        }

        current_agent = None
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.lower().startswith('user-agent:'):
                current_agent = line.split(':', 1)[1].strip()
                if current_agent not in rules["user_agents"]:
                    rules["user_agents"][current_agent] = {"allow": [], "disallow": []}

            elif line.lower().startswith('disallow:') and current_agent:
                path = line.split(':', 1)[1].strip()
                if path:
                    rules["user_agents"][current_agent]["disallow"].append(path)

            elif line.lower().startswith('allow:') and current_agent:
                path = line.split(':', 1)[1].strip()
                if path:
                    rules["user_agents"][current_agent]["allow"].append(path)

            elif line.lower().startswith('crawl-delay:'):
                delay = line.split(':', 1)[1].strip()
                try:
                    rules["crawl_delay"] = float(delay)
                except ValueError:
                    pass

            elif line.lower().startswith('sitemap:'):
                sitemap = line.split(':', 1)[1].strip()
                rules["sitemaps"].append(sitemap)

        return rules

    @staticmethod
    def get_agent_rules(parsed_rules: Dict[str, Any], user_agent: str = "*") -> Dict[str, Any]:
        """
        Get rules for specific user agent

        Args:
            parsed_rules: Parsed robots.txt rules
            user_agent: User agent to check (default: "*")

        Returns:
            Agent-specific rules
        """
        user_agents = parsed_rules.get("user_agents", {})

        # Try exact match first
        if user_agent in user_agents:
            return user_agents[user_agent]

        # Fallback to wildcard
        if "*" in user_agents:
            return user_agents["*"]

        return {"allow": [], "disallow": []}

    @staticmethod
    def is_path_allowed(parsed_rules: Dict[str, Any], path: str, user_agent: str = "*") -> bool:
        """
        Check if path is allowed for user agent

        Args:
            parsed_rules: Parsed robots.txt rules
            path: URL path to check
            user_agent: User agent (default: "*")

        Returns:
            True if allowed, False otherwise
        """
        agent_rules = RobotsParserModule.get_agent_rules(parsed_rules, user_agent)

        # Check disallow rules first (more restrictive)
        for disallow_path in agent_rules.get("disallow", []):
            if path.startswith(disallow_path):
                # Check if explicitly allowed
                for allow_path in agent_rules.get("allow", []):
                    if path.startswith(allow_path):
                        return True
                return False

        return True
