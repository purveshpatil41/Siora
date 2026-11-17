from fastapi import FastAPI, Depends
from datetime import datetime
import httpx
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
from database import engine, Base, get_db
from sqlalchemy.orm import Session
import models

Base.metadata.create_all(bind=engine)


class Context(BaseModel):
    url: str | None = None
    title: str
    videoTimestamp: float | None = None
    selectedText: str | None = None


class ChatRequest(BaseModel):
    user_query: str
    context: Context
    conversation_id: int | None = (
        None  # (means its optional , first time chat will be Null)
    )


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OMNIROUTE_URL = os.getenv(
    "OMNIROUTE_URL", "http://localhost:20128/v1/chat/completions"
)

PRIORITY_MODELS = [
    "kr/minimax-m2.5",  # 1. Primary — general tutoring
    "kr/glm-5",  # 2. Strong alternative — reasoning
    "kr/qwen3-coder-next",  # 3. Technical and programming questions
    "kr/claude-haiku-4.5",  # 4. Fast conversational fallback
    "kr/minimax-m2.1",  # 5. General-purpose fallback
    "gc/grok-4.7",  # 6. Alternative provider
    "horde/google/gemma-4-31b",  # 7. Free fallback
    "horde/aphrodite/TheDrummer/Skyfall-31B-v4.2",  # 8. Additional free fallback
]


async def call_llm_with_fallback(messages: list[dict], timeout: float = 35.0) -> str:
    """
    Tries models in order of priority. If a model fails or times out,
    automatically falls back to the next model in the hierarchy.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        last_error = None
        for model_id in PRIORITY_MODELS:
            try:
                print(f"Routing request to model [{model_id}]...")
                response = await client.post(
                    OMNIROUTE_URL, json={"model": model_id, "messages": messages}
                )
                if response.is_success:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"]
                    print(f"Success with model [{model_id}]!")
                    return answer
                else:
                    print(
                        f"Model [{model_id}] failed ({response.status_code}): {response.text[:120]}"
                    )
                    last_error = f"HTTP {response.status_code}: {response.text[:120]}"
            except httpx.TimeoutException:
                print(
                    f"Model [{model_id}] timed out after {timeout}s. Falling back to next..."
                )
                last_error = f"Timeout ({timeout}s)"
            except Exception as e:
                print(f"Error with model [{model_id}]: {e}")
                last_error = str(e)
        raise RuntimeError(f"All 8 fallback models failed. Last error: {last_error}")


# Global In-Memory Cache: { video_id: [transcript_chunks...] }
TRANSCRIPT_CACHE: dict[str, list[dict]] = {}


def format_timestamp(seconds: float | None) -> str:
    if seconds is None or seconds < 0:
        return "Not available"

    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def extract_video_id(url: str) -> str | None:
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None


def get_video_transcript(video_id: str):
    try:
        # Step 1: Video ke saare available transcripts list karo
        ytt_api = YouTubeTranscriptApi()

        transcript_list = ytt_api.list(video_id)

        # Step 2: Preferred languages me dhoondo
        try:
            transcript = transcript_list.find_transcript(
                ["en", "en-US", "en-GB", "hi", "en-IN"]
            )
        except Exception:
            # Step 3: Agar preferred nahi mila, toh jo bhi 1st available track hai wo le lo
            transcript = next(iter(transcript_list))

        # Step 4:  Fetch karo aur clean dict list me convert karo
        fetched = transcript.fetch()
        return fetched.to_raw_data()

    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
        return None


def get_transcript_window(
    transcript: list[dict] | None,
    current_time: float | None,
    past_seconds: float = 120.0,
    future_seconds: float = 30.0,
) -> str:

    if not transcript or current_time is None:
        return "No transcript available for this video."

    start_bound = max(0.0, current_time - past_seconds)
    end_bound = current_time + future_seconds

    relevant_snippets = []

    for chunk in transcript:

        chunk_start = chunk.get("start", 0.0)

        if start_bound <= chunk_start <= end_bound:
            time_str = format_timestamp(chunk.get("start", 0.0))
            text = chunk.get("text", "").strip()
            relevant_snippets.append(f"[{time_str}] {text}")

    if not relevant_snippets:
        return "No spoken words recorded around this timestamp."

    return "\n".join(relevant_snippets)


@app.get("/transcript")
def fetch_transcript(url: str):
    video_id = extract_video_id(url)
    if not video_id:
        return {"error": "Invalid YouTube URL", "transcript": None}

    transcript = get_video_transcript(video_id)
    if not transcript:
        return {"error": "No transcript available for this video", "transcript": None}

    return {
        "video_id": video_id,
        "total_chunks": len(transcript),
        "transcript": transcript,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):

    user_query = request.user_query
    context = request.context

    conversation = None
    if request.conversation_id:
        conversation = (
            db.query(models.Conversation)
            .filter(models.Conversation.id == request.conversation_id)
            .first()
        )

    if not conversation:
        conversation = models.Conversation(
            video_url=context.url,
            video_title=context.title,
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    transcript_window = "No transscript  available for this video."

    if context.url:
        video_id = extract_video_id(context.url)
        if video_id:
            # check cache first
            if video_id not in TRANSCRIPT_CACHE:
                fetched = get_video_transcript(video_id)
                if fetched:
                    TRANSCRIPT_CACHE[video_id] = fetched

            cached_transcript = TRANSCRIPT_CACHE.get(video_id)

            if cached_transcript and context.videoTimestamp is not None:
                transcript_window = get_transcript_window(
                    cached_transcript,
                    context.videoTimestamp,
                    past_seconds=120.0,
                    future_seconds=30.0,
                )

    formatted_time = format_timestamp(context.videoTimestamp)

    system_prompt = f"""You are Siora, an intelligent AI learning companion embedded directly in the student's browser.
