"""
JobMemory - Short-term Task Memory System
Manages task conversations stored in cloud databases (PostgreSQL/MySQL)
"""
import os
import yaml
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Job status enumeration with 9 states for comprehensive lifecycle"""
    QUEUED = "queued"                      # Job created, waiting to start
    PLANNING = "planning"                   # Generating execution plan
    EXECUTING = "executing"                 # Executing workflow steps
    PAUSED = "paused"                       # Paused by user or system
    WAITING_USER_INPUT = "waiting_user_input"  # Waiting for user response
    COMPLETED = "completed"                 # Successfully completed
    FAILED = "failed"                       # Failed with error
    CANCELLED = "cancelled"                 # Cancelled by user
    TIMEOUT = "timeout"                     # Timed out

    # Backwards compatibility aliases
    PENDING = "queued"
    IN_PROGRESS = "executing"


class JobEventType(Enum):
    """Job event type enumeration for audit trail"""
    # Lifecycle events
    JOB_CREATED = "job_created"
    JOB_STATUS_CHANGED = "job_status_changed"

    # Planning events
    PLAN_STARTED = "plan_started"
    PLAN_GENERATED = "plan_generated"
    PLAN_FAILED = "plan_failed"

    # Execution events
    STEP_STARTED = "step_started"
    STEP_SUCCEEDED = "step_succeeded"
    STEP_FAILED = "step_failed"

    # Module evolution events
    MODULE_SUGGESTED = "module_suggested"
    MODULE_SPEC_GENERATED = "module_spec_generated"
    MODULE_CODE_GENERATED = "module_code_generated"
    MODULE_APPROVED = "module_approved"
    MODULE_REJECTED = "module_rejected"

    # LLM events
    LLM_CALL_STARTED = "llm_call_started"
    LLM_CALL_COMPLETED = "llm_call_completed"
    LLM_CALL_FAILED = "llm_call_failed"

    # User interaction events
    WAITING_USER_INPUT = "waiting_user_input"
    USER_INPUT_RECEIVED = "user_input_received"

    # Security events
    SECURITY_VIOLATION = "security_violation"
    PERMISSION_CHECK = "permission_check"


class LanguageDetector:
    """
    Language detector using character-based heuristics
    Detects language from text for multilingual support
    """

    # Unicode ranges for different scripts
    CJK_RANGES = [
        (0x4E00, 0x9FFF),    # CJK Unified Ideographs
        (0x3400, 0x4DBF),    # CJK Extension A
        (0x20000, 0x2A6DF),  # CJK Extension B
        (0x3040, 0x309F),    # Hiragana
        (0x30A0, 0x30FF),    # Katakana
    ]

    LATIN_RANGE = (0x0000, 0x024F)

    def detect(self, text: str) -> tuple:
        """
        Detect language from text using character heuristics

        Args:
            text: Input text

        Returns:
            (language_code, confidence)
            language_code: 'zh', 'ja', 'en', 'unknown'
            confidence: 0.0 to 1.0
        """
        if not text or not text.strip():
            return ("unknown", 0.0)

        # Count character types
        total_chars = len(text)
        cjk_count = sum(1 for c in text if self._is_cjk(c))
        latin_count = sum(1 for c in text if self._is_latin(c))

        cjk_ratio = cjk_count / total_chars if total_chars > 0 else 0
        latin_ratio = latin_count / total_chars if total_chars > 0 else 0

        # Decision rules
        if cjk_ratio > 0.3:
            # High CJK presence
            if self._has_hiragana(text) or self._has_katakana(text):
                return ("ja", min(0.9, cjk_ratio))
            else:
                # Assume Chinese if CJK but no Japanese kana
                return ("zh", min(0.9, cjk_ratio))

        elif latin_ratio > 0.7:
            # Mostly Latin characters
            return ("en", min(0.9, latin_ratio))

        elif cjk_ratio > 0.1 and latin_ratio > 0.3:
            # Mixed content - default to English
            return ("en", 0.6)

        else:
            # Unclear
            return ("unknown", 0.3)

    def _is_cjk(self, char: str) -> bool:
        """Check if character is CJK"""
        code = ord(char)
        return any(start <= code <= end for start, end in self.CJK_RANGES)

    def _is_latin(self, char: str) -> bool:
        """Check if character is Latin"""
        code = ord(char)
        start, end = self.LATIN_RANGE
        return start <= code <= end

    def _has_hiragana(self, text: str) -> bool:
        """Check if text contains Hiragana"""
        return any(0x3040 <= ord(c) <= 0x309F for c in text)

    def _has_katakana(self, text: str) -> bool:
        """Check if text contains Katakana"""
        return any(0x30A0 <= ord(c) <= 0x30FF for c in text)


class Translator:
    """
    Bidirectional translator between user language and English
    Translates user input to English for internal processing (RAG, Planning, Execution)
    Translates English responses back to user's language
    """

    def __init__(self, ollama_endpoint: str = "http://localhost:11434"):
        """
        Initialize translator

        Args:
            ollama_endpoint: Ollama API endpoint URL
        """
        self.ollama_endpoint = ollama_endpoint
        self.translation_model = "qwen2.5:7b"  # Fast model for translation
        self.logger = logging.getLogger(__name__)

    def to_english(self, text: str, source_language: str) -> str:
        """
        Translate user input to English for internal processing

        Args:
            text: Original text in user's language
            source_language: Detected language code ('zh', 'ja', 'en', etc.)

        Returns:
            English translation (or original if already English/unknown)
        """
        if source_language == "en":
            return text  # Already English, no translation needed

        if source_language == "unknown":
            # Cannot translate unknown language, return as-is
            self.logger.warning(f"Cannot translate unknown language: {text[:50]}...")
            return text

        prompt = self._build_to_english_prompt(text, source_language)

        try:
            translation = self._call_llm(prompt)
            self.logger.debug(f"Translated to EN: {text[:50]}... -> {translation[:50]}...")
            return translation
        except Exception as e:
            self.logger.error(f"Translation to English failed: {e}")
            return text  # Fallback to original text

    def from_english(self, text: str, target_language: str) -> str:
        """
        Translate English response back to user's language

        Args:
            text: English text from system
            target_language: Target language code ('zh', 'ja', etc.)

        Returns:
            Translated text (or original if target is English/unknown)
        """
        if target_language == "en":
            return text  # Already English, no translation needed

        if target_language == "unknown":
            return text  # Cannot translate to unknown language

        prompt = self._build_from_english_prompt(text, target_language)

        try:
            translation = self._call_llm(prompt)
            self.logger.debug(f"Translated from EN: {text[:50]}... -> {translation[:50]}...")
            return translation
        except Exception as e:
            self.logger.error(f"Translation from English failed: {e}")
            return text  # Fallback to English

    def _build_to_english_prompt(self, text: str, source_language: str) -> str:
        """
        Build prompt for translating TO English

        Args:
            text: Text to translate
            source_language: Source language code

        Returns:
            Prompt string for LLM
        """
        lang_names = {"zh": "Chinese", "ja": "Japanese", "ko": "Korean"}
        lang_name = lang_names.get(source_language, source_language)

        return f"""Translate the following {lang_name} text to natural English.
