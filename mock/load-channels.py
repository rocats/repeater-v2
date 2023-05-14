import json
from typing import List
from urllib.request import urlopen


def load_channel(url: str) -> List[dict]:
    data = json.loads(urlopen(url).read().decode("utf-8"))["rows"]
    return [
        dict(zip(["row_id", "name", "uid", "type", "text_convert"], row))
        for row in data
    ]


channel_lib = load_channel(
    "https://repeater-bot-sqlite.vercel.app/remote/channels.json"
)

print(channel_lib)
print([item["uid"] for item in channel_lib])
print(list(filter(lambda x: x["uid"] == "123456", channel_lib)))
