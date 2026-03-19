---
name: youtube-transcript
description: "Extract a raw text transcript from a YouTube video. Use when the user only wants the transcript text itself — no summary, no analysis, no credibility check. Triggers on: get transcript, extract transcript, give me the YouTube transcript, raw transcript, video captions. For summary, analysis, or fact-checking use the youtube-analysis skill instead."
---

# YouTube Transcript

Extract clean text transcripts from YouTube videos using `yt-dlp`.

## Path resolution

The script `scripts/extract_transcript.py` is relative to the skill directory. Resolve it as:

```bash
python3 ~/.npm-global/lib/node_modules/openclaw/skills/youtube-transcript/scripts/extract_transcript.py <url>
```

## Usage

```bash
python3 scripts/extract_transcript.py <youtube_url> [--lang en]
```

- `--lang <code>` — Language code (default: `en`). Use `a.en` for auto-generated English captions.

## Output

Returns plain text transcript (timestamps and captions metadata stripped). Non-zero exit code on failure.

## Edge cases

- **Age-restricted videos:** returns error — cannot extract
- **No captions:** returns error
- **Live videos:** not supported
- **Playlist URLs:** extracts first video only

## Dependencies

Requires `yt-dlp`:

```bash
pip install yt-dlp
# or
sudo apt install yt-dlp
```

## Alternatives if this fails

1. `web_fetch` on `youtubesubtitles.com` with the video URL
2. Download the video and use a local transcription service

## What this skill does not do

This skill only extracts raw transcript text. It does not summarize, analyze, or assess credibility. For those tasks, use the `youtube-analysis` skill.
