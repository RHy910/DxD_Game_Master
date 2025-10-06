# 🎲 D&D AI Dungeon Master with Sora Visualization

An AI-powered Dungeons & Dragons campaign system that brings your adventures to life with dynamic narrative generation and cinematic video visualization using OpenAI's Sora API.

## 🌟 Overview

This project creates an immersive solo D&D experience where an AI Dungeon Master runs campaigns that adapt to your playstyle, tone, and decisions. As your story unfolds, the system automatically generates cinematic video scenes using Sora, creating a fully visualized campaign experience.

### Key Features

- **🤖 Adaptive AI Dungeon Master**: Powered by GPT-4 and LangChain, the DM dynamically generates narratives that respond to player choices
- **🎭 Tone-Aware Storytelling**: Automatically detects your communication style (serious, casual, humorous) and adapts the narrative accordingly
- **🎬 Automatic Scene Generation**: Identifies key story moments and generates Sora prompts for cinematic video visualization
- **👥 AI Party Members**: Adventure with up to 3 AI-controlled companions with unique personalities
- **📊 Character Sheet Parsing**: Upload D&D character sheets to automatically create your in-game character
- **🗺️ Dynamic State Management**: Persistent world state that evolves based on your decisions
- **📖 Story Sharing**: Save and share completed campaigns with others
- **🌲 Procedural Branching**: Pre-written one-shot campaigns that branch into procedurally generated content

## 🏗️ Project Structure

```
dnd-ai-dm/
├── backend/
│   ├── dm_engine.py          # Core LangChain DM logic
│   ├── models.py              # Data models (Character, Scene, etc.)
│   ├── tone_analyzer.py       # Player tone detection
│   ├── scene_manager.py       # Scene transition logic
│   ├── campaign_loader.py     # Campaign template system (TODO)
│   └── sora_integration.py    # Sora API wrapper (TODO)
├── frontend/
│   └── dnd-dm-app.jsx         # React UI prototype
├── campaigns/
│   └── templates/             # Pre-written campaign files (TODO)
└── README.md
```

## 🎮 Current Features (MVP)

### Backend (Python + LangChain)

#### ✅ Implemented

- **Campaign State Management**
  - Tracks player location, decisions, story progression
  - Maintains party member information
  - Records tone preferences and adapts accordingly
  
- **Tone Analysis System**
  - Real-time detection of player communication style
  - Keyword and structure-based analysis
  - Dynamic DM personality adaptation

- **Scene System**
  - Automatic scene type detection (combat, dialogue, exploration, revelation)
  - Sora prompt generation for visual scenes
  - Scene transition triggers based on narrative flow

- **AI Party Management**
  - Support for up to 3 AI companions
  - Personality-driven interactions
  - Relationship tracking with player character

- **LangChain Integration**
  - Conversation memory for context continuity
  - Dynamic system prompts that update with game state
  - GPT-4 powered narrative generation

### Frontend (React)

#### ✅ Implemented

- **Chat Interface**
  - Text input for player actions
  - Voice input support (Chrome/Edge)
  - Message history with DM/player distinction

- **Campaign Display**
  - Character information panel
  - Current location tracking
  - Tone and scene count indicators

- **Scene Visualization Placeholders**
  - Shows when Sora scenes are triggered
  - Displays generated prompts for testing

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.9+
Node.js 16+
OpenAI API key
```

### Backend Setup

```bash
# Install dependencies
pip install langchain openai python-dotenv

# Set environment variables
export OPENAI_API_KEY="your-api-key-here"

# Run the DM engine
python backend/dm_engine.py
```

### Frontend Setup

```bash
# Install dependencies
npm install react lucide-react

# Run development server
npm run dev
```

## 📝 Usage Example

### Starting a Campaign

```python
from dm_engine import DungeonMasterAgent, Character, PartyMember

# Create your character
player = Character(
    name="Theron Stormwind",
    race="Human",
    char_class="Paladin",
    level=3,
    background="Noble",
    alignment="Lawful Good",
    stats={'str': 16, 'dex': 10, 'con': 14, 'int': 10, 'wis': 12, 'cha': 15},
    backstory="A knight seeking redemption for a past failure.",
    hp_current=28,
    hp_max=28
)

