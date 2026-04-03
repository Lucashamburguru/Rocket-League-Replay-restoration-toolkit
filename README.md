# Rocket League Replay Restorer (v1.3)
### Restoring Legacy Replays (Net 10) for the 2026 Engine (Net 11)

> [!IMPORTANT]
> **ALWAYS BACKUP YOUR REPLAYS BEFORE USE.** 
> While this tool is designed to be "Surgical" and safe, modifying binary data always carries a risk of file corruption. Copy your legacy `.replay` files to a safe location before running the restoration scripts.

---

## **Quick Start**

1.  **Place Replays**: Put your old `.replay` files into the **`input_replays/`** folder.
2.  **Run the Tool**:
    -   **Windows**: Double-click **`restore_replays.bat`**.
    -   **Linux / Steam Deck**: Run **`./restore_replays.sh`** (ensure it has execute permissions).
3.  **Collect Fixes**: Your restored files will be in the **`restored_replays/`** folder.
4.  **Install**: Copy the restored files to your Rocket League Demos folder:
    `Documents\My Games\Rocket League\TAGame\Demos`

---

## **Technical Details**
This tool performs a "Surgical Bit-Shift" on the binary data:
-   **Header Update**: Patches the version and re-calculates the bit-perfect UE3 CRC.
-   **Hoops Shift**: Automatically detects Hoops matches and re-maps the ball archetype (from `Ball_BasketBall` to `ball_luminousairplane`) while shifting the entire 1.2MB netstream forward by 6 bytes.
-   **Soccar Refresh**: Updates the secondary Netstream checksums without shifting data.

---

## **Requirements**
-   Python 3.x installed and in your PATH.

---

## **Version History**

### **v1.3 (Latest)**
- **Legacy Hoops Support**: Added support for pre-2024 Hoops replays. Automatically patches the legacy `GameEvent_Basketball` archetype to `GameInfo_Basketball`, ensuring older replays don't crash the modern engine.

### **v1.2**
- **Folder Skeleton**: Added empty `input_replays/` and `restored_replays/` folder structures to the toolkit.
- **Improved Scripting**: Unified the `.bat` and `.sh` scripts to handle the new directory structure.

### **v1.1**
- **Mutator Support**: Added detection for `Ball_BasketBall_Mutator`.
- **Dynamic Bit-Shift**: Implemented automatic switching between +6 and -2 byte shifts depending on the match type.

### **v1.0**
- **Initial Release**: Cracked the UE3 CRC32 algorithm and implemented the first surgical bit-shift for standard Hoops matches.

---
**Created by Gemini & Pengo (March 2026)**
*"Preserving every flip reset, now and forever."*
