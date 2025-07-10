# sidekick_tools.py  (Playwright-free)

from dotenv import load_dotenv
import os, requests
from langchain.agents import Tool
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_experimental.tools import PythonREPLTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper

load_dotenv(override=True)

# --- Push notification -----------------------------------------
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_user  = os.getenv("PUSHOVER_USER")
pushover_url   = "https://api.pushover.net/1/messages.json"

def push(text: str):
    """Send a Pushover notification."""
    requests.post(
        pushover_url,
        data={"token": pushover_token, "user": pushover_user, "message": text}
    )
    return "success"

push_tool = Tool(
    name="send_push_notification",
    func=push,
    description="Send a push notification to the user"
)

# --- Safe Python REPL ------------------------------------------
class SafePythonREPLTool(PythonREPLTool):
    def run(self, code: str):
        banned = ["import os", "import sys", "open(", "eval(", "exec(", "__import__"]
        if any(b in code for b in banned):
            return "⚠️ Unsafe code blocked."
        return super().run(code)

# --- Other tools ------------------------------------------------
file_tools = FileManagementToolkit(root_dir="sandbox").get_tools()
search_tool = Tool(
    name="search",
    func=GoogleSerperAPIWrapper().run,
    description="Run a Google search and return results"
)
wiki_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
python_repl = SafePythonREPLTool()

def other_tools():
    """Return the final tool list (no browser)."""
    return file_tools + [push_tool, search_tool, wiki_tool, python_repl]
