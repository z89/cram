from dotenv import load_dotenv
import os

load_dotenv()


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(f"Missing required env var: {key}")
    return val


CANVAS_API_URL = _require("CANVAS_API_URL")
CANVAS_ACCESS_TOKEN = _require("CANVAS_ACCESS_TOKEN")

NOTION_TOKEN = _require("NOTION_TOKEN")
NOTION_UNIVERSITY_PAGE_ID = _require("NOTION_UNIVERSITY_PAGE_ID")
NOTION_DEBUG_PAGE_ID = os.getenv("NOTION_DEBUG_PAGE_ID", "")
