#!/usr/bin/env python3
"""
Extract transcript from a YouTube video using yt-dlp.
Usage: python3 extract_transcript.py <youtube_url> [--lang en]
"""

import sys
import json
import argparse
import subprocess
import os
import tempfile


def extract_transcript(url, lang="en", output_format="text"):
    """
    Extract transcript from a YouTube video.

    Args:
        url: YouTube video URL
        lang: Language code for subtitles (default: en)
        output_format: 'text' for plain text, 'json' for structured

    Returns:
        dict with keys: success (bool), text (str), video_id (str), error (str)
    """
    # First, get video info without downloading
    info_cmd = [
        "yt-dlp",
        "--write-auto-subs",
        "--write-subs",
        f"--sub-lang={lang}",
        "--skip-download",
        "--print=%(id)s|%(title)s|%(duration)s",
        "--flat-playlist",
        url
    ]

    try:
        # Get video info first
        info_result = subprocess.run(
            info_cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        video_id = None
        video_title = None
        duration = None

        if info_result.returncode == 0 and info_result.stdout.strip():
            parts = info_result.stdout.strip().split("|")
            if len(parts) >= 3:
                video_id = parts[0]
                video_title = parts[1]
                duration = parts[2]
            elif len(parts) == 1:
                video_id = parts[0]
        else:
            # Fallback: try to extract just the ID from URL
            if "watch" in url:
                for part in url.split("?"):
                    if "v=" in part:
                        video_id = part.split("v=")[-1].split("&")[0]
                        break
            elif "youtu.be" in url:
                video_id = url.split("youtu.be/")[-1].split("?")[0]

        # Now extract transcript using a simpler approach
        # Create temp dir for subtitle files
        with tempfile.TemporaryDirectory() as tmpdir:
            cmd = [
                "yt-dlp",
                "--write-auto-subs",
                "--write-subs",
                f"--sub-lang={lang}",
                "--skip-download",
                f"--output={tmpdir}/%(id)s.%(ext)s",
                url
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            # Look for subtitle files
            subtitle_files = []
            for f in os.listdir(tmpdir):
                if f.endswith((".vtt", ".srt", ".ass")):
                    subtitle_files.append(os.path.join(tmpdir, f))

            if subtitle_files:
                # Read the first subtitle file
                subtitle_file = subtitle_files[0]
                with open(subtitle_file, "r", encoding="utf-8") as f:
                    raw_subs = f.read()

                text = parse_subs_to_text(raw_subs)

                return {
                    "success": True,
                    "text": text,
                    "video_id": video_id,
                    "title": video_title,
                    "duration": duration,
                    "format": subtitle_file.split(".")[-1]
                }
            else:
                # No subtitles found
                error_msg = result.stderr.strip() if result.stderr else "No subtitles available"
                if "login" in error_msg.lower() or "age" in error_msg.lower():
                    return {
                        "success": False,
                        "error": "Video may be age-restricted or require login",
                        "video_id": video_id,
                        "title": video_title
                    }
                return {
                    "success": False,
                    "error": f"No subtitles found. yt-dlp output: {result.stdout[:500]} {result.stderr[:500]}",
                    "video_id": video_id,
                    "title": video_title
                }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout extracting transcript"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_subs_to_text(srt_content):
    """Parse VTT/SRT content to plain text."""
    lines = srt_content.split("\n")
    text_lines = []

    for line in lines:
        line = line.strip()
        # Skip timing lines, sequence numbers, and metadata
        if not line:
            continue
        if "-->" in line:
            continue
        if line.isdigit():
            continue
        if line.startswith(("WEBVTT", "Kind:", "Language:", "<", "NOTE")):
            continue
        # Remove HTML tags if any
        import re
        line = re.sub(r"<[^>]+>", "", line)
        # Skip empty after cleaning
        if line and not line.startswith("-"):
            text_lines.append(line)

    return " ".join(text_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract transcript from YouTube video")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--lang", default="en", help="Language code (default: en)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    result = extract_transcript(args.url, args.lang)

    if args.json:
        print(json.dumps(result, indent=2))
    elif result["success"]:
        print(result["text"])
    else:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
