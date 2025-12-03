"""
Job Resume Module
Allows resuming unfinished tasks after machine restart or crash
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

from src.core.memory.job_memory import get_job_memory, JobStatus

logger = logging.getLogger(__name__)


class JobResumer:
    """
    Job Resumer

    Functions:
    1. Resume interrupted tasks
    2. Auto-scan stuck tasks
    3. Notify users about unfinished tasks
    """

    def __init__(self):
        """Initialize JobResumer"""
        self.job_memory = get_job_memory()

    def resume_job(self, user_id: str, job_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Resume specified task

        Args:
            user_id: User ID
            job_id: Job ID

        Returns:
            (success, message, job_data)
        """
        try:
            # 1. Validate job exists
            job = self.job_memory.get_job(job_id)

            if job is None:
                return False, f"Job not found: {job_id}", None

            # 2. Validate permission
            if job['user_id'] != user_id:
                logger.warning(f"User {user_id} attempted to resume job {job_id} owned by {job['user_id']}")
                return False, "Access denied to this job", None

            # 3. Check job status
            if job['status'] == JobStatus.COMPLETED.value:
                return False, "Job already completed, cannot resume", None

            if job['status'] == JobStatus.FAILED.value:
                return False, "Job failed, please create a new task", None

            # 4. Read conversation history
            conversation = self.job_memory.get_conversation(job_id)

            # 5. Update status to in_progress
            self.job_memory.update_job_status(job_id, JobStatus.IN_PROGRESS)

            logger.info(f"Job {job_id} resumed by user {user_id}")

            # 6. Format resume message
            message = self._format_resume_message(job, conversation)

            return True, message, {
                'job': job,
                'conversation': conversation,
                'message_count': len(conversation)
            }

        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {e}")
            return False, f"Resume failed: {str(e)}", None

    def _format_resume_message(self, job: Dict, conversation: List[Dict]) -> str:
        """Format resume message"""
        task_desc = job['task_description'] or "Unnamed task"
        created_at = job['created_at']
        msg_count = len(conversation)

        # Get last message
        last_message = ""
        if conversation:
            last_msg = conversation[-1]
            role = "You" if last_msg['role'] == 'user' else "Bot"
            content = last_msg['content'][:100]
            last_message = f"\nLast message: {role}: {content}..."

        message = f"""Task resumed successfully

Task: {task_desc}
Created: {created_at}
Messages: {msg_count}{last_message}

Please continue your question, I will serve you based on previous conversation history."""

        return message

    def list_resumable_jobs(self, user_id: str) -> List[Dict]:
        """
        List user's resumable jobs

        Args:
            user_id: User ID

        Returns:
            List of resumable jobs
        """
        conn = self.job_memory._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT job_id, task_description, status, created_at, updated_at
                FROM jobs
                WHERE user_id = ? OR user_id = %s
                AND status IN ('pending', 'in_progress', 'timeout')
                ORDER BY updated_at DESC
                LIMIT 10
            """, (user_id,))

            rows = cursor.fetchall()

            jobs = []
            for row in rows:
                jobs.append({
                    'job_id': row[0],
                    'task_description': row[1],
                    'status': row[2],
                    'created_at': row[3],
                    'updated_at': row[4]
                })

            return jobs

        finally:
            cursor.close()
            self.job_memory._release_connection(conn)

    def find_stuck_jobs(self, inactive_minutes: int = 5) -> List[Dict]:
        """
        Find stuck jobs

        Args:
            inactive_minutes: Inactivity time (minutes)

        Returns:
            List of stuck jobs
        """
        conn = self.job_memory._get_connection()
        cursor = conn.cursor()

        try:
            # Calculate cutoff time
            cutoff_time = datetime.now() - timedelta(minutes=inactive_minutes)

            cursor.execute("""
                SELECT job_id, user_id, task_description, updated_at
                FROM jobs
                WHERE status = 'in_progress'
                AND updated_at < ? OR updated_at < %s
                ORDER BY updated_at ASC
            """, (cutoff_time,))

            rows = cursor.fetchall()

            stuck_jobs = []
            for row in rows:
                stuck_jobs.append({
                    'job_id': row[0],
                    'user_id': row[1],
                    'task_description': row[2],
                    'updated_at': row[3]
                })

            return stuck_jobs

        finally:
            cursor.close()
            self.job_memory._release_connection(conn)

    def auto_resume_on_startup(self, notify_callback=None):
        """
        Auto-scan and notify stuck jobs on startup

        Args:
            notify_callback: Notification callback function (user_id, message)
        """
        logger.info("Scanning for stuck jobs on startup...")

        stuck_jobs = self.find_stuck_jobs(inactive_minutes=5)

        if not stuck_jobs:
            logger.info("No stuck jobs found")
            return

        logger.warning(f"Found {len(stuck_jobs)} stuck jobs")

        for job in stuck_jobs:
            user_id = job['user_id']
            job_id = job['job_id']
            task_desc = job['task_description'] or "Unnamed task"

            message = f"""Interrupted task found

