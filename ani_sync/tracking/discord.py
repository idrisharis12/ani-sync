# -*- coding: utf-8 -*-
"""Cross-platform zero-dependency Discord Rich Presence client for Linux, macOS & Windows."""

import json
import os
import struct
import sys
import threading
import time

from ani_sync.config import load_config, log_debug


class DiscordRPC:
    """Zero-dependency Discord Rich Presence client via local IPC socket & Windows Named Pipes."""

    _sock = None
    _thread = None
    _active = False

    @classmethod
    def start_activity(cls, title, ep_num):
        """Start persistent Discord Rich Presence activity."""
        cls.stop_activity()
        cls._active = True

        def _run():
            try:
                import socket

                load_config()
                client_id = os.getenv(
                    "DISCORD_CLIENT_ID", "1543718626400403466"
                ).strip()
                if not client_id:
                    return

                sock = None
                is_win_pipe = False

                if sys.platform == "win32":
                    # P0 Fix: Open Windows Named Pipe for Discord IPC
                    for i in range(10):
                        pipe_name = rf"\\.\pipe\discord-ipc-{i}"
                        if os.path.exists(pipe_name):
                            try:
                                sock = open(pipe_name, "r+b", buffering=0)
                                is_win_pipe = True
                                log_debug(
                                    f"Connected to Windows Discord Named Pipe: {pipe_name}"
                                )
                                break
                            except Exception as pe:
                                log_debug(f"Failed to open pipe {pipe_name}: {pe}")
                else:
                    uid = os.getuid()
                    candidates = [
                        f"/run/user/{uid}/discord-ipc-0",
                        f"/run/user/{uid}/app/com.discordapp.Discord/discord-ipc-0",
                        os.path.join(
                            os.environ.get("XDG_RUNTIME_DIR", ""), "discord-ipc-0"
                        ),
                        "/tmp/discord-ipc-0",
                    ]
                    for c in candidates:
                        if os.path.exists(c):
                            try:
                                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                                sock.connect(c)
                                log_debug(f"Connected to Unix Discord socket: {c}")
                                break
                            except Exception as se:
                                log_debug(f"Failed to connect socket {c}: {se}")

                if not sock:
                    log_debug("No active Discord IPC socket found.")
                    return

                cls._sock = sock

                def _send(op, data_dict):
                    payload = json.dumps(data_dict).encode("utf-8")
                    hdr = struct.pack("<II", op, len(payload))
                    if is_win_pipe:
                        sock.write(hdr + payload)
                        sock.flush()
                    else:
                        sock.sendall(hdr + payload)

                def _recv():
                    if is_win_pipe:
                        hdr = sock.read(8)
                        if len(hdr) < 8:
                            return None
                        _, length = struct.unpack("<II", hdr)
                        return sock.read(length)
                    else:
                        return sock.recv(1024)

                # Send Handshake opcode 0
                _send(0, {"v": 1, "client_id": client_id})
                _recv()

                # Send Set Activity opcode 1
                activity = {
                    "cmd": "SET_ACTIVITY",
                    "args": {
                        "pid": os.getpid(),
                        "activity": {
                            "details": f"Watching {title[:120]}",
                            "state": f"Episode {ep_num} • 64x Turbo Speed",
                            "timestamps": {"start": int(time.time())},
                            "assets": {
                                "large_image": "ani_sync_logo",
                                "large_text": "ani-sync: Zero-Buffering Terminal Player",
                            },
                            "buttons": [
                                {
                                    "label": "⚡ Get ani-sync CLI",
                                    "url": "https://github.com/idrisharis12/ani-sync",
                                },
                                {
                                    "label": "⭐ Star on GitHub",
                                    "url": "https://github.com/idrisharis12/ani-sync",
                                },
                            ],
                        },
                    },
                    "nonce": str(time.time()),
                }
                _send(1, activity)

                # Keep socket alive while active
                while cls._active:
                    time.sleep(1)
            except Exception as e:
                log_debug(f"Discord RPC exception: {e}")
            finally:
                if cls._sock:
                    try:
                        cls._sock.close()
                    except Exception:
                        pass
                    cls._sock = None

        cls._thread = threading.Thread(target=_run, daemon=True)
        cls._thread.start()

    @classmethod
    def stop_activity(cls):
        """Close Discord Rich Presence activity cleanly."""
        cls._active = False
        if cls._sock:
            try:
                cls._sock.close()
            except Exception:
                pass
            cls._sock = None
