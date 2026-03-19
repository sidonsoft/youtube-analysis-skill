---
name: youtube-analysis
description: "Analyze YouTube videos for full summary, claims, implications, and credibility assessment. Use when a user provides a YouTube URL and wants more than just a transcript — analysis, credibility check, bias detection, or topic connections. Triggers on: analyze YouTube, YouTube summary, YouTube fact-check, credibility check, summarize and analyze, YouTube claims, YouTube bias. Do not use for transcript-only extraction (use youtube-transcript skill instead)."
---

# YouTube Analysis

Goal: extract transcript first, then use the main chat model for interpretation.

## Workflow

### 1. Extract transcript

Try `yt-dlp` directly for transcript extraction:

```bash
yt-dlp --write-auto-subs --write-subs --sub-lang=en --skip-download --output=/tmp/%(id)s.%(ext)s <youtube_url>
```

Or use the bundled script (returns JSON):

```bash
python3 scripts/extract_transcript.py <youtube_url> --lang en --json
```

The script returns JSON with `success`, `text`, `video_id`, `title`, and `error` fields.

### 2. Retry on failure

If extraction fails, try in order:

- `--sub-lang=en,es` — try English then Spanish
- `--sub-lang=a.en` — auto-generated English captions
- `--write-auto-subs` only (no `--write-subs`) — some videos only have auto-captions
- Age-restricted or login-gated videos cannot be extracted; say so and fall back to a direct summarization as last resort (lower confidence)

### 3. Assess transcript quality

Before summarizing, check for weak captions:

- misheard names, places, or products
- broken sentences or repeated fragments
- obvious substitutions
- unreliable dates, figures, or quoted claims
- auto-caption artifacts (e.g. "adapted computer" instead of "Adaptive Computer")

If quality is weak → lower confidence and say so early.

### 4. Analyze in the main chat model

Once you have transcript text, do the real work in chat. Do not delegate analysis to a subprocess summarizer.

**Summary section:**
- concise overview of what the video says
- grounded in transcript when available

**Analysis section:**
- main claims or arguments
- why they matter
- credibility, bias, or missing context
- connections to related topics
- caveats, counterpoints, or open questions

### 5. Confidence rules

Use **stronger confidence** when:
- transcript quality is good
- claims are straightforward and descriptive
- content is not controversial or high-stakes

Use **lower confidence** when:
- captions are noisy
- claims are technical, political, financial, or high-stakes
- transcript extraction failed and you fell back to summarization

Useful phrasing:
- "This appears to rely on auto-generated captions, so some details may be off."
- "The summary is approximate because the transcript quality is weak."
- "This is the speaker's claim, not something independently verified here."

### 6. Handle long transcripts

If the transcript is long (>50KB of text):
- read and process in chunks
- synthesize across chunks
- do not pretend to hold the full transcript perfectly in context

Use the transcript as source material; let the main model do synthesis.

## Fallback when extraction fails entirely

1. Try alternative caption languages
2. Try auto-generated captions only (`--write-auto-subs --skip-download`)
3. If all else fails, tell the user: "Transcript extraction failed — likely age-restricted, region-locked, or has no captions. I can try a direct summarization but confidence will be lower."

## Output format

Two sections unless the user asks for something else:

**Summary:** — what the video is about and what it says
**Analysis:** — claims, implications, credibility, connections

## Operating principle

Transcript first. Analysis second. Confidence language when source quality is weak.
