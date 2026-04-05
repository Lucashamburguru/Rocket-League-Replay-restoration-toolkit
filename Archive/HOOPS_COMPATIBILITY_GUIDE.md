# Rocket League Hoops: Compatibility & Version History
### A technical guide to the evolution of Hoops replays (2017–2026)

This document outlines the structural and metadata changes Psyonix implemented over the years and how the **Rocket League Replay Restorer** bridges the gap between historical recordings and the modern game engine.

---

## **The Golden Rules of Restoration**
1. **Protocol Preservation:** Rocket League's bitstream format changes over time (e.g., from NetVersion 0 to NetVersion 11). Never force a modern `NetVersion` onto an ancient replay. By preserving the original `NetVersion`, the engine correctly delegates parsing to its backward-compatible legacy parsers.
2. **Archetype Alignment:** The engine maps string names to internal 3D assets and game logic classes. If a replay requests an archetype that has been renamed or deleted, the game will crash during the loading screen. We must surgically patch legacy strings to their modern equivalents.
3. **CRC Integrity & Dynamic Shifting:** Because the replacement strings often differ in length from the originals, the entire binary payload shifts. Any byte shift requires full recalculation of both the Header and Body UE3 CRCs to prevent the engine from rejecting the file as corrupted.

---

## **Era 1: Ancient (Net 0) — 2017**
**Sample:** `B257F4AB48661FECCC9482A70E105CA9.replay`
*   **The Incompatibilities:**
    *   **UPK Extensions:** Early versions of Rocket League explicitly included Unreal Package extensions in object names (e.g., `HoopsStadium_P.upk` and `HoopsStadium_SFX.upk`). The modern engine expects clean package names and will crash if the extension is present.
    *   **Casing / Typographical Inconsistencies:** The ball archetype was named `Archetypes.Ball.Ball_Basketball` (with a lowercase 'b' in the second half of the word). Later eras capitalized it to `BasketBall`.
    *   **GameEvent Logic:** Used the legacy `Archetypes.GameEvent.GameEvent_Basketball` class to handle match rules and spawning.
*   **The Fix:** 
    *   Surgically strip `.upk\x00` from map and sound packages. 
    *   Replace the legacy, lowercase `Ball_Basketball` string with the modern `Archetypes.Ball.ball_luminousairplane` asset so the game loads the correct 3D model.
    *   Replace the legacy GameEvent with the modern `GameInfo_Basketball.GameInfo.GameInfo_Basketball:Archetype`.

## **Era 2: Early (Net 5–7) — 2018**
**Sample:** `D87F98BC4341A2580530AC92F26208E8.replay`
*   **The Incompatibilities:**
    *   **Normalized Casing:** The ball was renamed to `Archetypes.Ball.Ball_BasketBall` (uppercase 'B'), but it still points to a deprecated asset.
    *   **Legacy GameEvents:** Continued use of the deprecated `Archetypes.GameEvent.GameEvent_Basketball` class.
    *   **Goal Volume Drift:** The game map (`HoopsStadium_P`) used older goal volume names: `GoalVolume_TA_2` and `GoalVolume_TA_3`. Modern engines look for `GoalVolume_Hoops_TA_0` and `TA_1`.
*   **The Fix:** 
    *   Replace `Ball_BasketBall` with the modern `ball_luminousairplane` ball asset.
    *   Redirect the GameEvent spawn to the modern `GameInfo_Basketball` class.
    *   Remap the goal volume targets to the new `GoalVolume_Hoops_TA` naming scheme while strictly preserving the original `HoopsStadium_P` map prefix to avoid map-mismatch crashes.

## **Era 3: Legacy (Net 10–11) — 2019 – Feb 2026**
**Sample:** `2019.replay`
*   **The Incompatibilities:**
    *   **Ball Archetype:** Maintained the classic `Archetypes.Ball.Ball_BasketBall` asset string.
    *   **GameEvent Consolidation:** Still relied on the deprecated `Archetypes.GameEvent.GameEvent_Basketball` class, which modern Rocket League has since consolidated into the `GameInfo_Basketball` structure.
*   **The Fix:** Standardized replacement of the ball asset to `ball_luminousairplane` and the GameEvent logic to the modern `GameInfo_Basketball` equivalent. Goal volumes in this era are natively compatible, requiring no map patches.

## **Era 4: Modern (Net 11) — March 2026 – Present**
**Sample:** `2026.replay`
*   **Technical State:** 
    *   Natively uses `Archetypes.Ball.ball_luminousairplane` for the Hoops ball.
    *   Natively uses the consolidated `GameInfo_Basketball.GameInfo.GameInfo_Basketball:Archetype` for match logic.
    *   Supports multiple Hoops maps natively (e.g., Dunk House, The Block, hoopsStreet_p).
    *   Replays recorded in this era naturally conform to the modern engine's expectations and do not require any restoration.

---
**Maintained by Pengo & Gemini**
