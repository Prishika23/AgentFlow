class StateManager:
    def __init__(self):
        self.sessions = {}

    def get(self, session_id):
        return self.sessions.setdefault(
            session_id,
            {
                "messages": [],
                "pending": None,
                "variables": {},
                "last_plan": None,
                "last_actions": [],
                "last_steps": [],
                "facts": {},
                "task": None,
                "last_observation": None,
            },
        )

    def add_message(self, session_id, role, content):
        self.get(session_id)["messages"].append({"role": role, "content": content})

    def set_pending(self, session_id, variable, question):
        self.get(session_id)["pending"] = {"variable": variable, "question": question}

    def clear_pending(self, session_id):
        self.get(session_id)["pending"] = None

    def set_task(self, session_id, task):
        self.get(session_id)["task"] = task

    def clear_task(self, session_id):
        self.get(session_id)["task"] = None

    def set_observation(self, session_id, observation):
        self.get(session_id)["last_observation"] = observation

    def remember_execution(self, session_id, actions, steps):
        state = self.get(session_id)
        state["last_actions"] = actions
        state["last_steps"] = steps
        for step in steps:
            if step.get("status") != "success":
                continue
            action = step.get("action", {})
            args = action.get("args", {})
            action_type = action.get("type")
            if action_type == "OPEN_APPLICATION":
                state["facts"]["last_application"] = args.get("application")
            elif action_type in {"OPEN_URL", "BROWSER_OPEN_URL"}:
                state["facts"]["last_url"] = args.get("url")
            elif action_type in {"SEARCH_WEB", "BROWSER_SEARCH"}:
                state["facts"]["last_search"] = args.get("query")
            elif action_type in {"CREATE_FILE", "WORD_SAVE", "EXCEL_SAVE", "POWERPOINT_SAVE"}:
                path = args.get("path") or args.get("filename")
                if path:
                    state["facts"]["last_file_path"] = path
                    state["facts"]["last_filename"] = str(path).replace("/", "\\").split("\\")[-1]
            elif action_type in {"RENAME_FILE", "MOVE_FILE"}:
                destination = args.get("destination")
                if destination:
                    state["facts"]["last_file_path"] = destination
                    state["facts"]["last_filename"] = str(destination).replace("/", "\\").split("\\")[-1]
            elif action_type == "SEND_EMAIL":
                state["facts"]["last_email"] = {k: args.get(k) for k in ("to", "subject", "body")}
            elif action_type == "SET_REMINDER":
                state["facts"]["last_reminder"] = {"title": args.get("title"), "datetime": args.get("datetime")}
