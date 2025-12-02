"""
Setup Auto-Sync for Knowledge Base
Configures automatic synchronization via Git hooks or Task Scheduler

Options:
1. Git Hook (auto-sync on commit/push)
2. Windows Task Scheduler (periodic sync)
3. Cron Job (periodic sync - Linux/Mac)
4. File Watcher (real-time sync)
"""
import sys
import platform
from pathlib import Path
import subprocess

project_root = Path(__file__).parent.parent


def setup_git_hook():
    """Setup Git post-commit hook"""
    print("\n=== Setting up Git Hook ===")

    git_hooks_dir = project_root / ".git/hooks"
    if not git_hooks_dir.exists():
        print("✗ Not a git repository")
        return False

    # Create post-commit hook
    hook_file = git_hooks_dir / "post-commit"

    hook_content = f"""#!/bin/sh
# Auto-sync knowledge base after commit

echo "Syncing knowledge base..."
cd "{project_root}"
python scripts/auto_sync_knowledge.py --mode incremental --embeddings local

exit 0
"""

    hook_file.write_text(hook_content)
    hook_file.chmod(0o755)  # Make executable

    print(f"✓ Git hook created: {hook_file}")
    print("  Knowledge base will auto-sync after each commit")

    return True


def setup_windows_task():
    """Setup Windows Task Scheduler"""
    print("\n=== Setting up Windows Task Scheduler ===")

    if platform.system() != "Windows":
        print("✗ Not on Windows")
        return False

    # Create PowerShell script
    ps_script = project_root / "scripts/run_knowledge_sync.ps1"

    ps_content = f"""# Auto-sync knowledge base
$projectRoot = "{project_root}"
cd $projectRoot

python scripts/auto_sync_knowledge.py --mode incremental --embeddings local

# Log completion
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path "logs/knowledge_sync.log" -Value "$timestamp - Scheduled sync completed"
"""

    ps_script.write_text(ps_content)

    print(f"✓ PowerShell script created: {ps_script}")
    print("\nTo schedule with Task Scheduler:")
    print("1. Open Task Scheduler (taskschd.msc)")
    print("2. Create Basic Task")
    print("3. Trigger: Daily at preferred time")
    print(f"4. Action: Start a program")
    print(f"   Program: powershell.exe")
    print(f"   Arguments: -ExecutionPolicy Bypass -File \"{ps_script}\"")
    print(f"   Start in: {project_root}")

    # Try to create task automatically
    try:
        task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2">
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2025-12-03T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-ExecutionPolicy Bypass -File "{ps_script}"</Arguments>
      <WorkingDirectory>{project_root}</WorkingDirectory>
    </Exec>
  </Actions>
  <Settings>
    <Enabled>true</Enabled>
    <AllowStartOnDemand>true</AllowStartOnDemand>
  </Settings>
</Task>"""

        task_file = project_root / "scripts/knowledge_sync_task.xml"
        task_file.write_text(task_xml)

        print(f"\n✓ Task XML created: {task_file}")
        print("\nTo import task:")
        print(f"  schtasks /Create /TN \"Flyto2_Knowledge_Sync\" /XML \"{task_file}\"")

    except Exception as e:
        print(f"✗ Could not create task XML: {e}")

    return True


def setup_cron_job():
    """Setup Cron job (Linux/Mac)"""
    print("\n=== Setting up Cron Job ===")

    if platform.system() == "Windows":
        print("✗ Use Task Scheduler on Windows")
        return False

    python_path = sys.executable
    sync_script = project_root / "scripts/auto_sync_knowledge.py"

    cron_line = f"0 * * * * cd {project_root} && {python_path} {sync_script} --mode incremental --embeddings local >> logs/knowledge_sync.log 2>&1"

    print("Add this line to crontab (runs hourly):")
    print(f"\n  {cron_line}\n")
    print("To edit crontab:")
    print("  crontab -e")
    print("\nOr run this command:")
    print(f'  (crontab -l 2>/dev/null; echo "{cron_line}") | crontab -')

    return True


def setup_file_watcher_service():
    """Setup file watcher as background service"""
    print("\n=== Setting up File Watcher Service ===")

    if platform.system() == "Windows":
        # Create Windows service script
        service_script = project_root / "scripts/start_file_watcher.bat"

        bat_content = f"""@echo off
echo Starting Knowledge Base File Watcher...
cd /d "{project_root}"
python scripts/auto_sync_knowledge.py --mode watch --interval 300 --embeddings local
pause
"""

        service_script.write_text(bat_content)

        print(f"✓ File watcher script created: {service_script}")
        print("\nTo start file watcher:")
        print(f"  Double-click: {service_script}")
        print("  Or run in terminal: python scripts/auto_sync_knowledge.py --mode watch")

    else:
        print("Run in terminal:")
        print("  python scripts/auto_sync_knowledge.py --mode watch --interval 300")
        print("\nTo run in background:")
        print("  nohup python scripts/auto_sync_knowledge.py --mode watch > logs/watcher.log 2>&1 &")

    return True


def main():
    """Main setup wizard"""
    print("=" * 60)
    print("Flyto2 Knowledge Base Auto-Sync Setup")
    print("=" * 60)

    print("\nAvailable options:")
    print("1. Git Hook (auto-sync on commit)")
    print("2. Windows Task Scheduler (daily sync)")
    print("3. Cron Job (hourly sync - Linux/Mac)")
    print("4. File Watcher (real-time sync)")
    print("5. Setup All")
    print("0. Exit")

    choice = input("\nSelect option (0-5): ").strip()

    if choice == "1":
        setup_git_hook()
    elif choice == "2":
        setup_windows_task()
    elif choice == "3":
        setup_cron_job()
    elif choice == "4":
        setup_file_watcher_service()
    elif choice == "5":
        setup_git_hook()
        if platform.system() == "Windows":
            setup_windows_task()
        else:
            setup_cron_job()
        setup_file_watcher_service()
    elif choice == "0":
        print("Exiting...")
        return

    print("\n" + "=" * 60)
    print("✓ Setup complete!")
    print("=" * 60)
    print("\nRecommendations:")
    print("- Git Hook: Best for development workflow")
    print("- Task Scheduler/Cron: Best for periodic updates")
    print("- File Watcher: Best for real-time sync (uses resources)")
    print("\nYou can use multiple methods together!")


if __name__ == "__main__":
    main()
