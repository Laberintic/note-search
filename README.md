**DISCLAIMER: this build currently uses google's gemini API to get LLM responses. Take into account Googles ToS and Privacy Policy.**
**If outside the UE... Google WILL use your messages for training.**

# Obsidian LLM Assistant (WIP)

A simple way to use Large Language Models (LLMs) to search through an [Obsidian](https://obsidian.md) vault and get personalized, context-aware responses.

---

## Overview

This project aims to make it easier to query your personal knowledge base using a conversational AI.  
It acts as a local assistant that searches through your Obsidian notes and provides responses based on your own content rather than external data.

Currently, it is a **Python-based PoC** that:

- Uses the **Google Gemini API** to generate targeted search terms given questions.
- Searches through an Obsidian vault for relevant notes.
- Returns matched results ranked by frequency of keyword appearances.

---

Your `.env` file should contain:

```
OBSIDIAN_PATH=/path/to/your/vault
GOOGLE_API_KEY=your_google_api_key_here
```

---

## Roadmap

### Phase 1 — Core Search Assistant

* [x] Generate search queries using Gemini.
* [x] Scan Obsidian notes for term frequency.
* [x] Summarize and answer based on note content.

### Phase 2 — Source-Aware Responses

* [ ] Display which notes were referenced in each answer.
* [ ] Optionally link directly to notes in the vault.

### Phase 3 — Local UI

* [ ] Add a simple local web interface or desktop window.
* [ ] Allow asking questions and viewing note references interactively.
* [ ] Explore Obsidian API or plugin integration for seamless use.

---

## Motivation

This is a personal hobby project.
I use Obsidian on a day to day basis to take my university notes. My main goal is to make 
browsing my notes much easyer and to learn how to use APIs in the process.

---

## Tech Stack

* **Python 3.10+**
* **Google Gemini API** (`google-genai`)
* **Streamlit UI** (`streamlit`)

---

## Getting Started

1. **Clone this repository**

   ```bash
   git clone https://github.com/Laberintic/note-search.git
   cd note-search
   ```

2. **Install dependencies**

   ```bash
   uv install
   ```

3. **Create a `.env` file**

   ```bash
   OBSIDIAN_PATH=/path/to/your/vault
   GOOGLE_API_KEY=your_api_key_here
   ```

4. **Run the script**

   ```bash
   python main.py
   // or use uv run main.py
   ```

---

## Future Ideas

* Support for local LLMs using Ollama or other remote APIs.
* Context-based summarization of note content
* Markdown or HTML report generation
* Optional local web-based interface
* Plugin integration with Obsidian

---

## License

This project is licensed under the **MIT License**.
You are free to use, modify, and distribute it for personal or educational purposes.

---

Built with love ❤

---




