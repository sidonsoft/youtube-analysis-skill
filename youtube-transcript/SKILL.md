---
name: youtube-transcript
description: "Extract transcripts from YouTube videos. Use when you need to analyze, summarize, or quote YouTube video content. Triggers on: extract transcript, get YouTube transcript, YouTube video text, transcribe YouTube, video transcript, or any request involving getting text content from a YouTube URL. Supports English and other languages via --lang flag."
---

# YouTube Transcript Skill

Extract clean text transcripts from YouTube videos using `yt-dlp`.

## Quick Usage

```bash
python3 scripts/extract_transcript.py <youtube_url>
```

## Options

- `--lang <code>` — Language code (default: `en`). Use `en,es` for multiple, or `a.en` for auto-generated English.
- `--json` — Output structured JSON instead of plain text.

## Script Output

**Success:** Returns plain text transcript (timestamps stripped) or JSON with `success`, `text`, `video_id`, `title`.

**Failure:** Returns error message explaining why (no captions, age-restricted, etc.).

## Example

```bash
python3 scripts/extract_transcript.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Edge Cases

- **Age-restricted videos**: Returns error — cannot extract
- **No captions**: Returns error with suggestion to try `--lang a.en` for auto-generated
- **Playlist URLs**: Extracts from first video only (or use `--flat-playlist` for all)
- **Live videos**: Not supported — no captions available

## Dependencies

Requires `yt-dlp` installed:

```bash
pip install yt-dlp
# or
sudo apt install yt-dlp
```

## When This Skill Doesn't Work

Try alternative approaches:
1. Use `web_fetch` on `youtubesubtitles.com` with the video URL
2. Check if the video has a community transcript (not accessible via this script)
3. For very short clips, consider downloading and using a local transcription service
