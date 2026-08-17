# eFoil V1 — VESC Configuration Reference (v2)

**Originally configured:** June 12, 2026 (bench commissioning)
**Last updated:** August 7, 2026 (power diagnosis session — limits raised, throttle retuned)
**Hardware:** Flipsky 75200 Pro V2 (reports as HW 75_300_R2) + 65161 120KV + VX3 Pro remote
**Connectivity:** USB **and** integrated Bluetooth BLE — VESC Tool mobile connects wirelessly (confirmed working Aug 7). Android app; $3.99 on Google Play.
**Backups:** `vesc_mcconf.xml` + `vesc_appconf.xml` via ConfBackup. **Re-back-up after every change session** — settings have reset twice.

---

## Motor Configuration (current values)

### Detection results (FOC wizard, propeller profile, large inrunner)
| Parameter | Value |
|---|---|
| Motor R | 29.74 mΩ |
| Motor L | 52.16 µH |
| Motor Lq−Ld | 29.46 µH |
| Flux linkage | 16.30 mWb |
| Sensors | Sensorless |
| VESC ID | 16 |

### Current limits — **REVISED Aug 7, 2026**
| Parameter | Original | **Current** | Notes |
|---|---|---|---|
| Motor Current Max | 80 A | **180 A** | 80 A was the cause of the no-takeoff failure. See diagnosis below. |
| Motor Current Max Brake | 0 A | 0 A | No braking on a prop |
| Battery Current Max | 80 A | **100 A** | ~11 A/cell across 9P. Cells rated 15 A max continuous. |
| Battery Current Max Regen | 0 A | 0 A | BMS charge OCP is 10 A |
| Absolute Maximum Current (ABS) | 142.04 A | **240 A** | Must stay ~1.3–1.5× Motor Current Max or it nuisance-trips |

**Limit hierarchy (why three numbers):**
- **Battery Current Max** protects the pack (cells, nickel, BMS, main wiring)
- **Motor Current Max** protects the motor windings and ESC FETs — at low duty this can far exceed battery current with no pack impact
- **ABS Max Current** is a fast instantaneous trip, not a regulator. It shuts the ESC down rather than limiting.
- **JK BMS discharge limit stays at 120 A** — last-resort protection, deliberately above the VESC operating ceiling so it never trips in normal riding.

### Voltage / temperature
| Parameter | Value | Notes |
|---|---|---|
| Battery Voltage Cutoff Start | 42.0 V | 3.0 V/cell |
| Battery Voltage Cutoff End | 39.2 V | 2.8 V/cell, matches BMS UVP |
| MOSFET Temp Cutoff Start/End | 80 / 100 °C | Validated: peak observed 47.4 °C |
| Motor Temp Cutoff Start/End | 85 / 100 °C | **Inert** — sensor type Disabled |
| Motor Temperature Sensor Type | Disabled | 65161 has no temp sensor wired |
| FOC Temp Comp | **False** | Disabled because no sensor (was feeding constant 0 °C) |

**Note:** `temp_mos_2` and `temp_mos_3` report garbage (−94 °C, −101 °C) — those sensors are dead or unconnected. Only `temp_mos_1` is valid, and `temp_mos_max` correctly tracks it. Thermal picture comes from a single sensor.

### Setup / speed display
| Parameter | Value |
|---|---|
| Motor Poles | 6 (3 pole pairs) |
| Direct Drive | True |
| Wheel Diameter | 160 mm (prop diameter — **display only, not real speed**) |
| Battery | Li-ion 3.0–4.2 V, 14S, 45 Ah |
| Invert Motor Direction | False |

---

## App Configuration (current values)

| Parameter | Value | Notes |
|---|---|---|
| App to Use | **UART** | NEVER "PPM and UART". **This resets itself — verify every session.** |
| UART Baudrate | 115200 | VX3 default |
| Timeout | 1000 ms | Link dies → coast to stop |
| Timeout Brake Current | 0 A | Coast, don't brake |