Only output the English translation, no explanations or notes.

{lang_name} text:
{text}

English translation:"""

    def _build_from_english_prompt(self, text: str, target_language: str) -> str:
        """
        Build prompt for translating FROM English

        Args:
            text: English text to translate
            target_language: Target language code

        Returns:
            Prompt string for LLM
        """
        lang_names = {"zh": "Chinese", "ja": "Japanese", "ko": "Korean"}
        lang_name = lang_names.get(target_language, target_language)

        return f"""Translate the following English text to natural {lang_name}.
Only output the {lang_name} translation, no explanations or notes.

English text:
{text}

{lang_name} translation:"""

    def _call_llm(self, prompt: str) -> str:
        """
        Call Ollama LLM for translation

        Args:
            prompt: Translation prompt

        Returns:
            Translated text

        Raises:
            Exception: If API call fails
        """
        import requests

        response = requests.post(
            f"{self.ollama_endpoint}/api/generate",
            json={
                "model": self.translation_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Low temperature for consistent translation
                    "num_predict": 512
                }
            },
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code}")

        result = response.json()
        translation = result.get('response', '').strip()

        return translation


# ============================================================
# Phase 3.1: Capability Inspector (Security-First Approach)
# ============================================================


class CapabilityType(Enum):
    """Types of system capabilities"""
    BROWSER = "browser"              # Playwright browser automation
    API_KEY = "api_key"              # Third-party API access
    FILE_SYSTEM = "file_system"      # Local file operations
    DATABASE = "database"            # Database connections
    NETWORK = "network"              # HTTP requests
    SYSTEM_COMMAND = "system_command" # Shell command execution


@dataclass
class Capability:
    """
    Capability definition
    Represents what the system can or cannot do
    """
    name: str                        # e.g., "openai_api", "browser_chrome"
    type: CapabilityType
    available: bool                  # Is it configured?
    reason: Optional[str] = None     # Why unavailable
    metadata: Optional[Dict] = None  # Additional info


@dataclass
class SecurityPolicy:
    """
    Security policy for a job
    Defines what actions are allowed for a specific job
    """
    allowed_domains: List[str] = field(default_factory=list)  # ["google.com", "*.github.com"]
    allowed_capabilities: List[str] = field(default_factory=list)  # ["browser", "network"]
    requires_confirmation: List[str] = field(default_factory=list)  # ["file_write", "system_command"]
    max_requests_per_minute: int = 60


class CapabilityInspector:
    """
    Capability Inspector - Security-First Approach

    Detects available capabilities from deployment config (NEVER asks users)
    Provides constraints to Planner
    Validates execution plans before execution
    """

    def __init__(self):
        """Initialize capability inspector and detect available capabilities"""
        self.capabilities: Dict[str, Capability] = {}
        self._detect_capabilities()

    def _detect_capabilities(self):
        """
        Detect available capabilities from environment
        IMPORTANT: Only check environment variables, NEVER ask user for credentials
        """
        # 1. Browser automation
        self.capabilities['browser'] = self._check_browser()

        # 2. API keys (from env vars only, NOT from user input)
        self.capabilities['openai_api'] = self._check_env_key('OPENAI_API_KEY', 'OpenAI')
        self.capabilities['anthropic_api'] = self._check_env_key('ANTHROPIC_API_KEY', 'Anthropic')
        self.capabilities['google_api'] = self._check_env_key('GOOGLE_API_KEY', 'Google')

        # 3. File system (always available in current implementation)
        self.capabilities['file_system'] = Capability(
            name='file_system',
            type=CapabilityType.FILE_SYSTEM,
            available=True,
            metadata={'writable': True}
        )

        # 4. Network access (always available)
        self.capabilities['network'] = Capability(
            name='network',
            type=CapabilityType.NETWORK,
            available=True
        )

        # Log summary
        available_caps = [c.name for c in self.capabilities.values() if c.available]
        unavailable_caps = [c.name for c in self.capabilities.values() if not c.available]

        logger.info(f"Capabilities available: {', '.join(available_caps)}")
        if unavailable_caps:
            logger.info(f"Capabilities unavailable: {', '.join(unavailable_caps)}")

    def _check_browser(self) -> Capability:
        """Check if browser automation is available"""
        try:
            from playwright.sync_api import sync_playwright
            return Capability(
                name='browser',
                type=CapabilityType.BROWSER,
                available=True,
                metadata={'engine': 'playwright'}
            )
        except ImportError:
            return Capability(
                name='browser',
                type=CapabilityType.BROWSER,
                available=False,
                reason="Playwright not installed"
            )

    def _check_env_key(self, env_var: str, service_name: str) -> Capability:
        """
        Check if API key exists in environment

        Args:
            env_var: Environment variable name (e.g., 'OPENAI_API_KEY')
            service_name: Human-readable service name (e.g., 'OpenAI')

        Returns:
            Capability object indicating availability
        """
        api_key = os.getenv(env_var)

        if api_key and len(api_key) > 10:
            return Capability(
                name=f"{service_name.lower()}_api",
                type=CapabilityType.API_KEY,
                available=True,
                metadata={'service': service_name}
            )
        else:
            return Capability(
                name=f"{service_name.lower()}_api",
                type=CapabilityType.API_KEY,
                available=False,
                reason=f"{env_var} not set in deployment config"
            )

    def get_capability(self, name: str) -> Optional[Capability]:
        """Get specific capability by name"""
        return self.capabilities.get(name)

    def is_available(self, capability_name: str) -> bool:
        """Check if capability is available"""
        cap = self.capabilities.get(capability_name)
        return cap.available if cap else False

    def get_unavailable_reason(self, capability_name: str) -> str:
        """Get reason why capability is unavailable"""
        cap = self.capabilities.get(capability_name)
        if not cap:
            return f"Unknown capability: {capability_name}"
        return cap.reason or "Available"

    def generate_constraint_message(self) -> str:
        """
        Generate constraint message for Planner

        Returns:
            Text description of what system CAN and CANNOT do
        """
        available = [c for c in self.capabilities.values() if c.available]
        unavailable = [c for c in self.capabilities.values() if not c.available]

        message = "SYSTEM CAPABILITIES:\n\n"

        message += "Available:\n"
        for cap in available:
            message += f"  - {cap.name}: {cap.type.value}\n"

        if unavailable:
            message += "\nNOT Available (do not plan these):\n"
            for cap in unavailable:
                message += f"  - {cap.name}: {cap.reason}\n"

        message += "\nIMPORTANT: Only use available capabilities. Do not ask users for API keys."

        return message

    def validate_plan(self, plan: Dict) -> tuple:
        """
        Validate if plan uses only available capabilities

        Args:
            plan: Execution plan with steps

        Returns:
            (is_valid: bool, errors: List[str])
        """
        errors = []

        for step in plan.get('steps', []):
            module_id = step.get('module', '')

            # Check if module requires unavailable capability
            required_cap = self._get_required_capability(module_id)

            if required_cap and not self.is_available(required_cap):
                reason = self.get_unavailable_reason(required_cap)
                errors.append(
                    f"Step '{step.get('id')}' requires '{required_cap}' which is unavailable: {reason}"
                )

        return (len(errors) == 0, errors)

    def _get_required_capability(self, module_id: str) -> Optional[str]:
        """
        Map module ID to required capability

        Args:
            module_id: Module identifier (e.g., 'browser.launch', 'openai.chat')

        Returns:
            Required capability name or None
        """
        # Browser modules
        if module_id.startswith('browser.'):
            return 'browser'

        # API modules
        if 'openai' in module_id.lower():
            return 'openai_api'
        if 'anthropic' in module_id.lower():
            return 'anthropic_api'
        if 'google' in module_id.lower():
            return 'google_api'

        # File modules
        if module_id.startswith('file.'):
            return 'file_system'

        return None


class SecurityEnforcer:
    """
    Enforce security policies for jobs
    Provides per-job security boundaries and audit logging
    """

    def __init__(self):
        """Initialize security enforcer"""
        self.logger = logging.getLogger(__name__)
        self._job_memory = None

    @property
    def job_memory(self):
        """Lazy-load job memory to avoid circular dependency"""
        if self._job_memory is None:
            self._job_memory = get_job_memory()
        return self._job_memory

    def get_policy(self, job_id: str) -> SecurityPolicy:
        """
        Get security policy for job

        Args:
            job_id: Job ID

        Returns:
            SecurityPolicy object

        Raises:
            ValueError: If job not found
        """
        job = self.job_memory.get_job(job_id)

        if not job:
            raise ValueError(f"Job not found: {job_id}")

        policy_data = job.get('security_policy')

        if policy_data:
            # Load policy from job metadata
            if isinstance(policy_data, str):
                import json
                policy_data = json.loads(policy_data)

            return SecurityPolicy(
                allowed_domains=policy_data.get('allowed_domains', []),
                allowed_capabilities=policy_data.get('allowed_capabilities', []),
                requires_confirmation=policy_data.get('requires_confirmation', []),
                max_requests_per_minute=policy_data.get('max_requests_per_minute', 60)
            )
        else:
            # Default policy: safe defaults
            return SecurityPolicy(
                allowed_domains=['*'],  # Allow all by default
                allowed_capabilities=['browser', 'network', 'file_system'],
                requires_confirmation=['system_command'],
                max_requests_per_minute=60
            )

    def check_domain_allowed(self, job_id: str, url: str) -> tuple:
        """
        Check if URL is allowed by job policy

        Args:
            job_id: Job ID
            url: URL to check

        Returns:
            (allowed: bool, reason: str)
        """
        policy = self.get_policy(job_id)

        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc

        # Check wildcard
        if '*' in policy.allowed_domains:
            return (True, "All domains allowed")

        # Check exact match
        if domain in policy.allowed_domains:
            return (True, f"Domain {domain} is whitelisted")

        # Check wildcard subdomains (e.g., *.google.com)
        for pattern in policy.allowed_domains:
            if pattern.startswith('*.'):
                base_domain = pattern[2:]
                # Match only if domain ends with .base_domain (not just base_domain)
                # e.g., www.example.com matches *.example.com
                # but example.com does NOT match *.example.com
                if domain.endswith('.' + base_domain):
                    return (True, f"Domain {domain} matches pattern {pattern}")

        # Denied
        self.job_memory.log_event(
            job_id=job_id,
            event_type=JobEventType.SECURITY_VIOLATION,
            payload={
                'violation_type': 'domain_not_allowed',
                'url': url,
                'domain': domain,
                'allowed_domains': policy.allowed_domains
            }
        )

        return (False, f"Domain {domain} not in allowed list: {policy.allowed_domains}")

    def check_action_allowed(self, job_id: str, action: str) -> tuple:
        """
        Check if action is allowed

        Args:
            job_id: Job ID
            action: Action name like 'file_write', 'system_command', etc.

        Returns:
            (allowed: bool, reason_or_confirmation_required: str)
        """
        policy = self.get_policy(job_id)

        # Check if action requires confirmation
        if action in policy.requires_confirmation:
            return (False, f"Action '{action}' requires user confirmation")

        return (True, "Action allowed")

    def log_permission_check(
        self,
        job_id: str,
        check_type: str,
        result: bool,
        details: Dict
    ):
        """
        Log permission check for audit trail

        Args:
            job_id: Job ID
            check_type: Type of check (e.g., 'domain_access', 'action')
            result: Whether permission was granted
            details: Additional details about the check
        """
        self.job_memory.log_event(
            job_id=job_id,
            event_type=JobEventType.PERMISSION_CHECK,
            payload={
                'check_type': check_type,
                'result': 'allowed' if result else 'denied',
                'details': details
            }
        )


class JobMemoryStore:
    """
    Job Memory Storage System

    Features:
    1. Manage job lifecycle (create, update, complete, fail)
    2. Store task conversation history
    3. Provide conversation context retrieval
    4. Auto-cleanup expired tasks
    5. Support cloud databases (Postgres/MySQL) or local SQLite
    """

    # State transition rules: current_state -> [allowed_next_states]
    STATE_TRANSITIONS = {
        JobStatus.QUEUED: [
            JobStatus.PLANNING,
            JobStatus.CANCELLED
        ],
        JobStatus.PLANNING: [
            JobStatus.EXECUTING,
            JobStatus.FAILED,
            JobStatus.CANCELLED
        ],
        JobStatus.EXECUTING: [
            JobStatus.PAUSED,
            JobStatus.WAITING_USER_INPUT,
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.TIMEOUT,
            JobStatus.CANCELLED
        ],
        JobStatus.PAUSED: [
            JobStatus.EXECUTING,
            JobStatus.CANCELLED
        ],
        JobStatus.WAITING_USER_INPUT: [
            JobStatus.EXECUTING,
            JobStatus.TIMEOUT,
            JobStatus.CANCELLED
        ],
        JobStatus.COMPLETED: [],  # Terminal state
        JobStatus.FAILED: [],      # Terminal state
        JobStatus.CANCELLED: [],   # Terminal state
        JobStatus.TIMEOUT: []      # Terminal state
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize JobMemory

        Args:
            config_path: Path to config file, defaults to config/memory_config.yaml
        """
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent.parent / "config" / "memory_config.yaml"

        self.config = self._load_config(config_path)
        self.backend_type = self.config['job_memory']['backend']

        # Initialize database connection
        self.db = None
        self._init_database()

        # Configuration parameters
        self.max_messages_per_job = self.config['job_memory']['conversation']['max_messages_per_job']
        self.context_limit = self.config['job_memory']['conversation']['context_limit']

        # Initialize language detector
        self.language_detector = LanguageDetector()

        logger.info(f"JobMemory initialized with backend: {self.backend_type}")

    def _load_config(self, config_path: Path) -> Dict:
        """Load configuration file"""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Replace environment variables
            import re
            def replace_env(match):
                var_name = match.group(1)
                default = match.group(2) if match.group(2) else None
                value = os.getenv(var_name, default)
                if value is None:
                    raise ValueError(f"Environment variable {var_name} not set and no default provided")
                return value

            # Support ${VAR} and ${VAR:default} formats
            content = re.sub(r'\$\{([A-Z_]+)(?::([^\}]+))?\}', replace_env, content)

            return yaml.safe_load(content)

    def _init_database(self):
        """Initialize database connection"""
        if self.backend_type == "postgres":
            self._init_postgres()
        elif self.backend_type == "mysql":
            self._init_mysql()
        elif self.backend_type == "sqlite":
            self._init_sqlite()
        else:
            raise ValueError(f"Unsupported backend: {self.backend_type}")

        # Create tables
        self._create_tables()

    def _init_postgres(self):
        """Initialize PostgreSQL connection"""
        try:
            import psycopg2
            from psycopg2 import pool

            conn_config = self.config['job_memory']['connection']['postgres']
            pool_config = self.config['performance']['connection_pool']

            self.db_pool = pool.ThreadedConnectionPool(
                pool_config['min_size'],
                pool_config['max_size'],
                host=conn_config['host'],
                port=conn_config['port'],
                database=conn_config['database'],
                user=conn_config['user'],
                password=conn_config['password'],
                sslmode=conn_config['ssl_mode']
            )

            logger.info("PostgreSQL connection pool initialized")
        except ImportError:
            raise ImportError("psycopg2 not installed. Install with: pip install psycopg2-binary")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")
            raise

    def _init_mysql(self):
        """Initialize MySQL connection"""
        try:
            import mysql.connector
            from mysql.connector import pooling

            conn_config = self.config['job_memory']['connection']['mysql']
            pool_config = self.config['performance']['connection_pool']

            self.db_pool = pooling.MySQLConnectionPool(
                pool_name="flyto2_pool",
                pool_size=pool_config['max_size'],
                host=conn_config['host'],
                port=conn_config['port'],
                database=conn_config['database'],
                user=conn_config['user'],
                password=conn_config['password'],
                charset=conn_config['charset']
            )

            logger.info("MySQL connection pool initialized")
        except ImportError:
            raise ImportError("mysql-connector-python not installed. Install with: pip install mysql-connector-python")
        except Exception as e:
            logger.error(f"Failed to initialize MySQL: {e}")
            raise

    def _init_sqlite(self):
        """Initialize SQLite connection"""
        import sqlite3

        db_path = Path(self.config['job_memory']['connection']['sqlite']['path'])
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db = sqlite3.connect(
            db_path,
            check_same_thread=self.config['job_memory']['connection']['sqlite']['check_same_thread']
        )
        self.db.row_factory = sqlite3.Row

        logger.info(f"SQLite initialized at: {db_path}")

    def _get_connection(self):
        """Get database connection"""
        if self.backend_type == "sqlite":
            return self.db
        else:
            return self.db_pool.getconn()

    def _release_connection(self, conn):
        """Release database connection"""
        if self.backend_type in ["postgres", "mysql"]:
            self.db_pool.putconn(conn)

    def _create_tables(self):
        """Create database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Jobs table
            if self.backend_type == "sqlite":
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        job_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        task_description TEXT,
                        status TEXT NOT NULL,
                        preferred_language VARCHAR(10) DEFAULT 'en',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        metadata TEXT
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS job_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        detected_language VARCHAR(10),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT,
                        FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
                    )
                """)

                # Job events table (audit trail)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS job_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        payload TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
                    )
                """)

                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_messages_job_id ON job_messages(job_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_messages_timestamp ON job_messages(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_events_job_id ON job_events(job_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_events_type ON job_events(event_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_events_timestamp ON job_events(timestamp)")

            else:  # PostgreSQL or MySQL
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        job_id VARCHAR(255) PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        task_description TEXT,
                        status VARCHAR(50) NOT NULL,
                        preferred_language VARCHAR(10) DEFAULT 'en',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        metadata JSON
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS job_messages (
                        id SERIAL PRIMARY KEY,
                        job_id VARCHAR(255) NOT NULL,
                        role VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        detected_language VARCHAR(10),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata JSON,
                        FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
                    )
                """)

                # Job events table (audit trail)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS job_events (
                        id SERIAL PRIMARY KEY,
                        job_id VARCHAR(255) NOT NULL,
                        event_type VARCHAR(100) NOT NULL,
                        payload JSON,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
                    )
                """)

                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_messages_job_id ON job_messages(job_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_messages_timestamp ON job_messages(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_events_job_id ON job_events(job_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_events_type ON job_events(event_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_events_timestamp ON job_events(timestamp)")

            conn.commit()
            logger.info("Database tables created successfully")

            # Run migrations to add new columns if they don't exist
            self._run_migrations(conn, cursor)

        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            self._release_connection(conn)

    def _run_migrations(self, conn, cursor):
        """
        Run database migrations to add new columns/features to existing tables

        Args:
            conn: Database connection
            cursor: Database cursor
        """
        try:
            # Migration: Add preferred_language column to jobs table (Phase 2.2)
            if self.backend_type == "sqlite":
                # Check if column exists
                cursor.execute("PRAGMA table_info(jobs)")
                columns = [row[1] for row in cursor.fetchall()]
                if 'preferred_language' not in columns:
                    cursor.execute("ALTER TABLE jobs ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en'")
                    conn.commit()
                    logger.info("Migration: Added preferred_language column to jobs table")
            else:  # PostgreSQL or MySQL
                # Check if column exists
                cursor.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'jobs' AND column_name = 'preferred_language'
                """)
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE jobs ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en'")
                    conn.commit()
                    logger.info("Migration: Added preferred_language column to jobs table")

            # Migration: Add security_policy column to jobs table (Phase 3.2)
            if self.backend_type == "sqlite":
                # Check if column exists
                cursor.execute("PRAGMA table_info(jobs)")
                columns = [row[1] for row in cursor.fetchall()]
                if 'security_policy' not in columns:
                    cursor.execute("ALTER TABLE jobs ADD COLUMN security_policy TEXT")
                    conn.commit()
                    logger.info("Migration: Added security_policy column to jobs table")
            else:  # PostgreSQL or MySQL
                # Check if column exists
                cursor.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'jobs' AND column_name = 'security_policy'
                """)
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE jobs ADD COLUMN security_policy TEXT")
                    conn.commit()
                    logger.info("Migration: Added security_policy column to jobs table")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            conn.rollback()
            # Don't raise - migrations are best-effort

    # ============================================================
    # Job Management
    # ============================================================

    def create_job(
        self,
        user_id: str,
        task_description: str,
        preferred_language: str = "en",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Create new task with language preference

        Args:
            user_id: User ID
            task_description: Task description
            preferred_language: User's preferred language (e.g., 'zh', 'ja', 'en')
            metadata: Task metadata

        Returns:
            job_id: Job ID
        """
        import uuid
        job_id = f"job_{uuid.uuid4().hex[:16]}"

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            import json

            # Extract security_policy from metadata if present (Phase 3.2)
            security_policy = None
            remaining_metadata = None
            if metadata:
                metadata_copy = metadata.copy()
                security_policy = metadata_copy.pop('security_policy', None)
                remaining_metadata = metadata_copy if metadata_copy else None

            metadata_str = json.dumps(remaining_metadata) if remaining_metadata else None
            security_policy_str = json.dumps(security_policy) if security_policy else None

            cursor.execute("""
                INSERT INTO jobs (job_id, user_id, task_description, preferred_language, status, metadata, security_policy)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """ if self.backend_type == "sqlite" else """
                INSERT INTO jobs (job_id, user_id, task_description, preferred_language, status, metadata, security_policy)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (job_id, user_id, task_description, preferred_language, JobStatus.QUEUED.value, metadata_str, security_policy_str))

            conn.commit()
            logger.info(f"Job created: {job_id}")

            # Log job creation event
            self.log_event(
                job_id=job_id,
                event_type=JobEventType.JOB_CREATED,
                payload={
                    'user_id': user_id,
                    'task_description': task_description,
                    'metadata': metadata
                }
            )

            return job_id

        except Exception as e:
            logger.error(f"Failed to create job: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            self._release_connection(conn)

    def update_job_status(self, job_id: str, status: JobStatus, reason: Optional[str] = None):
        """
        Update job status with state transition validation

        Args:
            job_id: Job ID
            status: New status
            reason: Optional reason for status change
        """
        # Get current job status
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        current_status_str = job['status']

        # Find matching JobStatus enum (handle aliases)
        current_status = None
        for s in JobStatus:
            if s.value == current_status_str:
                current_status = s
                break

        if not current_status:
            logger.warning(f"Unknown current status: {current_status_str}, allowing transition")
        else:
            # Validate state transition
            allowed_transitions = self.STATE_TRANSITIONS.get(current_status, [])

            if status not in allowed_transitions:
                # Allow transition if current state is terminal and trying to move to same state
                if current_status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED, JobStatus.TIMEOUT]:
                    if status == current_status:
                        logger.debug(f"Job {job_id} already in terminal state {status.value}")
                        return
                    else:
                        raise ValueError(
                            f"Invalid state transition: {current_status.value} -> {status.value}. "
                            f"Terminal states cannot transition to other states."
                        )
                else:
                    raise ValueError(
                        f"Invalid state transition: {current_status.value} -> {status.value}. "
                        f"Allowed transitions: {[s.value for s in allowed_transitions]}"
                    )

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Set completed_at for terminal states
            completed_at = datetime.now() if status in [
                JobStatus.COMPLETED,
                JobStatus.FAILED,
                JobStatus.CANCELLED,
                JobStatus.TIMEOUT
            ] else None

            if self.backend_type == "sqlite":
                cursor.execute("""
                    UPDATE jobs
                    SET status = ?, updated_at = ?, completed_at = ?
                    WHERE job_id = ?
                """, (status.value, datetime.now(), completed_at, job_id))
            else:
                cursor.execute("""
                    UPDATE jobs
                    SET status = %s, updated_at = %s, completed_at = %s
                    WHERE job_id = %s
                """, (status.value, datetime.now(), completed_at, job_id))

            conn.commit()
            logger.info(f"Job {job_id} status: {current_status_str} -> {status.value}")

            # Log status change event
            self.log_event(
                job_id=job_id,
                event_type=JobEventType.JOB_STATUS_CHANGED,
                payload={
                    'from_status': current_status_str,
                    'to_status': status.value,
                    'reason': reason
                }
            )

        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            self._release_connection(conn)

    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job information"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Use explicit column names to avoid index issues after migrations
            if self.backend_type == "sqlite":
                cursor.execute("""
                    SELECT job_id, user_id, task_description, status, preferred_language,
                           created_at, updated_at, completed_at, metadata, security_policy
                    FROM jobs WHERE job_id = ? LIMIT 1
                """, (job_id,))
            else:
                cursor.execute("""
                    SELECT job_id, user_id, task_description, status, preferred_language,
                           created_at, updated_at, completed_at, metadata, security_policy
                    FROM jobs WHERE job_id = %s LIMIT 1
                """, (job_id,))

            row = cursor.fetchone()

            if row:
                import json
                # For SQLite, metadata is TEXT and needs json.loads()
                # For PostgreSQL, metadata is JSON and already parsed
                if self.backend_type == "sqlite":
                    metadata = json.loads(row[8]) if row[8] else None
                    security_policy = json.loads(row[9]) if row[9] else None
                else:
                    metadata = row[8] if row[8] else None
                    security_policy = row[9] if row[9] else None

                return {
                    'job_id': row[0],
                    'user_id': row[1],
                    'task_description': row[2],
                    'status': row[3],
                    'preferred_language': row[4],  # Added in Phase 2.2
                    'created_at': row[5],
                    'updated_at': row[6],
                    'completed_at': row[7],
                    'metadata': metadata,
                    'security_policy': security_policy  # Added in Phase 3.2
                }
            return None

        finally:
            cursor.close()
            self._release_connection(conn)

    # ============================================================
    # Conversation Memory Management
    # ============================================================

    def add_message(self, job_id: str, role: str, content: str,
                    detected_language: Optional[str] = None,
                    metadata: Optional[Dict] = None):
        """
        Add conversation message with language detection

        Args:
            job_id: Job ID
            role: Role ('user' | 'assistant' | 'system')
            content: Message content
            detected_language: Detected language code (auto-detected if not provided)
            metadata: Message metadata
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            import json
            metadata_str = json.dumps(metadata) if metadata else None

            # Auto-detect language if not provided
            if detected_language is None and content:
                lang_code, confidence = self.language_detector.detect(content)
                detected_language = lang_code if confidence > 0.5 else None

            cursor.execute("""
                INSERT INTO job_messages (job_id, role, content, detected_language, metadata)
                VALUES (?, ?, ?, ?, ?)
            """ if self.backend_type == "sqlite" else """
                INSERT INTO job_messages (job_id, role, content, detected_language, metadata)
                VALUES (%s, %s, %s, %s, %s)
            """, (job_id, role, content, detected_language, metadata_str))

            conn.commit()

            # Check message count limit
            self._trim_messages(job_id)

        except Exception as e:
            logger.error(f"Failed to add message: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            self._release_connection(conn)

    def _trim_messages(self, job_id: str):
        """Trim messages to keep only the most recent N messages"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Count messages
            if self.backend_type == "sqlite":
                cursor.execute("SELECT COUNT(*) FROM job_messages WHERE job_id = ?", (job_id,))
            else:
                cursor.execute("SELECT COUNT(*) FROM job_messages WHERE job_id = %s", (job_id,))

            count = cursor.fetchone()[0]

            if count > self.max_messages_per_job:
                # Delete oldest messages
                delete_count = count - self.max_messages_per_job

                if self.backend_type == "sqlite":
                    cursor.execute("""
                        DELETE FROM job_messages
                        WHERE job_id = ? AND id IN (
                            SELECT id FROM job_messages
                            WHERE job_id = ?
                            ORDER BY timestamp ASC
                            LIMIT ?
                        )
                    """, (job_id, job_id, delete_count))
                else:
                    cursor.execute("""
                        DELETE FROM job_messages
                        WHERE job_id = %s AND id IN (
                            SELECT id FROM job_messages
                            WHERE job_id = %s
                            ORDER BY timestamp ASC
                            LIMIT %s
                        )
                    """, (job_id, job_id, delete_count))

                conn.commit()
                logger.info(f"Trimmed {delete_count} old messages from job {job_id}")

        except Exception as e:
            logger.error(f"Failed to trim messages: {e}")
            conn.rollback()
        finally:
            cursor.close()
            self._release_connection(conn)

    def get_conversation(self, job_id: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Get task conversation history

        Args:
            job_id: Job ID
            limit: Limit number of messages to return (defaults to context_limit)

        Returns:
            List of conversation messages
        """
        if limit is None:
            limit = self.context_limit

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if self.backend_type == "sqlite":
                cursor.execute("""
                    SELECT role, content, timestamp, metadata, detected_language
                    FROM job_messages
                    WHERE job_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (job_id, limit))
            else:
                cursor.execute("""
                    SELECT role, content, timestamp, metadata, detected_language
                    FROM job_messages
                    WHERE job_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (job_id, limit))

            rows = cursor.fetchall()

            import json
            messages = []
            for row in reversed(rows):  # Reverse to get correct order
                messages.append({
                    'role': row[0],
                    'content': row[1],
                    'timestamp': row[2],
                    'metadata': json.loads(row[3]) if row[3] else None,
                    'detected_language': row[4] if len(row) > 4 else None
                })

            return messages

        finally:
            cursor.close()
            self._release_connection(conn)

    def get_context_for_llm(self, job_id: str, current_query: str) -> str:
        """
        Prepare conversation context for LLM

        Args:
            job_id: Job ID
            current_query: Current query

        Returns:
            Formatted context string
        """
        messages = self.get_conversation(job_id)

        context_parts = []
        context_parts.append(f"Job ID: {job_id}")

        # Get task description
        job = self.get_job(job_id)
        if job and job['task_description']:
            context_parts.append(f"Task description: {job['task_description']}")

        context_parts.append("\nConversation history:")

        for msg in messages:
            role_name = {
                'user': 'User',
                'assistant': 'Assistant',
                'system': 'System'
            }.get(msg['role'], msg['role'])

            context_parts.append(f"{role_name}: {msg['content']}")

        context_parts.append(f"\nCurrent question: {current_query}")

        return "\n".join(context_parts)

    # ============================================================
    # Cleanup and Maintenance
    # ============================================================

    def cleanup_old_jobs(self):
        """Clean up expired tasks"""
        retention = self.config['job_memory']['retention']

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            now = datetime.now()

            # Clean up completed jobs
            completed_cutoff = now - timedelta(days=retention['completed_jobs_days'])
            cursor.execute("""
                DELETE FROM jobs
                WHERE status = ? AND completed_at < ?
            """ if self.backend_type == "sqlite" else """
                DELETE FROM jobs
                WHERE status = %s AND completed_at < %s
            """, (JobStatus.COMPLETED.value, completed_cutoff))

            # Clean up failed jobs
            failed_cutoff = now - timedelta(days=retention['failed_jobs_days'])
            cursor.execute("""
                DELETE FROM jobs
                WHERE status = ? AND completed_at < ?
            """ if self.backend_type == "sqlite" else """
                DELETE FROM jobs
                WHERE status = %s AND completed_at < %s
            """, (JobStatus.FAILED.value, failed_cutoff))

            # Mark timed out jobs
            timeout_cutoff = now - timedelta(days=retention['in_progress_timeout_days'])
            cursor.execute("""
                UPDATE jobs
                SET status = ?, updated_at = ?
                WHERE status = ? AND updated_at < ?
            """ if self.backend_type == "sqlite" else """
                UPDATE jobs
                SET status = %s, updated_at = %s
                WHERE status = %s AND updated_at < %s
            """, (JobStatus.TIMEOUT.value, now, JobStatus.IN_PROGRESS.value, timeout_cutoff))

            conn.commit()
            logger.info("Old jobs cleaned up successfully")

        except Exception as e:
            logger.error(f"Failed to cleanup old jobs: {e}")
            conn.rollback()
        finally:
            cursor.close()
            self._release_connection(conn)

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            stats = {}

            # Job statistics
            cursor.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
            status_counts = {row[0]: row[1] for row in cursor.fetchall()}
            stats['jobs_by_status'] = status_counts

            # Message statistics
            cursor.execute("SELECT COUNT(*) FROM job_messages")
            stats['total_messages'] = cursor.fetchone()[0]

            return stats

        finally:
            cursor.close()
            self._release_connection(conn)

    # ============================================================
    # Event Logging (Audit Trail)
    # ============================================================

    def log_event(self, job_id: str, event_type: JobEventType, payload: Optional[Dict] = None):
        """
        Log structured event for audit trail

        Args:
            job_id: Job ID
            event_type: Event type from JobEventType enum
            payload: Event-specific data (JSON-serializable)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            import json
            payload_str = json.dumps(payload) if payload else None

            cursor.execute("""
                INSERT INTO job_events (job_id, event_type, payload)
                VALUES (?, ?, ?)
            """ if self.backend_type == "sqlite" else """
                INSERT INTO job_events (job_id, event_type, payload)
                VALUES (%s, %s, %s)
            """, (job_id, event_type.value, payload_str))

            conn.commit()
            logger.debug(f"Event logged: {event_type.value} for job {job_id}")

        except Exception as e:
            logger.error(f"Failed to log event: {e}")
            conn.rollback()
        finally:
            cursor.close()
            self._release_connection(conn)

    def get_job_timeline(self, job_id: str) -> List[Dict]:
        """
        Get chronological timeline of all events for a job

        Args:
            job_id: Job ID

        Returns:
            List of events with timestamp, type, and payload
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if self.backend_type == "sqlite":
                cursor.execute("""
                    SELECT event_type, payload, timestamp
                    FROM job_events
                    WHERE job_id = ?
                    ORDER BY timestamp ASC
                """, (job_id,))
            else:
                cursor.execute("""
                    SELECT event_type, payload, timestamp
                    FROM job_events
                    WHERE job_id = %s
                    ORDER BY timestamp ASC
                """, (job_id,))

            rows = cursor.fetchall()

            import json
            events = []
            for row in rows:
                events.append({
                    'event_type': row[0],
                    'payload': json.loads(row[1]) if row[1] else None,
                    'timestamp': row[2]
                })

            return events

        finally:
            cursor.close()
            self._release_connection(conn)

    # ============================================================
    # Job Cleanup and Retention
    # ============================================================

    def cleanup_old_jobs(self) -> Dict[str, int]:
        """
        Cleanup old jobs based on retention policy

        Returns:
            Dictionary with cleanup statistics
        """
        from datetime import timedelta

        stats = {
            'completed_deleted': 0,
            'failed_deleted': 0,
            'timeout_marked': 0
        }

        try:
            # 1. Delete old completed jobs
            completed_days = self.config['job_memory']['retention']['completed_jobs_days']
            stats['completed_deleted'] = self._delete_jobs_by_status_and_age(
                JobStatus.COMPLETED,
                completed_days
            )

            # 2. Delete old failed jobs
            failed_days = self.config['job_memory']['retention']['failed_jobs_days']
            stats['failed_deleted'] = self._delete_jobs_by_status_and_age(
                JobStatus.FAILED,
                failed_days
            )

            # 3. Mark stuck in-progress jobs as TIMEOUT
            timeout_days = self.config['job_memory']['retention']['in_progress_timeout_days']
            stats['timeout_marked'] = self._mark_stuck_jobs_as_timeout(timeout_days)

            logger.info(f"Cleanup completed: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return stats

    def _delete_jobs_by_status_and_age(self, status: JobStatus, days: int) -> int:
        """
        Delete jobs with specific status older than specified days

        Args:
            status: Job status to delete
            days: Age in days

        Returns:
            Number of jobs deleted
        """
        from datetime import timedelta

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            # Get jobs to delete
            if self.backend_type == "sqlite":
                cursor.execute("""
                    SELECT job_id FROM jobs
                    WHERE status = ?
                    AND updated_at < ?
                """, (status.value, cutoff_date))
            else:
                cursor.execute("""
                    SELECT job_id FROM jobs
                    WHERE status = %s
                    AND updated_at < %s
                """, (status.value, cutoff_date))

            job_ids = [row[0] for row in cursor.fetchall()]

            # Delete jobs and their related data (CASCADE will handle job_events)
            deleted_count = 0
            for job_id in job_ids:
                if self.backend_type == "sqlite":
                    # Delete job messages
                    cursor.execute("DELETE FROM job_messages WHERE job_id = ?", (job_id,))
                    # Delete job
                    cursor.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
                else:
                    cursor.execute("DELETE FROM job_messages WHERE job_id = %s", (job_id,))
                    cursor.execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))

                deleted_count += 1

            conn.commit()

            logger.info(f"Deleted {deleted_count} {status.value} jobs older than {days} days")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete old jobs: {e}")
            conn.rollback()
            return 0

        finally:
            cursor.close()
            self._release_connection(conn)

    def _mark_stuck_jobs_as_timeout(self, days: int) -> int:
        """
        Mark in-progress jobs as TIMEOUT if inactive for too long

        Args:
            days: Inactivity threshold in days

        Returns:
            Number of jobs marked as timeout
        """
        from datetime import timedelta

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            # Find stuck in-progress jobs
            if self.backend_type == "sqlite":
                cursor.execute("""
                    SELECT job_id FROM jobs
                    WHERE status = ?
                    AND updated_at < ?
                """, (JobStatus.EXECUTING.value, cutoff_date))
            else:
                cursor.execute("""
                    SELECT job_id FROM jobs
                    WHERE status = %s
                    AND updated_at < %s
                """, (JobStatus.EXECUTING.value, cutoff_date))

            stuck_job_ids = [row[0] for row in cursor.fetchall()]

            # Mark each as TIMEOUT
            timeout_count = 0
            for job_id in stuck_job_ids:
                self.update_job_status(
                    job_id,
                    JobStatus.TIMEOUT,
                    reason=f"Automatic timeout after {days} days of inactivity"
                )
                timeout_count += 1

            logger.info(f"Marked {timeout_count} stuck jobs as TIMEOUT")
            return timeout_count

        except Exception as e:
            logger.error(f"Failed to mark stuck jobs: {e}")
            return 0

        finally:
            cursor.close()
            self._release_connection(conn)

    def start_cleanup_scheduler(self, callback=None):
        """
        Start background cleanup scheduler

        Args:
            callback: Optional callback function after each cleanup
        """
        import threading
        import time

        cleanup_interval = self.config['job_memory']['retention']['cleanup_interval']

        def cleanup_loop():
            logger.info("Cleanup scheduler started")

            while True:
                try:
                    # Wait for interval
                    time.sleep(cleanup_interval)

                    # Run cleanup
                    logger.info("Running scheduled cleanup...")
                    stats = self.cleanup_old_jobs()

                    # Call callback if provided
                    if callback:
                        callback(stats)

                except Exception as e:
                    logger.error(f"Cleanup scheduler error: {e}")

        # Start background thread
        thread = threading.Thread(target=cleanup_loop, daemon=True)
        thread.start()
        logger.info(f"Cleanup scheduler thread started (interval: {cleanup_interval}s)")


# ============================================================
# Global Instance Management
# ============================================================

_job_memory_instance: Optional[JobMemoryStore] = None
_translator_instance: Optional[Translator] = None
_capability_inspector_instance: Optional[CapabilityInspector] = None
_security_enforcer_instance: Optional[SecurityEnforcer] = None


def get_job_memory() -> JobMemoryStore:
    """Get JobMemory singleton"""
    global _job_memory_instance
    if _job_memory_instance is None:
        _job_memory_instance = JobMemoryStore()
    return _job_memory_instance


def get_translator(ollama_endpoint: str = "http://localhost:11434") -> Translator:
    """
    Get Translator singleton

    Args:
        ollama_endpoint: Ollama API endpoint URL (default: http://localhost:11434)

    Returns:
        Translator instance
    """
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = Translator(ollama_endpoint=ollama_endpoint)
    return _translator_instance


def get_capability_inspector() -> CapabilityInspector:
    """
    Get CapabilityInspector singleton

    Returns:
        CapabilityInspector instance
    """
    global _capability_inspector_instance
    if _capability_inspector_instance is None:
        _capability_inspector_instance = CapabilityInspector()
    return _capability_inspector_instance


def get_security_enforcer() -> SecurityEnforcer:
    """
    Get SecurityEnforcer singleton

    Returns:
        SecurityEnforcer instance
    """
    global _security_enforcer_instance
    if _security_enforcer_instance is None:
        _security_enforcer_instance = SecurityEnforcer()
    return _security_enforcer_instance
