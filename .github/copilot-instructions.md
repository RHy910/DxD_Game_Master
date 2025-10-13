<!-- .github/copilot-instructions.md for DxD_Game_Master (CiteSoleilOnline) -->
# Repo-specific instructions for AI coding agents

This project implements an AI-driven D&D Dungeon Master engine (Python 3.9+) with LangChain/OpenAI integration and an intended Sora visualization pipeline. The guidance below is focused and actionable for code changes in this repo.

- Primary entry points and purpose
  - `DungeonMasterAgent.py` — main orchestration (LLM setup, memory, turn processing, campaign start). Treat this as the high-level controller.
  - `CampaignState.py` — persistent in-memory state shape. Use `to_context()` when building system prompts.
  - `SceneManager.py` — scene detection and Sora prompt generation. Scene triggers are based on trigger phrases and turn frequency.
  - `ToneAnalyzer.py` — simple keyword-based tone classifier. Prefer adding keywords or refining scoring here rather than changing callers.

- Coding patterns & conventions
  - Data classes are used to hold domain objects (`Scene`, `Character`, `CampaignState`, `PartyMember`). Use their `to_context()` methods when building prompts.
  - The project uses synchronous LangChain-style calls (passing a list of SystemMessage/HumanMessage). Keep message order: SystemMessage first, then HumanMessage.
  - LLM call site: `self.llm(messages)` returns an object with `.content`. Preserve this usage when refactoring.
  - Add new fields to `CampaignState` carefully; `to_context()` serializes selected fields for system prompts.

- Where to make small, low-risk improvements
  - Improve `SceneManager.create_scene_from_narrative()` to use a short LLM extraction call for structured fields (title, npcs_present, danger_level). Keep current fallback heuristics.
  - Expand `ToneAnalyzer.TONE_KEYWORDS` or add small NLP heuristics inside `ToneAnalyzer.analyze()` if tone mistakes appear. Do not change `ToneType` enum values; they're persisted in state.
  - When touching prompts, update `DungeonMasterAgent.create_system_prompt()` — it centralizes tone rules and instructions and is used for both campaign start and per-turn messages.

- Tests, environment, and runtime
  - No test suite currently exists; `test.py` contains a small OpenAI model-listing snippet for validating API key setup. Use `.env` or `export OPENAI_API_KEY` on macOS zsh.
  - Expected runtime requirements: Python 3.9+, packages referenced in README (langchain, openai, python-dotenv). Use a venv and `pip install langchain openai python-dotenv`.

- Common pitfalls & project-specific rules
  - The code expects `Scene.scene_type` to be a `SceneType` Enum (string values like "exploration"). When constructing Scene objects directly, use `SceneType.EXPLORATION` etc.
  - `CampaignState.change_scene()` appends the previous scene id to `scenes_visited` and increments `scenes_generated`; keep these semantics when adding persistence.
  - `DungeonMasterAgent.process_turn()` mutates `state` (tone, turn_count, current_scene). Prefer returning new state only if you also update all call sites.
  - `memory` uses LangChain `ConversationBufferMemory` and adds messages via `self.memory.chat_memory.add_user_message()` and `add_ai_message()`. Preserve these calls for continuity.

- Integration & external dependencies
  - OpenAI / LangChain: `DungeonMasterAgent` expects an OpenAI key passed to `ChatOpenAI`; do not hardcode API keys in source. Use the environment and `test.py` for quick checks.
  - Sora: Not yet integrated; visual prompt generation is in `Scene.generate_sora_prompt()`. If adding Sora calls, use `scene.sora_prompt` as the payload and add queuing/caching.

- Quick examples (copy-paste friendly)
  - Build a system prompt: call `state.to_context()` and then `DungeonMasterAgent.create_system_prompt(state)`; system prompts must remain SystemMessage first.
  - Detecting a scene: `SceneManager.should_trigger_new_scene(dm_response, state)` — uses trigger phrases and `state.turn_count % 5 == 0`.

- What not to change without review
  - Message ordering and memory calls in `DungeonMasterAgent` (these affect conversation continuity). Any change to message shapes or memory storage should be validated with a live DM session.
  - `ToneType` enum values and `CampaignState` field names used in `to_context()` — external prompts depend on these exact labels.

If anything in these notes is unclear or missing (deploy steps, CI commands, desired test harness), tell me which area to expand and I will iterate. After your feedback I can refine examples or add a minimal `requirements.txt` / test harness.