### VESC Remote page (VX3 data path over UART) — **REVISED Aug 7**
| Parameter | Original | **Current** | Notes |
|---|---|---|---|
| Control Type | Current No Reverse | **Current No Reverse** | Resets to OFF after wizards — check first when throttle is dead |
| Positive Ramping Time | 0.8 s | **0.4 s** | 0.8 s made takeoff mushy |
| Negative Ramping Time | 0.2 s | 0.2 s | |
| Throttle Expo | −25 % | **0 %** | Linear. Polynomial mode (irrelevant at 0 %) |
| Throttle Expo Brake | 0 % | 0 % | |
| **Input Deadband** | 15 % | **3 %** | 15 % killed the bottom of the trigger travel |

### VX3 remote onboard settings
| Setting | Value |
|---|---|
| Control Type | UART |
| ESC Type | FSESC |
| Usage scenario | eSurf, no IAP receiver |
| Throttle deadband | 2–3 % (was 5 %) |
| Throttle initiative | Level 3 |
| Battery cells | **14** (was 12 — wrong, made the on-remote gauge lie) |
| Throttle calibration | Speed 1095–1406, Brake 1118–1374 |

---

## Aug 7, 2026 — Power diagnosis (the 1500 W problem)

**Symptom:** Board would not get on foil. Power capped at ~1,271 W / 25 A battery, throttle felt delayed and soft.

**What it was NOT:**
- Not the pack — BMS log showed zero OCP events, ever. Discharge limit 120 A, never approached.
- Not the battery limit — Battery Current Max was 80 A, actual draw was 22 A.
- Not Duty mode — duty sat at 38 % because in current mode duty is an *output*, not a command.
- Not throttle mapping — current pinned exactly at the limit, proving full trigger commanded full current.

**What it was:** **Motor Current Max at 80 A.** Motor current read 79 A against an 80 A ceiling. Because battery current ≈ motor current × duty, 79 A × 38 % ≈ 25 A battery = ~1,271 W. The motor was torque-starved and could not accelerate the prop past low RPM.

**Fix sequence and results:**
| Motor limit | Battery A | Peak power |
|---|---|---|
| 80 A (original) | 22 A | 1,271 W |
| 120 A | 41 A | ~2,300 W |
| 150 A | 62–79 A | **4,169 W measured** |
| 180 A (set, untested) | ~100 A expected | **~5.3 kW expected** |

**Secondary fault:** raising Motor Current Max to 150 A produced `FAULT_CODE_ABS_OVER_CURRENT` — ABS Max Current was still at its old value and tripping first. Raised ABS to 200 A (now 240 A); faults stopped completely.

### Measured log data — Aug 7 hot tub session (66 min, 35,789 samples)
| Metric | Value |
|---|---|
| Peak motor current | 153.3 A |
| Peak battery current | 78.8 A |
| Peak power | **4,169 W** |
| Peak duty | 91 % |
| Peak ERPM | 13,977 |
| Voltage under 79 A load | 52.8 V (from 56.8 V rest — **minimal sag, healthy cells**) |
| Peak FET temp | **47.4 °C** — dropped to 37–38 °C for the rest of the session |
| ABS faults | 68, all between t=1053–1117 s, **zero after ABS was raised** |
| Under-voltage fault | 1, at t=3961 s during shutdown — not real |

**Thermal conclusion:** passive cooling sheds heat far better than expected. Enormous headroom to the 80 °C cutoff. Not currently a constraint.

---

## Gotchas discovered during commissioning

1. **ESC power button is mandatory.** The 75200 Pro V2 will not boot — no LED, nothing — unless the included latching button is connected and pressed ON. Lives inside the ESC enclosure, permanently latched; the BMS button is the system power switch.

