import subprocess
import uuid
from datetime import datetime


def set_reminder(title, datetime_value):
    title = str(title).strip(); datetime_value = str(datetime_value).strip()
    dt = datetime.fromisoformat(datetime_value)
    if dt <= datetime.now():
        raise ValueError("The reminder time must be in the future.")
    task_name = "AgentFlow_Reminder_" + uuid.uuid4().hex[:8]
    reminder_message = "AgentFlow Reminder: " + title
    powershell_command = (
        "Add-Type -AssemblyName PresentationFramework; "
        "[System.Windows.MessageBox]::Show("
        f"'{reminder_message.replace(chr(39), chr(39) + chr(39))}',"
        "'AgentFlow Reminder')"
    )
    command = [
        "schtasks", "/Create", "/TN", task_name, "/TR",
        f'powershell.exe -NoProfile -WindowStyle Hidden -Command "{powershell_command}"',
        "/SC", "ONCE", "/SD", dt.strftime("%m/%d/%Y"), "/ST", dt.strftime("%H:%M"), "/F",
    ]
    result = subprocess.run(command, capture_output=True, text=True, shell=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Windows could not create the reminder.")
    return f"Reminder '{title}' scheduled for {dt.strftime('%d %B %Y at %I:%M %p')}"
