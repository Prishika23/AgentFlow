import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

from .prompts import SYSTEM_PROMPT
from state.manager import StateManager
from security.validator import validate
from automation.executor import execute_action
from automation.verifier import verify_action

load_dotenv()


class Orchestrator:
    def __init__(self):
        key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=key) if key else None
        self.state = StateManager()
        self.models = [
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3-flash-preview",
            "gemini-2.5-flash",
        ]

    def _fallback(self):
        return {
            "status": "chat",
            "message": "Gemini API is not configured. Please add GEMINI_API_KEY to backend/.env.",
            "actions": [],
        }

    def _generate(self, model, prompt):
        return self.client.models.generate_content(
            model=model,
            contents=json.dumps(prompt, ensure_ascii=False),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
            ),
        )

    def _normalize_plan(self, raw):
        """Make Gemini output safe before anything calls .get() on it."""
        if not isinstance(raw, dict):
            return {
                "status": "chat",
                "message": "I received an invalid plan from the AI planner. Please try again.",
                "actions": [],
            }

        status = raw.get("status")
        if status not in {"ready", "needs_input", "chat"}:
            status = "ready" if isinstance(raw.get("actions"), list) else "chat"

        raw_actions = raw.get("actions")
        if raw_actions is None:
            raw_actions = []
        if not isinstance(raw_actions, list):
            raw_actions = []

        actions = []
        for item in raw_actions:
            if not isinstance(item, dict):
                print(f"[AgentFlow] Ignoring malformed action: {item!r}")
                continue
            action_type = item.get("type")
            if not isinstance(action_type, str) or not action_type.strip():
                print(f"[AgentFlow] Ignoring action without a valid type: {item!r}")
                continue
            args = item.get("args")
            if not isinstance(args, dict):
                args = {}
            actions.append({"type": action_type.strip(), "args": args})

        return {
            "status": status,
            "message": raw.get("message") or "",
            "question": raw.get("question"),
            "variable": raw.get("variable"),
            "actions": actions,
        }

    def _plan(self, session_id, user_message, extra=None):
        if not self.client:
            return self._fallback()

        state = self.state.get(session_id)
        prompt = {
            "conversation": state["messages"][-20:],
            "new_user_message": user_message,
            "pending": state.get("pending"),
            "variables": state.get("variables", {}),
            "facts": state.get("facts", {}),
            "last_actions": state.get("last_actions", []),
            "last_steps": state.get("last_steps", []),
            "current_task": state.get("task"),
            "last_observation": state.get("last_observation"),
        }
        if extra:
            prompt["additional_context"] = extra

        last_error = None
        for model in self.models:
            try:
                print(f"[AgentFlow] Trying model: {model}")
                response = self._generate(model, prompt)
                raw_text = (getattr(response, "text", "") or "").strip()
                print(f"[AgentFlow] Model succeeded: {model}")
                print(f"[AgentFlow] Planner output: {raw_text[:2000]}")
                return self._normalize_plan(json.loads(raw_text))
            except errors.ServerError as exc:
                last_error = exc
                print(f"[AgentFlow] Model {model} server error: {exc}")
                if getattr(exc, "status_code", None) == 503:
                    time.sleep(1)
                    continue
            except errors.APIError as exc:
                last_error = exc
                print(f"[AgentFlow] API error: {exc}")
                continue
            except json.JSONDecodeError as exc:
                last_error = exc
                print(f"[AgentFlow] Invalid JSON: {exc}")
                continue
            except Exception as exc:
                last_error = exc
                print(f"[AgentFlow] Unexpected planner error: {exc}")
                continue

        return {
            "status": "chat",
            "message": f"Gemini is temporarily unavailable. Please try again. ({last_error})",
            "actions": [],
        }

    def _describe_action(self, action):
        if not isinstance(action, dict):
            return "Invalid action"
        t = action.get("type", "UNKNOWN")
        a = action.get("args") if isinstance(action.get("args"), dict) else {}
        descriptions = {
            "OPEN_APPLICATION": f"Opening {a.get('application', 'application')}",
            "CLOSE_ACTIVE_WINDOW": "Closing the active window",
            "TYPE": "Typing text",
            "KEY_PRESS": f"Pressing {a.get('key', '')}",
            "HOTKEY": "Pressing " + "+".join(a.get("keys", [])),
            "CLICK": "Clicking", "DOUBLE_CLICK": "Double-clicking",
            "WAIT": f"Waiting {a.get('seconds', 1)} seconds",
            "CREATE_FOLDER": f"Creating folder {a.get('path', '')}",
            "CREATE_FILE": f"Creating file {a.get('path', '')}",
            "RENAME_FILE": "Renaming file", "MOVE_FILE": "Moving file",
            "OPEN_URL": f"Opening {a.get('url', '')}",
            "SEARCH_WEB": f"Searching for {a.get('query', '')}",
            "GET_ACTIVE_WINDOW": "Checking active window",
            "OBSERVE_SYSTEM": "Checking system state",
            "OBSERVE_APPLICATION": f"Checking {a.get('application', '')} state",
            "BROWSER_OPEN": "Opening Chrome",
            "BROWSER_OPEN_URL": f"Opening {a.get('url', '')} in Chrome",
            "BROWSER_SEARCH": f"Searching Chrome for {a.get('query', '')}",
            "WORD_STATUS": "Checking Word state", "WORD_NEW_DOCUMENT": "Creating a blank Word document",
            "WORD_OPEN": f"Opening Word document {a.get('path', '')}", "WORD_TYPE": "Writing in Word",
            "WORD_ADD_HEADING": "Adding a Word heading", "WORD_SAVE": "Saving the Word document",
            "WORD_SAVE_AS": f"Saving Word document as {a.get('path', '')}",
            "EXCEL_STATUS": "Checking Excel state", "EXCEL_NEW_WORKBOOK": "Creating a blank Excel workbook",
            "EXCEL_OPEN": f"Opening Excel workbook {a.get('path', '')}",
            "EXCEL_WRITE_CELL": f"Writing to Excel cell {a.get('cell', '')}",
            "EXCEL_WRITE_RANGE": "Entering Excel data", "EXCEL_FORMULA": f"Adding Excel formula to {a.get('cell', '')}",
            "EXCEL_SAVE": "Saving the Excel workbook", "POWERPOINT_STATUS": "Checking PowerPoint state",
            "POWERPOINT_NEW": "Creating a presentation", "POWERPOINT_ADD_SLIDE": f"Adding slide: {a.get('title', '')}",
            "POWERPOINT_SAVE": "Saving the presentation", "SEND_EMAIL": f"Preparing email to {a.get('to', '')}",
            "SET_REMINDER": f"Creating reminder '{a.get('title', '')}'",
        }
        return descriptions.get(t, t)

    def _execute_plan(self, session_id, actions):
        steps = []
        safe_actions = [a for a in actions if isinstance(a, dict)]
        for index, action in enumerate(safe_actions):
            description = self._describe_action(action)
            try:
                print(f"[AgentFlow] ▶ {description}")
                result = execute_action(action)
                verification = verify_action(action, result)
                if not verification.get("verified", True):
                    raise RuntimeError(f"Verification failed: {verification.get('observation')}")
                self.state.set_observation(session_id, verification.get("observation"))
                print(f"[AgentFlow] ✓ {description}")
                steps.append({"action": action, "description": description, "status": "success", "result": result, "verification": verification})
            except Exception as exc:
                print(f"[AgentFlow] ✕ {description}: {exc}")
                steps.append({"action": action, "description": description, "status": "failed", "result": str(exc)})
                return steps, index
        return steps, None

    def _is_confirmation(self, message):
        return message.strip().lower() in {"yes", "y", "confirm", "confirmed", "proceed", "do it", "go ahead", "send it", "okay", "ok"}

    def handle(self, session_id, message):
        state = self.state.get(session_id)
        self.state.add_message(session_id, "user", message)

        if state.get("pending"):
            variable = state["pending"].get("variable")
            if variable:
                state["variables"][variable] = message
            self.state.clear_pending(session_id)

        if isinstance(state.get("task"), dict) and state["task"].get("type") == "confirmation":
            if self._is_confirmation(message):
                actions = state["task"].get("actions", [])
                self.state.clear_task(session_id)
            else:
                self.state.clear_task(session_id)
                reply = "Cancelled the pending action."
                self.state.add_message(session_id, "assistant", reply)
                return {"status": "cancelled", "message": reply, "actions": [], "steps": []}
        else:
            plan = self._plan(session_id, message)
            state["last_plan"] = plan
            if plan.get("status") == "needs_input":
                variable = plan.get("variable") or "user_input"
                question = plan.get("question") or plan.get("message") or "What information do you need?"
                self.state.set_pending(session_id, variable, question)
                self.state.add_message(session_id, "assistant", question)
                return {"status": "needs_input", "message": question, "actions": [], "steps": []}
            if plan.get("status") == "chat":
                reply = plan.get("message") or "I can help with that."
                self.state.add_message(session_id, "assistant", reply)
                return {"status": "chat", "message": reply, "actions": [], "steps": []}
            actions = plan.get("actions", [])

        if not actions:
            reply = "I don't have any actions to perform."
            self.state.add_message(session_id, "assistant", reply)
            return {"status": "chat", "message": reply, "actions": [], "steps": []}

        security = validate(actions)
        if security["requires_confirmation"] and state.get("task") is None:
            state["task"] = {"type": "confirmation", "actions": actions}
            reply = security["reason"]
            self.state.add_message(session_id, "assistant", reply)
            return {"status": "confirmation_required", "message": reply, "actions": actions, "steps": []}

        steps, failed_index = self._execute_plan(session_id, actions)
        self.state.remember_execution(session_id, actions, steps)
        failed = failed_index is not None

        if failed:
            failed_action = actions[failed_index]
            recovery_context = {
                "failed_action": failed_action,
                "failed_step": steps[-1],
                "successful_steps": steps[:-1],
                "instruction": "Create a safe alternative continuation. Do not repeat the exact failed action unless the new plan explicitly changes the approach. Return only JSON in the normal schema.",
            }
            recovery = self._plan(session_id, "Recover from the failed action and continue the user's original task.", recovery_context)
            recovery_actions = recovery.get("actions", []) if recovery.get("status") == "ready" else []
            if recovery_actions:
                sec = validate(recovery_actions)
                if not sec["requires_confirmation"]:
                    extra_steps, extra_failed = self._execute_plan(session_id, recovery_actions)
                    steps.extend(extra_steps)
                    actions.extend(recovery_actions)
                    failed = extra_failed is not None
                    self.state.remember_execution(session_id, actions, steps)

        if failed:
            reply = "I started the task, but an action could not be completed: " + str(steps[-1].get("result", "unknown error"))
            status = "error"
        else:
            reply = "I completed the requested task."
            status = "completed"
        self.state.add_message(session_id, "assistant", reply)
        return {"status": status, "message": reply, "actions": actions, "steps": steps}
