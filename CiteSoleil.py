"""
D&D AI DM Backend - LangChain Powered Campaign Engine
Handles dynamic state management, scene transitions, and narrative generation
"""
import os
from DungeonMasterAgent import DungeonMasterAgent
from Player import Character
from Party import PartyMember

from dotenv import load_dotenv
load_dotenv()


def main():
    """Example usage of the DM system"""
    
    # Create player character
    player = Character(
        name="Theron Stormwind",
        race="Human",
        char_class="Paladin",
        level=3,
        background="Noble",
        alignment="Lawful Evil",
        stats={'str': 16, 'dex': 10, 'con': 14, 'int': 10, 'wis': 12, 'cha': 15},
        backstory="A knight seeking redemption for a past failure.",
        hp_current=28,
        hp_max=28
    )
    
    # Create party members
    party = [
        PartyMember(
            name="Lyra Whisperwind",
            race="Elf",
            char_class="Ranger",
            level=3,
            personality="Cautious and perceptive, with a dry wit",
            relationship_with_player="Trusted companion, met during training"
        ),
        PartyMember(
            name="Grimble Tinkertop",
            race="Gnome",
            char_class="Wizard",
            level=3,
            personality="Enthusiastic and curious, prone to experimentation",
            relationship_with_player="Hired for magical expertise"
        )
    ]
    
    # Initialize DM
    dm = DungeonMasterAgent(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-3.5-turbo"
    )
    
    # Start campaign
    state, opening = dm.start_campaign(
        campaign_name="The Missing Caravan",
        player_character=player,
        party_members=party
    )
    
    print("\n\n\n\n\n=== CAMPAIGN START ===")
    print(opening)
    print(f"\n[Scene Generated: {state.current_scene.sora_prompt}]")
    
    # Example gameplay loop
    while True:
        print("\n" + "="*60)
        player_action = input("\nWhat do you do? > ")
        
        if player_action.lower() in ['quit', 'exit']:
            break
        
        dm_response, new_scene, sora_prompt = dm.process_turn(player_action, state)
        
        print(f"\n{dm_response}")
        
        if new_scene:
            print(f"\n[NEW SCENE GENERATED]")
            print(f"Sora Prompt: {sora_prompt}")
        
        print(f"\n[Turn {state.turn_count} | Tone: {state.player_tone.value}]")


if __name__ == "__main__":
    main()