# Mind Companion

**An AI companion that actually listens — and knows when to say "please talk to someone."**

Mind Companion pairs a warm, conversational AI with a grounded knowledge base of real therapeutic techniques (CBT, DBT, ACT) and a safety-first pipeline that recognizes emotional distress and routes crisis-level conversations differently from everyday check-ins. Built as a full product: Flutter mobile app, FastAPI backend, and a retrieval-augmented conversation engine — not a thin wrapper around a chatbot API.

> **Responsible by design**: Mind Companion is explicitly *not* a therapist, doctor, or diagnostic tool. It offers psychoeducation, emotional support, and evidence-based coping techniques, and is built to recognize when a conversation needs a real human — then say so clearly.

---

## Why it's different from "just prompting an LLM"

Most AI chat wrappers send a message straight to a language model and hope for the best. Mind Companion runs every message through a purpose-built pipeline first:

| Step | What it does |
|---|---|
| **Emotion & intensity read** | Classifies what the user is feeling and how intensely, before deciding how to respond |
| **Risk check** | A dedicated safety classifier flags safe / elevated / crisis — biased toward caution when uncertain |
| **Crisis routing** | Crisis-level messages skip everything else and go straight to a calm, human-first safety response — no techniques, no exercises, just support and a clear path to real help |
| **Grounded retrieval** | Everyday responses pull from a curated library of real techniques and protocols, so the AI isn't improvising mental-health advice from general training data |
| **Memory** | Conversations persist — the companion remembers what was said earlier in a chat, and long-term patterns feed personalized practice and insight recommendations |

## What's inside

- 💬 **Conversational chat** with real multi-turn memory, plus a **voice call mode** (speech-to-text + text-to-speech)
- 🧘 **Personalized practices** — grounding, breathing, and reframing techniques recommended by semantic search over a 60+ document knowledge base, not a static list
- 🔍 **Insights** — gentle, therapist-style reflections on recurring emotional patterns, generated from the user's own conversation history
- 🎨 **Polished, cohesive UI** — a custom "Dusk" visual identity (soft lavender-indigo + warm apricot) built on a proper design system, not default Material colors
- 🔐 **Accounts & auth** — JWT-based sign-up/sign-in
- 🐳 **One-command local stack** — Postgres, Redis, Qdrant, and the API all run via Docker Compose

## Tech stack

**Backend** — FastAPI · LangGraph · LangChain · PostgreSQL · Redis · Qdrant · OpenAI (or self-hosted via Ollama)
**Mobile** — Flutter · Riverpod · GoRouter
**Infra** — Docker Compose, structured (Pydantic-validated) LLM output throughout

## Getting started

```bash
# 1. Configure
cp .env.example .env        # add your OPENAI_API_KEY

# 2. Launch the stack
docker-compose up --build -d

# 3. Load the knowledge base (one-time, safe to re-run)
cd backend && python -m scripts.ingest_knowledge_base

# 4. Run the app
cd mobile && flutter pub get && flutter run
```
API docs live at `http://localhost:8000/docs`.

## Roadmap

- Enforced authentication on every endpoint (currently the auth flow is live; broader endpoint-level enforcement is in progress)
- Database migration tooling for safe schema evolution
- Automated test suite + CI
- Semantic (embedding-based) long-term memory, beyond today's keyword extraction

## License

For personal / portfolio use.

Built with care for mental wellness support.