Your mission is to help students deeply understand educational content (YouTube lectures, tutorials, and documentation) in real-time.

=== 1. CURRENT RESOURCE / VIDEO CONTEXT ===
- Title: "{context.title}"
- URL: "{context.url or 'N/A'}"
- Active Playback Timestamp: {formatted_time}
- Highlighted / Selected Text: "{context.selectedText or 'None'}"

=== 2. LOCAL TRANSCRIPT (Spoken around {formatted_time}) ===
\"\"\"
{transcript_window}
\"\"\"

=== 3. CONVERSATIONAL MEMORY & INTERACTION GUIDELINES ===
1. CONTEXT AWARENESS:
   - You HAVE direct access to the student's current video context and the local transcript window provided above. Never claim you cannot see or process the video.
   - If the student asks about what was just said, shown, or explained around {formatted_time}, ground your explanation in the transcript above.

2. CONVERSATION CONTINUITY:
   - The messages following this system prompt represent the ongoing conversation history with the student.
   - Use this history to resolve pronouns and references (e.g., "explain that again", "give code for that", "summarize our chat").
   - Respond directly to the student's LATEST message at the end of the history.

3. PEDAGOGICAL TEACHING STYLE:
   - Explain concepts from first principles with intuitive real-world examples.
   - Use clean Markdown: bold key terms, use bullet points for lists, and syntax-highlighted code blocks for technical snippets.
   - Be concise and encourage active learning. If information is not in the transcript (like total video duration or unmentioned topics), honestly state that it is not covered in the local transcript window rather than making things up.

4. OUTPUT FORMATTING & CONSTRAINTS:
   - Begin your helpful response directly.
   - NEVER prepend your response with timestamps, dates, or speaker tags (e.g., "[Siora answered]:", "[Siora responded]:", or any bracketed metadata).
"""

    recent_messages = (
        db.query(models.Message)
        .filter(models.Message.conversation_id == conversation.id)
        .order_by(models.Message.created_at.desc())
        .limit(5)
        .all()
    )
    past_messages = list(reversed(recent_messages))

    messages = [{"role": "system", "content": system_prompt}]

    for msg in past_messages:
        if msg.role == "user":
            time_str = (
                msg.created_at.strftime("%d %b %y, %I:%M %p")
                if msg.created_at
                else "Unknown time"
            )
            video_pos = (
                f"at video playback {format_timestamp(msg.video_timestamp)}"
                if msg.video_timestamp is not None
                else "video playback unknown"
            )
            enriched_content = (
                f"[{time_str} | Student asked {video_pos}]:\n{msg.content}"
            )
            messages.append({"role": "user", "content": enriched_content})
        else:
            # Clean assistant content: Strip any accidental old prefix if stored earlier in DB
            clean_content = re.sub(
                r"^\[.*?Siora\s+(?:answered|responded).*?\]:\s*",
                "",
                msg.content,
                flags=re.IGNORECASE,
            ).strip()
            messages.append({"role": "assistant", "content": clean_content})

    current_time_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
    active_user_query = f"[{current_time_str} | Active Question at video playback {formatted_time}]:\n{user_query}"
    messages.append({"role": "user", "content": active_user_query})

    ai_answer = await call_llm_with_fallback(messages)

    # Defensive cleaning: Strip any hallucinated prefix if model still produced one
    ai_answer = re.sub(
        r"^\[.*?Siora\s+(?:answered|responded).*?\]:\s*",
        "",
        ai_answer,
        flags=re.IGNORECASE,
    ).strip()

    user_msg = models.Message(
        conversation_id=conversation.id,
        role="user",
        content=user_query,
        video_timestamp=context.videoTimestamp,
    )

    ai_msg = models.Message(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_answer,
        video_timestamp=context.videoTimestamp,
    )

    db.add(user_msg)
    db.add(ai_msg)
    db.commit()

    return {
        "answer": ai_answer,
        "conversation_id": conversation.id,
    }
