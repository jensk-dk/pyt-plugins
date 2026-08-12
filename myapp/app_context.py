from typing import Any


class DefaultAppContext:
    async def log(self, level: str, message: str) -> None:
        print(f"[{level.upper()}] {message}")

    async def emit_event(self, name: str, data: Any) -> None:
        print(f"[EVENT] {name}: {data!r}")
