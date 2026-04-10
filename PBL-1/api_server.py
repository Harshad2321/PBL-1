from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from nurture.main import NurtureGame
from nurture.core.enums import ParentRole

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game = NurtureGame()
game_initialized = False


def _normalize_01(value, default):
    """Normalize values that may be in 0-100 or 0-1 scale to 0-1."""
    if value is None:
        return default
    try:
        v = float(value)
    except (TypeError, ValueError):
        return default

    if v > 1.5:
        v = v / 100.0

    return max(0.0, min(1.0, v))


def _get_live_status_payload():
    """Return status payload mapped to the HUD scale used by GameMaker bars."""
    story_status = game.get_story_status() or {}
    rel_status = game.get_relationship_status() or {}

    rel_state = rel_status.get("relationship_state", {}) if isinstance(rel_status, dict) else {}
    ai_personality = rel_status.get("ai_personality_state", {}) if isinstance(rel_status, dict) else {}

    return {
        "day": story_status.get("day", 1),
        "act": story_status.get("act", 1),
        "trust": _normalize_01(rel_state.get("trust"), 0.5),
        "resentment": _normalize_01(rel_state.get("resentment"), 0.0),
        "closeness": _normalize_01(rel_state.get("emotional_closeness"), 0.5),
        "stress": _normalize_01(ai_personality.get("stress_level"), 0.3),
        "game_over": story_status.get("game_over", False),
        "collapse_reason": story_status.get("collapse_reason", None),
    }


def _build_scenario_payload():
    """Build scenario response shared by /start and /skip_day."""
    scenario_data = game.get_current_scenario()
    story_status = game.get_story_status()

    return {
        "scenario": (
            scenario_data.get("title", "") + "\n\n" +
            scenario_data.get("description", "") + "\n\n" +
            scenario_data.get("scenario_text", "")
        ),
        "choices": scenario_data.get("choices", []),
        "day": story_status.get("day", 1),
        "status": _get_live_status_payload(),
    }


def _apply_choice_impact(choice_number: int) -> None:
    """
    Apply deterministic short-term relationship effects from scenario choices.
    Choice 1 tends supportive, choice 2 neutral/ambivalent, choice 3 conflict-heavy.
    """
    if not game.ai_parent:
        return

    rel = game.ai_parent.relationship_state
    pers = game.ai_parent.ai_personality

    if choice_number == 1:
        rel.trust += 2.5
        rel.emotional_closeness += 2.0
        rel.resentment -= 1.0
        pers.stress_level -= 1.5
    elif choice_number == 2:
        rel.trust -= 0.5
        rel.emotional_closeness -= 0.5
        rel.resentment += 0.8
        pers.stress_level += 0.8
    elif choice_number == 3:
        rel.trust -= 2.5
        rel.emotional_closeness -= 2.0
        rel.resentment += 1.8
        pers.stress_level += 1.8

    rel.clamp()
    pers.clamp()


# ==========================
# REQUEST MODELS
# ==========================

class StartRequest(BaseModel):
    player_role: str


class ChooseRequest(BaseModel):
    day: int
    choice: int


class MessageRequest(BaseModel):
    message: str


class EndConversationRequest(BaseModel):
    pass


# ==========================
# START / NEXT DAY
# ==========================
@app.post("/start")
async def start_game(request: StartRequest):
    try:
        global game_initialized

        if not game_initialized:
            role = ParentRole.FATHER if request.player_role == "father" else ParentRole.MOTHER
            game.select_role(role)
            game_initialized = True
        
        # Mark current day as active so /choose can be processed.
        game._current_day_active = True

        payload = _build_scenario_payload()

        print("DAY:", payload.get("day"))

        return payload

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.post("/skip_day")
async def skip_day(request: EndConversationRequest):
    """Force day progression (used by F5 when player skips a scenario outright)."""
    try:
        if not game.story_engine:
            raise HTTPException(status_code=500, detail={"error": "Story engine is not initialized"})

        current_act = game.story_engine.acts[game.story_engine.current_act_index]
        if game.story_engine.progress.current_day < current_act.total_days:
            game.story_engine.progress.current_day += 1

        game._current_day_active = True
        return _build_scenario_payload()

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


# ==========================
# CHOICE HANDLING
# ==========================
@app.post("/choose")
async def make_choice(request: ChooseRequest):
    try:
        processed = game.respond_to_scenario(request.choice)

        if not processed:
            # Recover from any stale inactive-day state in API mode.
            game._current_day_active = True
            processed = game.respond_to_scenario(request.choice)

        if not processed:
            raise HTTPException(status_code=400, detail={"error": "Could not process choice for current day"})

        _apply_choice_impact(request.choice)

        rel_status = game.get_relationship_status()

        return {
            "state_delta": rel_status,
            "status": _get_live_status_payload(),
            "ai_reaction": "Choice processed. You can now talk with the child."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


# ==========================
# CHAT SYSTEM
# ==========================
@app.post("/message")
async def send_message(request: MessageRequest):
    try:
        reply = game.send_message(request.message)

        return {
            "reply": reply,
            "status": _get_live_status_payload()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


# ==========================
# STATUS (DEBUG / OPTIONAL)
# ==========================
@app.get("/status")
async def get_status():
    try:
        return _get_live_status_payload()

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


# ==========================
# END CONVERSATION
# ==========================
@app.post("/end_conversation")
async def end_conversation(request: EndConversationRequest):
    try:
        story_status = game.get_story_status()
        rel_status = game.get_relationship_status()

        day_summary = f"Day {story_status.get('day', 1)} complete. Trust: {rel_status.get('trust', 0.5):.2f}"

        return {
            "day_summary": day_summary,
            "trust_delta": 0.0,
            "next_scenario": "Next day scenario will be loaded..."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


# ==========================
# RUN SERVER
# ==========================
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)