# Add party members
party = [
    PartyMember(
        name="Lyra Whisperwind",
        race="Elf",
        char_class="Ranger",
        level=3,
        personality="Cautious and perceptive, with dry wit",
        relationship_with_player="Trusted companion"
    )
]

# Initialize the DM
dm = DungeonMasterAgent(openai_api_key="your-key")

# Start campaign
state, opening = dm.start_campaign(
    campaign_name="The Missing Caravan",
    player_character=player,
    party_members=party
)

print(opening)  # DM introduces the adventure
```

### Playing the Game

```python
# Process player actions
player_input = "I accept the quest and ask about the missing caravans"

response, new_scene, sora_prompt = dm.process_turn(player_input, state)

print(response)  # DM's narrative response

if new_scene:
    print(f"Scene generated: {sora_prompt}")
    # This is where you'd call Sora API to generate video
```

## 🎯 Roadmap

### Phase 1: Core Engine ✅ (Current)
- [x] State management system
- [x] Tone adaptation
- [x] Scene detection and Sora prompt generation
- [x] Party member integration
- [x] Basic LangChain DM

### Phase 2: Campaign System (Next)
- [ ] Pre-written one-shot campaign templates
- [ ] Campaign branching logic
- [ ] Multiple campaign options
- [ ] Save/load system

### Phase 3: Character Integration
- [ ] Character sheet parser (PDF/image)
- [ ] D&D Beyond integration
- [ ] Manual character creation UI
- [ ] Character progression tracking

### Phase 4: Sora Integration
- [ ] Sora API wrapper (when API becomes available)
- [ ] Video caching system
- [ ] Queue management for generation
- [ ] Visual consistency tracking

### Phase 5: Advanced Features
- [ ] Dice rolling and combat mechanics
- [ ] Voice output (text-to-speech for DM)
- [ ] Multi-session campaign support
- [ ] Story sharing and export
- [ ] Social features (campaign gallery)

### Phase 6: Multiplayer (Future)
- [ ] Real-time multiplayer support
- [ ] Shared campaign experiences
- [ ] Player-to-player interaction

## 🔧 Technical Architecture

### Backend Stack
- **LangChain**: Orchestration and memory management
- **OpenAI GPT-4**: Narrative generation and DM logic
- **OpenAI Sora**: Video scene generation (when available)
- **Python 3.9+**: Core backend language

### Frontend Stack
- **React**: UI framework
- **Tailwind CSS**: Styling
- **Lucide Icons**: UI icons
- **Web Speech API**: Voice input

### Planned Integrations
- **Firebase/Supabase**: User data and campaign persistence
- **AWS S3/Cloudflare R2**: Video storage
- **WebSockets**: Real-time updates for multiplayer

## 🎨 Design Principles

1. **Player Agency First**: The AI never controls player actions, only describes consequences
2. **Adaptive Storytelling**: The narrative adapts to player tone and choices
3. **Cinematic Experience**: Key moments are visualized through Sora-generated scenes
4. **Persistent World**: Decisions have lasting consequences that affect the story
5. **Accessibility**: Support for both text and voice input

## 🔐 Environment Variables

```bash
OPENAI_API_KEY=your-openai-api-key
SORA_API_KEY=your-sora-api-key  # When available
DATABASE_URL=your-database-url  # For campaign persistence
```

## 🤝 Contributing

This is currently a solo project in early development. Contribution guidelines will be added as the project matures.

## 📄 License

TBD

## 🐛 Known Issues

- Sora API not yet publicly available (using mock prompts)
- Scene consistency across videos needs manual prompt engineering
- Character sheet parser not yet implemented
- No save/load functionality yet

## 💡 Future Improvements

- **Enhanced Memory**: Use LangChain's more sophisticated memory types for long campaigns
- **Vector Embeddings**: Store campaign lore and world state in vector DB for better context retrieval
- **Multi-modal Input**: Support for image uploads (maps, character art)
- **Voice Cloning**: Generate unique voices for different NPCs
- **Music Generation**: Dynamic background music that matches scene tone

## 📞 Contact

For questions or collaboration inquiries, please open an issue on the GitHub repository.

---

**Note**: This project uses OpenAI's Sora API which is currently in limited release. The system is designed with Sora integration in mind, but currently uses generated prompts that can be used once the API becomes publicly available.

Built with ⚔️ by adventurers, for adventurers.