2. **Never set App to Use = "PPM and UART".** Receiver is on UART; the PPM pin floats and reads noise as a stream of ~0 % throttle commands that override everything. Symptom: faint ticking, duty blips of ~0.1 %, no faults logged.

3. **Control Type defaults to OFF after wizard/firmware changes.** Trigger does nothing but telemetry still works → check Control Type first. Must be Current No Reverse.

4. **The Input Setup Wizard is dangerous — do not enter it.** It only offers PPM / NRF / ADC / nunchuk. UART is not listed because it isn't configured there. **Merely opening it reset App to Use and killed throttle on Aug 7.** For UART remotes, set App to Use = UART in App Cfg → General and never touch the wizard. (Confirmed against Flipsky's own UART instructions, which contain no wizard step.)

5. **CHANGING A VALUE IS NOT WRITING IT.** The RT Data gauge scale updates from the app's *local* config the moment you move a slider — before it reaches the ESC. Cost an entire test cycle on Aug 7. **Always hit Write, then Read back to confirm.**

6. **ABS Max Current is a separate ceiling from Motor Current Max.** Raising motor current without raising ABS produces immediate overcurrent faults. Keep ABS at ~1.3–1.5× motor current.

7. **App to Use resets spontaneously.** Observed twice on Aug 7. Verify UART before every session.

8. **Turning the handheld off does NOT silence the UART line.** The receiver keeps streaming failsafe zeros as long as it has 5 V. To isolate, unplug the receiver connector.

9. **Unloaded bench behavior lies.** Small trigger input → duty runs to 100 % with no load. Judge throttle on the water.

10. **USB doesn't power the ESC.** Battery on (via BMS) first, then USB.

11. **Mobile app can't reach everything.** Full parameter tree is under the gear icon → Motor Cfg / App Cfg tabs. Some parameters are desktop-VESC-Tool only.

---

## Pre-session checklist (do before every trip — no cell service at Lucky Peak)

- [ ] **Read back** Motor Current Max = 180 A, Battery Current Max = 100 A, ABS = 240 A
- [ ] **Read back** App to Use = UART, Control Type = Current No Reverse
- [ ] Power cycle, then pull throttle and confirm smooth response from low trigger
- [ ] Backup Configs
- [ ] Enable RT Data Logging (`/Documents/logs`)
- [ ] Pack charged, cell spread checked in JK app
- [ ] Phone charged, VESC Tool installed, Bluetooth paired

## On-water numbers to know cold
| Reading | Action |
|---|---|
| ESC temp < 60 °C | Fine |
| ESC temp 60–70 °C | Ease off between attempts |
| ESC temp 70–80 °C | Head in |
| ESC temp 80 °C+ | Thermal rollback — power will fade |
| Pack ~46–48 V | Turn around; don't chase the 42 V cutoff |
| Power suddenly soft | Thermal rollback, not a fault — let it cool |

## Bench sign-off status
- [x] BMS commissioning, discharge/charge FETs verified
- [x] ESC boots, VESC Tool connects (USB + BLE)
- [x] FOC detection successful, values recorded
- [x] Limits set, written, and **verified by read-back**
- [x] Remote throttle functional (Current No Reverse)
- [x] Configs backed up to XML
- [x] Direction verified
- [x] Prop mounted with drive pin, loaded water test (hot tub, 66 min, 4.1 kW)
- [ ] **Reed switch kill system — NOT INSTALLED.** Parts on hand (MKA10110 reed switches, 20×3mm neodymium magnets). Currently the only protection is the 1000 ms UART timeout, which does **not** cover falling off while holding throttle. Riding with wrist float strap, away from people, until retrofitted. **Required before any beginner rides the board.**

---

## Next tuning steps
- Ride at 180 A / 100 A and log a full session; check whether thermals hold under repeated real water starts (harder duty cycle than the hot tub)
- If FET temps stay under 60 °C across a session, there is room above 180 A — the 75200 is rated 200 A
- Revisit ramping/expo only after riding at full power; current values are untested on the water
