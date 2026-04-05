# Hoops Archetype Mapping Master List
### A complete reference of binary string transformations for Hoops restoration.

This list maps legacy Rocket League object names to their modern (Post-March 2026) equivalents. The engine relies on these strings to load assets and classes; if an outdated string is encountered, the game crashes.

---

## **1. Ball Archetypes (The Visual Model)**
These patches ensure the modern engine loads the correct 3D model and physical properties for the Hoops ball.
| Legacy String (Pre-March 2026) | Modern Replacement | Era / Notes |
| :--- | :--- | :--- |
| `Archetypes.Ball.Ball_Basketball` | `Archetypes.Ball.ball_luminousairplane` | **Ancient (2017):** Note the lowercase 'b' in the second half. |
| `Archetypes.Ball.Ball_BasketBall` | `Archetypes.Ball.ball_luminousairplane` | **Legacy (2018-2026):** Standard pre-2026 Hoops ball. |
| `Archetypes.Ball.Ball_BasketBall_Mutator` | `Archetypes.Ball.ball_luminousairplane` | **Mutator Matches:** Used when custom physics or sizes were applied. |

## **2. Game Event Logic (The Match Rules)**
These patches intercept requests for deleted match-logic classes and redirect them to the modern consolidated GameInfo class.
| Legacy String (Pre-March 2026) | Modern Replacement | Notes |
| :--- | :--- | :--- |
| `Archetypes.GameEvent.GameEvent_Basketball` | `GameInfo_Basketball.GameInfo.GameInfo_Basketball:Archetype` | Handles core match spawning, rules, and state replication. |

## **3. Map Targets / Goal Volumes (The Physics Triggers)**
These patches update the internal names of the scoring triggers inside the classic `HoopsStadium_P` map. Without these, the engine cannot locate the goals and crashes on load.
| Legacy String | Modern Replacement | Era |
| :--- | :--- | :--- |
| `HoopsStadium_P.TheWorld:PersistentLevel.GoalVolume_TA_2.Goal_TA_0` | `HoopsStadium_P.TheWorld:PersistentLevel.GoalVolume_Hoops_TA_0.Goal_Hoops_TA_0` | **Early (2017-2018)** |
| `HoopsStadium_P.TheWorld:PersistentLevel.GoalVolume_TA_3.Goal_TA_0` | `HoopsStadium_P.TheWorld:PersistentLevel.GoalVolume_Hoops_TA_1.Goal_Hoops_TA_0` | **Early (2017-2018)** |

## **4. Package / Extension Stripping (The Asset Loaders)**
Modern Rocket League has deprecated the `.upk` suffix in internal object references. These patches surgically strip the extension so the engine can locate the packages.
| Legacy String | Modern Replacement | Era / Notes |
| :--- | :--- | :--- |
| `HoopsStadium_P.upk` | `HoopsStadium_P` | **Ancient (2017):** Main map package. |
| `HoopsStadium_SFX.upk` | `HoopsStadium_SFX` | **Ancient (2017):** Stadium audio/crowd logic. |
| `GameInfo_Basketball_SF.upk` | `GameInfo_Basketball` | **Ancient (2017):** Core basketball logic package. |

---
**Technical Note:** All strings are patched as **Pascal Strings** (4-byte length prefix + null-terminated bytes). The restoration toolkit automatically calculates the difference in length between the Old and New strings, shifts the subsequent binary data, and recalculates all cyclic redundancy checks (CRCs) to ensure the file remains valid.

**Maintained by Pengo & Gemini**
