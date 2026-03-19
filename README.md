# YouTube Skills for OpenClaw

Two OpenClaw skills for working with YouTube video content.

## Skills

### youtube-transcript
Lean transcript extraction. Returns raw text only — no summary, no analysis.

**Use when:** you just want the transcript text.

### youtube-analysis
Transcript-first video analysis. Extracts the transcript, then uses the main model to produce a structured summary, identify claims, assess credibility, and connect to related topics.

**Use when:** you want a summary, fact-check, credibility assessment, or deeper analysis of a video.

## Installation

Download the `.skill` file for the skill you want and place it in OpenClaw's skills directory. Alternatively, copy the skill folder directly.

## Requirements

Both skills require `yt-dlp` installed:

```bash
pip install yt-dlp
# or
sudo apt install yt-dlp
```

## Usage

**youtube-transcript:**
```bash
python3 youtube-transcript/scripts/extract_transcript.py <youtube_url>
```

**youtube-analysis:**
```bash
python3 youtube-analysis/scripts/extract_transcript.py <youtube_url> --lang en
# then use the transcript output in the main chat model for analysis
```

Both scripts are self-contained and require no API keys.

## Quick comparison

| | youtube-transcript | youtube-analysis |
|---|---|---|
| Returns raw transcript | ✅ | ✅ |
| Summary | — | ✅ |
| Claims analysis | — | ✅ |
| Credibility check | — | ✅ |
| Confidence language | — | ✅ |

## Portability

The scripts resolve their own paths relative to the skill directory. No hardcoded install paths. Works in any environment where `yt-dlp` is available.
