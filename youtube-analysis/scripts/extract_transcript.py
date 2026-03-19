#!/usr/bin/env python3
"""
Extract transcript from a YouTube video using yt-dlp.
Always returns JSON to stdout. Exit code 0 on success, non-zero on failure.

Usage: python3 extract_transcript.py <youtube_url> [--lang en] [--json]
  --json   Explicit JSON output (default). Included for docs consistency.
"""

import sys
import json
import argparse
import subprocess
import os
import re
import tempfile


def extract_transcript(url, lang="en"):
    """
    Extract transcript from a YouTube video using yt-dlp.

    Returns:
        dict with: success (bool), text (str), video_id (str),
                   title (str or None), error (str or None)
    """
    # Get video metadata first (id, title) so we can return title reliably
    video_id = None
    video_title = None

    info_cmd = [
        "yt-dlp", "--skip-download",
        "--print=%(id)s|%(title)s",
        url
    ]

    try:
        info_result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=30)
        if info_result.returncode == 0 and info_result.stdout.strip():
            parts = info_result.stdout.strip().split("|", 1)
            video_id = parts[0]
            video_title = parts[1] if len(parts) > 1 else None
    except Exception:
        # Non-fatal: still try to extract transcript
        pass

    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = os.path.join(tmpdir, "%(id)s.%(ext)s")

        cmd = [
            "yt-dlp",
            "--write-auto-subs",
            "--write-subs",
            f"--sub-lang={lang}",
            "--skip-download",
            f"--output={output_template}",
            url
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            return {
                "success": False, "error": "Timeout extracting transcript",
                "video_id": video_id, "title": video_title, "url": url
            }
        except Exception as e:
            return {
                "success": False, "error": str(e),
                "video_id": video_id, "title": video_title, "url": url
            }

        # Find subtitle files
        subtitle_files = []
        try:
            for f in os.listdir(tmpdir):
                if f.endswith((".vtt", ".srt", ".ass", ".lrc")):
                    subtitle_files.append(os.path.join(tmpdir, f))
        except Exception:
            pass

        if not subtitle_files:
            stderr_lower = result.stderr.lower() if result.stderr else ""
            if any(k in stderr_lower for k in ["age", "login", "requires authentication", "restricted"]):
                return {
                    "success": False,
                    "error": "Video is age-restricted or requires login",
                    "video_id": video_id, "title": video_title, "url": url
                }
            if "video" in stderr_lower and ("not found" in stderr_lower or "unavailable" in stderr_lower):
                return {
                    "success": False,
                    "error": "Video not found or unavailable",
                    "video_id": video_id, "title": video_title, "url": url
                }
            return {
                "success": False,
                "error": f"No subtitles found. yt-dlp exit code: {result.returncode}",
                "video_id": video_id, "title": video_title, "url": url
            }

        subtitle_file = subtitle_files[0]
        ext = os.path.splitext(subtitle_file)[1]

        with open(subtitle_file, "r", encoding="utf-8") as f:
            raw = f.read()

        text = parse_subs(raw, ext)

        return {
            "success": True,
            "text": text,
            "video_id": video_id,
            "title": video_title,
            "subtitle_format": ext.lstrip("."),
            "lang": lang,
            "url": url
        }


def parse_subs(content, ext):
    """Parse VTT/SRT/ASS content to plain text."""
    lines = content.split("\n")
    text_lines = []
    buffer = []

    for line in lines:
        line = line.strip()
        if not line:
            if buffer:
                text_lines.append(" ".join(buffer))
                buffer = []
            continue
        if "-->" in line:
            continue
        if line.isdigit():
            continue
        if ext == ".ass":
            if line.startswith("Dialogue:"):
                parts = line.split(",", 9)
                if len(parts) > 9:
                    buffer.append(parts[9].strip())
            continue
        if line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE", "<")):
            continue
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"^[-\s]+", "", line)
        if line:
            buffer.append(line)

    if buffer:
        text_lines.append(" ".join(buffer))

    return " ".join(text_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract transcript from YouTube video")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--lang", default="en", help="Language code (default: en)")
    parser.add_argument(
        "--json", action="store_true", default=True,
        help="Output JSON (default; included for docs consistency)"
    )

    args = parser.parse_args()
    result = extract_transcript(args.url, args.lang)
    print(json.dumps(result, indent=2))
