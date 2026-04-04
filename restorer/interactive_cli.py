import sys
import os
from restorer.replay_editor import ReplayEditor

def main():
    if len(sys.argv) < 2:
        print("Usage: python restorer/interactive_cli.py <path_to_replay>")
        return

    path = sys.argv[1]
    editor = ReplayEditor()
    editor.load(path)
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"--- Rocket League Replay Editor ---")
        print(f"File: {path}\n")
        
        # Discovery current values (Mock logic for display)
        print(f"[1] Edit Replay Name")
        print(f"[2] Edit Player 1 Name")
        print(f"[3] Edit Player 1 Goals")
        print(f"[S] Save Changes")
        print(f"[Q] Quit")
        
        choice = input("\nSelection: ").upper()
        
        if choice == '1':
            new_val = input("New Replay Name: ")
            editor.update_str_property("ReplayName", new_val)
        elif choice == '2':
            new_val = input("New Player Name: ")
            # Assuming occurrence 1 for simplicity in this basic CLI
            editor.update_str_property("PlayerName", new_val, occurrence=1)
        elif choice == '3':
            new_val = int(input("New Goals: "))
            # Assuming occurrence 1 for simplicity in this basic CLI
            editor.update_int_property("Goals", new_val, occurrence=1)
        elif choice == 'S':
            output_path = path + ".edited.replay"
            editor.save(output_path)
            print(f"Saved to {output_path}")
            input("\nPress Enter to exit...")
            break
        elif choice == 'Q':
            break

if __name__ == "__main__":
    main()
