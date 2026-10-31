"""Optional hosted videos for lightweight package installs; never proxy local data."""
import json
import re
from pathlib import Path

HOSTED_MEDIA = "https://chatify-demo-779c.onrender.com/chatify/media/"

def hosted_video(name, web):
    """Return a fixed public destination only for a known missing optional video."""
    if not name.startswith("media/") or not name.endswith(".mp4"):
        return None
    relative = name.removeprefix("media/")
    allowed = {"paperworks-walkthrough.mp4", "signal-desk-walkthrough.mp4", "bunny-meadow.mp4", "bunny-morning.mp4"}
    try:
        stories = json.loads((Path(web) / "media/stories/manifest.json").read_text())["stories"]
        for story in stories:
            sid = story.get("id", "")
            if re.fullmatch(r"[a-z0-9-]+", sid) and story.get("src") == sid + ".mp4":
                allowed.add("stories/" + story["src"])
    except (OSError, ValueError, KeyError, TypeError):
        pass
    if relative not in allowed or (Path(web) / name).is_file():
        return None
    return HOSTED_MEDIA + relative
