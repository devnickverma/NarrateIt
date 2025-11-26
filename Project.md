# Project Requirement Document (PRD)

**Project Name:** MangaNarrator MVP
**Version:** 1.0
**Status:** Draft
**Cost Strategy:** High-Performance Free Tier (Gemini Flash + Deepgram Credits)

-----

## 1\. Executive Summary

**Goal:** Build a Python tool that automatically converts a Manga PDF into a "Read-Along" video.
**Core Experience:** Instead of a robotic reading, the AI acts as an **entertaining narrator** who describes the scene, reads dialogue with personality, and cracks jokes about the art style or characters, mimicking a YouTuber's "Let's Read" style.

-----

## 2\. Technology Stack & Cost Breakdown

| Component | Technology | Model / Library | Cost Status |
| :--- | :--- | :--- | :--- |
| **Language** | Python 3.10+ | Standard Libs | Free |
| **PDF Processing**| `pdf2image` | Poppler backend | Open Source |
| **Vision & Script**| **Google Gemini API** | `gemini-1.5-flash` | **Free Tier** (15 RPM) |
| **Voice (TTS)** | **Deepgram API** | `aura-asteria-en` | **Free $200 Credit** (Sign-up) |
| **Fallback Voice**| `edge-tts` | Microsoft Edge Online | Free (Unlimited fallback) |
| **Video Engine** | **FFmpeg** | CLI Tool | Open Source |

> **Note on Deepgram:** New accounts get \~$200 in credits. If you run out, switch the code to `edge-tts` (completely free forever) with minimal quality loss.

-----

## 3\. System Architecture

The data flows strictly in one direction:
`PDF File` $\rightarrow$ `Images` $\rightarrow$ `Witty Script (Text)` $\rightarrow$ `Audio File` $\rightarrow$ `Video Segment` $\rightarrow$ `Final MP4`

-----

## 4\. Functional Requirements

### Phase 1: Image Extraction

  * **Library:** `pdf2image`
  * **Action:** Convert PDF pages to high-resolution PNGs (e.g., 300 DPI).
  * **Output:** Save locally as `page_001.png`, `page_002.png`, etc.
  * **Constraint:** Ensure numerical sorting is correct so page 10 comes after page 9, not page 1.

### Phase 2: The "Witty Narrator" Script (Gemini)

  * **Model:** `gemini-1.5-flash`
  * **Prompt Strategy:** The prompt must prevent "robotic OCR" and enforce "Creative Narration."
  * **System Prompt:**
    > "You are an energetic, witty manga narrator making a video for fans. Look at this manga page. Read the panels in the correct Japanese order (Right-to-Left).
    > **Your Task:**
    > 1.  **Narrate the visual action** briefly between dialogue (e.g., *'Naruto glares at Sasuke, looking like he's about to explode.'*).
    > 2.  **Read the dialogue** with character labels (e.g., *'Sasuke says: ...'*).
    > 3.  **Add Humor:** Crack **one** short joke or sarcastic comment about the facial expressions or the situation.
    > 4.  **Format:** Output *only* the text to be spoken. No markdown, no scene headers."

### Phase 3: Voice Synthesis (Deepgram)

  * **API:** Deepgram Text-to-Speech
  * **Voice Model:** `aura-asteria-en` (Female, energetic) or `aura-orion-en` (Male, narrative).
  * **Logic:**
    1.  Send Gemini's text script to Deepgram.
    2.  Receive audio stream.
    3.  Save as `audio_001.mp3`.
    4.  **Critical:** Measure the duration of this audio file (in seconds) precisely.

### Phase 4: Dynamic Video Stitching (FFmpeg)

  * **Logic:** We cannot use a fixed framerate because every page takes a different amount of time to read.
  * **Approach:** "Slide Show" method.
      * For `page_001.png`, display it for `duration_of_audio_001`.
      * For `page_002.png`, display it for `duration_of_audio_002`.
  * **Command Structure (Complex Filter):**
    Use a "demuxer" text file for FFmpeg to stitch them easily without complex re-encoding.
      * *file list.txt:*
        ```text
        file 'page_001.png'
        duration 12.50
        file 'page_002.png'
        duration 8.20
        ...
        ```

-----

## 5\. Implementation Roadmap (Step-by-Step)

### Step 1: Python Environment Setup

Install necessary libraries:

```bash
pip install google-generativeai deepgram-sdk pdf2image pydub
# Requires FFmpeg and Poppler installed on your system OS
```

### Step 2: The "Phase 1" Script (Get Images)

I will provide this script first. It will take your PDF and verify `pdf2image` is working.

### Step 3: The "Phase 2 & 3" Script (Get AI to Talk)

We will write a loop that sends one image to Gemini, prints the text (so you can read the joke), generates the audio, and saves it.

### Step 4: The "Phase 4" Script (Make Video)

We will write the FFmpeg wrapper to combine the assets.

-----

## 6\. Risks & Mitigations

  * **Risk:** Gemini refuses to read "Copyrighted" characters.
      * *Mitigation:* Use a generic system prompt ("Describe this comic page") rather than naming specific copyrighted series in the prompt instructions.
  * **Risk:** Text is read in Western order (Left-to-Right).
      * *Mitigation:* Explicitly enforce "Right-to-Left reading order" in the system instructions.