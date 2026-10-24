"""Tiny MCP stdio client: starts the server defined in .mcp.json and calls its tools.

Used by mcp_verify.py to drive the Playwright MCP server (same server a Claude
client would start from .mcp.json), because this session has no native MCP loader.
"""
import json
import subprocess
import sys


class McpClient:
    def __init__(self, name="playwright", config=".mcp.json"):
        spec = json.load(open(config, encoding="utf-8"))["mcpServers"][name]
        cmd = [spec["command"], *spec.get("args", [])]
        # npx is a .cmd file on Windows
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
                                     shell=(sys.platform == "win32"))
        self._id = 0
        self.request("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                    "clientInfo": {"name": "books-scraper-verify", "version": "1.0"}})
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _send(self, msg):
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()

    def request(self, method, params=None):
        self._id += 1
        self._send({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}})
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("MCP server closed the connection")
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if msg.get("id") == self._id:
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                return msg["result"]

    def list_tools(self):
        return [t["name"] for t in self.request("tools/list")["tools"]]

    def call(self, tool, **args):
        result = self.request("tools/call", {"name": tool, "arguments": args})
        return "\n".join(c.get("text", "") for c in result.get("content", []))

    def close(self):
        self.proc.terminate()
