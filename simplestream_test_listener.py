#!/usr/bin/env python3
import socket
import struct
import json
from datetime import datetime

UDP_IP = "0.0.0.0"   # listen on all interfaces
UDP_PORT = 9123      # must match your simplestream port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening on {UDP_IP}:{UDP_PORT} for simplestream packets...")

while True:
    data, addr = sock.recvfrom(65535)
    if len(data) < 4:
        print("Packet too short from", addr)
        continue

    (hdr_len,) = struct.unpack("<I", data[:4])   # little-endian uint32

    if hdr_len > len(data) - 4:
        print(f"Bad header length {hdr_len} > {len(data)-4} from {addr}")
        continue

    hdr_bytes = data[4:4 + hdr_len]
    audio_bytes = data[4 + hdr_len:]

    try:
        meta = json.loads(hdr_bytes.decode("utf-8"))
    except Exception as e:
        print("Failed to parse JSON header:", e)
        continue

    ts = datetime.now().strftime("%H:%M:%S")
    event = meta.get("event", "audio")

    if event in ("call_start", "call_end"):
        print(f"[{ts}] {event} tg={meta.get('talkgroup')} "
              f"tag={meta.get('talkgroup_tag')} "
              f"src={meta.get('src')} freq={meta.get('freq')} "
              f"short={meta.get('short_name')}")
    else:
        samples = len(audio_bytes) // 2  # 16-bit samples
        print(f"[{ts}] audio tg={meta.get('talkgroup')} "
              f"src={meta.get('src')} "
              f"rate={meta.get('audio_sample_rate')} "
              f"samples={samples}")
        # Uncomment for full JSON dump:
        # print(json.dumps(meta, indent=2))