Task: {task_desc}
Job ID: {job_id}

Use /resume {job_id} to continue"""

            # Notify user
            if notify_callback:
                try:
                    notify_callback(user_id, message)
                    logger.info(f"Notified user {user_id} about stuck job {job_id}")
                except Exception as e:
                    logger.error(f"Failed to notify user {user_id}: {e}")

            # Optional: auto-mark as timeout
            # self.job_memory.update_job_status(job_id, JobStatus.TIMEOUT)


# ============================================================
# Global instance
# ============================================================

_resumer = None


def get_job_resumer() -> JobResumer:
    """Get JobResumer singleton"""
    global _resumer
    if _resumer is None:
        _resumer = JobResumer()
    return _resumer


# ============================================================
# Telegram Bot Integration Example
# ============================================================

def handle_resume_command(user_id: str, args: List[str]) -> str:
    """
    Handle /resume command

    Args:
        user_id: Telegram user_id
        args: Command arguments [job_id] (optional)

    Returns:
        Response message
    """
    resumer = get_job_resumer()

    # No args: list resumable jobs
    if not args:
        jobs = resumer.list_resumable_jobs(user_id)

        if not jobs:
            return "No unfinished tasks currently"

        message = "Unfinished tasks:\n\n"
        for i, job in enumerate(jobs, 1):
            job_id = job['job_id']
            task = job['task_description'] or "Unnamed task"
            status = job['status']
            updated = job['updated_at']

            message += f"{i}. {task[:50]}\n"
            message += f"   ID: {job_id}\n"
            message += f"   Status: {status}\n"
            message += f"   Updated: {updated}\n\n"

        message += "Use /resume <job_id> to resume a specific task"
        return message

    # With args: resume specified job
    job_id = args[0]
    success, message, data = resumer.resume_job(user_id, job_id)

    return message


# ============================================================
# Startup Script Example
# ============================================================

if __name__ == "__main__":
    import sys

    # Test: list resumable jobs
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        user_id = sys.argv[2] if len(sys.argv) > 2 else "test_user"

        resumer = get_job_resumer()
        jobs = resumer.list_resumable_jobs(user_id)

        print(f"Found {len(jobs)} resumable jobs for user {user_id}:")
        for job in jobs:
            print(f"  - {job['job_id']}: {job['task_description']}")

    # Test: find stuck jobs
    elif len(sys.argv) > 1 and sys.argv[1] == "stuck":
        resumer = get_job_resumer()
        stuck = resumer.find_stuck_jobs(inactive_minutes=5)

        print(f"Found {len(stuck)} stuck jobs:")
        for job in stuck:
            print(f"  - {job['job_id']} (user: {job['user_id']}): {job['task_description']}")

    # Test: resume job
    elif len(sys.argv) > 1 and sys.argv[1] == "resume":
        if len(sys.argv) < 4:
            print("Usage: python resume.py resume <user_id> <job_id>")
            sys.exit(1)

        user_id = sys.argv[2]
        job_id = sys.argv[3]

        resumer = get_job_resumer()
        success, message, data = resumer.resume_job(user_id, job_id)

        print(message)
        if data:
            print(f"\nConversation history: {data['message_count']} messages")

    else:
        print("Usage:")
        print("  python resume.py list [user_id]")
        print("  python resume.py stuck")
        print("  python resume.py resume <user_id> <job_id>")
