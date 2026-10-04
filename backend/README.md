# AgentFlow Backend — Complete Automation Build

This backend keeps the existing `POST /api/chat` contract and adds a state-aware automation layer.

## Main capabilities

- Natural-language planning through Gemini
- Conversation context and follow-up questions
- Windows application detection and reuse
- Microsoft Word automation through Office COM
- Microsoft Excel automation through Office COM
- Microsoft PowerPoint automation through Office COM
- Chrome launch/reuse/search/navigation
- File and folder operations
- Keyboard and mouse automation
- System/application observation
- Action verification
- One bounded recovery/re-plan pass after a failed action
- Confirmation for dangerous operations such as email/reminders/deletion if enabled

## Important

This is a **Windows backend**. Microsoft Office automation requires desktop Microsoft Office and `pywin32`.

Do not copy `.env` from the old backend into this distribution. Keep your existing `GEMINI_API_KEY` in the local backend `.env` file.

## Install/update

```powershell
cd C:\Users\BABOU.V\Desktop\AgentFlow\backend
venv\Scripts\activate
pip install -r requirements.txt
python -m pywin32_postinstall -install
uvicorn main:app --reload
```

If `python -m pywin32_postinstall -install` is not available, skip it; `pywin32` can still work in many environments.

## Health check

Open `http://127.0.0.1:8000/api/health` and expect:

```json
{"status":"ok"}
```

## Recommended test sequence

1. `Open Calculator and add 25 and 37.`
2. `Open Word and create a blank document.`
3. `Write a short paragraph about AI in healthcare.`
4. `Save it as AI_Healthcare.docx on my Desktop.`
5. `Open Excel and create a table with names Alice, Bob, Charlie and marks 80, 90, 70. Calculate the average.`
6. `Search Chrome for AI healthcare applications.`
7. Cross-app: `Create an Excel marks sheet, calculate the average, then create a Word summary and save both in a Student Reports folder.`

## Notes

Office actions use COM rather than screen coordinates wherever possible. This makes Word/Excel workflows substantially more dynamic: existing applications/documents can be reused, new documents/workbooks can be created, and files can be saved directly.

Chrome still relies on the local Chrome installation/profile and visible browser window. It avoids the previous hard-coded `chrome.exe --guest` launch and attempts to reuse a running browser or select an existing local Chrome profile.
