#!/usr/bin/env python3
"""Read the 4 KB RAM console ring buffer over SWD (no USB-TTL needed).

Example (addresses from `arm-none-eabi-nm`):

    python tools/read_ramlog.py \
        --stflash "C:/stlink/bin/st-flash.exe" \
        --buf 0x200017a0 --head 0x200027a0 --size 4096
"""
import argparse
import os
import struct
import subprocess
import tempfile


def read_mem(stflash, addr, size, path):
    subprocess.run(
        [stflash, "read", path, hex(addr), str(size)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    with open(path, "rb") as handle:
        return handle.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stflash", default="st-flash")
    parser.add_argument("--buf", type=lambda x: int(x, 0), default=0x200017A0)
    parser.add_argument("--head", type=lambda x: int(x, 0), default=0x200027A0)
    parser.add_argument("--size", type=int, default=4096)
    args = parser.parse_args()

    tmp = tempfile.gettempdir()
    data = read_mem(args.stflash, args.buf, args.size, os.path.join(tmp, "omx_log.bin"))
    head_raw = read_mem(args.stflash, args.head, 4, os.path.join(tmp, "omx_head.bin"))
    head = struct.unpack("<I", head_raw)[0]
    ordered = data[head:] + data[:head] if head else data
    text = ordered.decode("utf-8", errors="replace").strip("\x00")
    print(text)


if __name__ == "__main__":
    main()
