# HanPinEn

## Introduction
HanPinEn is a minimalist, responsive web application created by my passion to sing along to Chinese songs. Just by inserting a Youtube link, it displays structured lyrics featuring **Hanzi (漢字)**, **Pinyin (拼音)**, and **English translations**.

#### Background
After my internship, I was granted a prestigious scholarship to study Chinese language in Taiwan for 3 months where I became obsessed with listening to Chinese songs. Not only to listen but to sing along to it as well.

Whenever I search for the pinyin or English subtitles of a song I like, I sometimes find a lack of resources that satisfies me (be it a website or a fanmade video). And even if they did exist, there were either too many ads (making the website hard to navigate) or it was missing either the hanzi, pinyin, or english.

So, as a Data Science fresh graduate, I decided to create this LLM-powered website app where as long as a youtube link exists, it can display the hanzi, pinyin, and english lyrics.


## Features
* **Multi-Tier Scraper:** Scrapes transcripts or description in Youtube for lyrics. Else, fallback to fetch from an external music API (NetEase Cloud Music / 網易雲音樂)
* **Intelligent Language Processing:** Integrates OpenAI API to take the raw Chinese text into Pinyin and English.
* **Database Caching:** Stores the submitted songs to eliminate redundant API calls (optimizing OpenAI Token Usage)


#### How AI is Used?
This project uses OpenAI as an intelligent data layer. Instead of writing custom parsers or doing dictionary lookups, I used a LLM pipeline to take in the raw scraped transcripts, cleans them up, generates the Pinyin and English translations, and outputs strict JSON that drops right into the Frontend UI.


## Tech Stacks

### Frontend
* **Framework:** React (Vite)
* **Styling:** Tailwind CSS
* **UI Workbench:** Storybook (WIP)

### Backend
* **Framework:** FastAPI (Python)
* **Database Engine:** SQLModel (Built on SQLAlchemy & Pydantic)
* **Database Storage:** SQLite (Local storage)
* **Server:** Uvicorn

### AI & Data Pipeline
* **LLM Engine:** OpenAI API (Structured Outputs / JSON Mode)
* **Lyric Metadata Scraping:** `youtube-transcript-api`
* **Lyric Fallback Data Source:** NetEase Cloud Music API

### Deployment & DevOps
* **Version Control:** Git & GitHub
* **Frontend Hosting:** Vercel
* **Backend Hosting:** Render

---

## Result
Test it out: https://lyrics-finder-coffeeholixcc.vercel.app/
(But get ready with a Youtube URL to a Chinese song)

<img width="3764" height="1842" alt="image" src="https://github.com/user-attachments/assets/078855b6-fc28-49c3-8b63-a60f5e64652b" />

---

## My Engineering Road Map

<img width="1353" height="784" alt="HanPinEn Architecture Diagram" src="https://github.com/user-attachments/assets/103c8638-7662-4c6b-a710-36037e520ddb" />

### Phase 1: Scraping CC/Description from Youtube Link. Fallback to NetEast.
**Goal:** Create a data retrieval engine that extracts raw Chinese captions or description text from YouTube videos, with an automated fallback to the NetEase Cloud Music API when native subtitles are absent.

**Module Structure:**
* `extractor.py`: Extracts native YouTube CC or description text using video ID parameters.
* `external_search.py`: Handles fallback queries to NetEase Cloud Music API if YouTube extraction yields no usable text.

> **Lesson Learnt — Single Responsibility Principle (SRP):**
> Separate CC/ description extraction and external API fallbacks into isolated modules. Each module has exactly one action/purpose/responsibility, in case if there was any update to Youtube API, it will not break NetEase fallback logic.

### Phase 1.1: OpenAI Integration
**Goal:** Convert scraped raw text into line-by-line Hanzi, Pinyin, and English translations.

**Module Structure:**
* `pipeline.py`: Implements `orchestrate_lyrics_extraction()` to execute processing through the OpenAI API.
* `main.py`: Integrates modules into cohesive FastAPI endpoints.

> **Lesson Learnt: Pydantic Model, Deterministic Responsibility**
> **Goal:** OpenAI outputs a strict Pydantic JSON schema (`{ "hanzi": "...", "pinyin": "...", "english": "..." }`) rather than conversational text, making the AI-processing deterministic.

### Phase 2: Setting Database Cache Layer
**Goal:** Implement a Cache-Aside Pattern using YouTube Video IDs as primary keys to speed up response time and save-up OpenAI API token consumption

**Module Structure:**
* `database.py`: Manages SQLite connections and session lifecycles.
* `models.py`: Defines SQLModel database entities.
* `lyrics.db`: Local SQLite database file storing cached processed payloads.

> **Lesson Learnt: Schema Synchronization between FastAPI and SQLModel**
> SQLModel combines Pydantic data validation schemas with SQLAlchemy ORM (Object-Relational Mapping) modelling into a single Python class, eliminating duplicate code between FastAPI and SQLite.

> **Notes to Self (because all the SQL is confusing me):** Instead of writing raw SQL code, SQLAlchemy’s ORM syntax-es through SQLModel to query SQLite (a serverless relational database management system) . Example of native SQLAlchemy ORM methods: `db.add()`, `db.commit()`, and `db.refresh()` .

### Phase 3: Frontend UI
**Goal:** Create a responsive user interface with 3-columns lyric grid and a search bar.

### Phase 3.1: Connecting Backend to Frontend (make it fullstack)
**Goal:** In a nutshell, ensure “POST youtube url, RESPONSE hanzi, pinyin, english text” works.

### Phase 3.2: UI Styling
**Goal:** Polish the UI using tailwindcss

### Phase 4: Deploying
**Goal:** Deploy onto cloud platforms for public use. 
**Infrastructure:** Use Vercel (Frontend) and Render (Backend)

## Bugs and Troubleshooting Log

1. (25/09/2026) There were some error on passing valid cookies because YouTube flags requests from cloud hosting IP addresses (like Render) as automated bots. Solution: Add a search engine by artist and song name so yt-dlp don't always have to default to empty or users dont always need to have a YouTube URL to get around.

## Limitation and Future Work
There are *no* restrictions to only accept Chinese songs. So, even if the users submit other language songs, the website still generates Chinese lyrics (given the constraints I had to only extract Traditional Chinese lyrics for now) and consequently, the chinese-to-pinyin and the chinese-to-english. 

In the future, this project may display Japanese Kanji and Korean Hangul in addition to its romanization and translation. As well as, a toggle between simplified and traditional Chinese. The next update will come when the passion to learn a language re-ignites!

Future features/chores:
1. Better User Experience: add a loading/processing lyrics/fetching lyrics state to update the user while they wait

## Conclusion/ Reflection
For how simple the website looks, it took longer than expected to complete (about 3 months until the first deployment). This was my first time juggling fulltime work while doing a side-project. However, when you put in the dedication and the action, a little goes a long way!

I admit I did not become a master of using these tech stacks (since I had a Gemini guru to learn alongside with). Rather than a ‘vibe-coded’ project, I consider this journey an educational walkthrough to understand how the programs are broken down and how these different tech stacks come together. In the end, my notebook was filled with what I learnt and mistakes made along the way.

With more to learn, thus concludes my first LLM-based project.
