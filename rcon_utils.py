"""Raw socket RCON — no signals, safe in any thread/async context."""
import socket, struct


def rcon_command(host: str, port: int, password: str, command: str, timeout: float = 5.0) -> str:
    def _pack(req_id: int, req_type: int, payload: str) -> bytes:
        data = payload.encode("utf-8") + b"\x00\x00"
        length = 4 + 4 + len(data)
        return struct.pack("<ii", length, req_id) + struct.pack("<i", req_type) + data

    def _recv(sock: socket.socket) -> tuple[int, int, str]:
        raw_len = b""
        while len(raw_len) < 4:
            chunk = sock.recv(4 - len(raw_len))
            if not chunk:
                raise ConnectionError("Connection closed")
            raw_len += chunk
        length = struct.unpack("<i", raw_len)[0]
        raw = b""
        while len(raw) < length:
            chunk = sock.recv(length - len(raw))
            if not chunk:
                raise ConnectionError("Connection closed")
            raw += chunk
        req_id, req_type = struct.unpack("<ii", raw[:8])
        payload = raw[8:-2].decode("utf-8", errors="replace")
        return req_id, req_type, payload

    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(_pack(1, 3, password))
        rid, _, _ = _recv(sock)
        if rid == -1:
            raise ValueError("RCON auth failed — wrong password")
        sock.sendall(_pack(2, 2, command))
        _, _, response = _recv(sock)
    return response
