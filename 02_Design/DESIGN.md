# Design & Iconography Reference — Berlin S-Bahn / U-Bahn

Research basis for the widget's visual language (system marks, line badge colors, departure display conventions).

## 1. System marks (the two round symbols)

| Mark | Design | Colors |
|---|---|---|
| **S-Bahn** | Circle with a white **"S"**, designed 1929/30 by Fritz Rosen for the Deutsche Reichsbahn; standardized across Germany since 1930. "S" = *Stadtschnellbahn*. | Green circle `#008D4F` (VBB official), white letter |
| **U-Bahn** | Blue circle with a white **"U"**; the "U" prefix was officially adopted in 1984 to distinguish U-Bahn from S-Bahn. | Blue circle `#0066AD` (VBB official), white letter |

Both are perfect circles with a bold sans-serif white letter centered — easy to recreate as inline SVG at any size.

## 2. Line badges (Liniensignets)

- **Shape:** rounded-corner square in the line's color with the line number in white bold sans-serif (e.g. `U8`, `S41`).
- **Font:** official icons are set in **FF Transit** (TransitLinie-S / TransitLinie-U). Free lookalikes: Barlow SemiBold, Roboto Condensed Bold, Arial Bold.
- **Text color exception:** on yellow badges (U4) use dark text `#191919`; everything else white.

## 3. Official VBB line colors (RGB)

Source: VBB *Handbuch VBB-Richtlinien Fahrgastinformation* (May 2022), "Farben Liniensignets".

### U-Bahn

| Line | Hex | Note | Line | Hex | Note |
|---|---|---|---|---|---|
| U1 | `#7DAD4C` | green | U6 | `#8C6DAB` | purple |
| U2 | `#DA421E` | red | U7 | `#009BD5` | light blue |
| U3 | `#16683D` | dark green | U8 | `#224F86` | dark blue |
| U4 | `#F0D722` | yellow — dark text `#191919` | U9 | `#F3791D` | orange |
| U5 | `#7E5330` | brown | generic U | `#0066AD` | |
| U12/U15 | `#7DAD4C` | former | U55 | `#7E5330` | former |

### S-Bahn

| Line | Hex | Note | Line | Hex | Note |
|---|---|---|---|---|---|
| S1 | `#DA6BA2` | pink | S5 | `#EB7405` | orange |
| S2/S25/S26 | `#007734` | green | S7/S75 | `#816DA6` | violet |
| S3 | `#0066AD` | blue | S8/S85 | `#66AA22` | yellow-green |
| S41 | `#AD5937` | copper, clockwise Ring | S9 | `#992746` | burgundy |
| S42 | `#CB6418` | orange-brown, counter-clockwise Ring | generic S | `#008D4F` | |
| S45/S46/S47 | `#CD9C53` | ochre | | | |

The generic system colors (`#008D4F` S, `#0066AD` U) match the round marks, so the two station sections can be keyed to them.

## 4. Station departure display conventions

### S-Bahn platform displays (DFA)

- Line badge (colored squircle) + destination in bold + **minutes until departure** as a large number.
- Trapezoid symbols below the minutes indicate train length (number of cars).
- Some boards show principal intermediate stops; a bold ticker at the bottom carries construction/disruption info.

### U-Bahn platform displays (BVG DAISY, 899 displays network-wide)

- Two-line LED displays showing the next departures per direction.
- 2024 redesign: countdown as **`3'`** — "in … min" replaced by an apostrophe after the number.
- Imminent departure is signaled by **blinking the destination text**; the row then disappears and the next departure slides up.
- Icons indicate barrier-free access and short trains (*Kurzzug*).
- Bottom row can show scrolling special messages (disruptions, construction).

## 5. Typography

- Official: **FF Transit** (paid, by Erik Spiekermann's group) — humanist sans designed for transit signage.
- Open alternatives with the same flavor: Barlow, Roboto Condensed, Inter.
- Historical S-Bahn station-name signage used Tannenberg/Reichsbahnschrift (blackletter) — decorative heritage, not suitable for a departures board.

## Sources

- S-Bahn Museum — Symbols of the S-Bahn: https://s-bahn-museum.de/en/100-years-of-the-berlin-s-bahn/found-objects/symbols-of-the-s-bahn
- Berliner Zeitung — The story behind the S-Bahn logo: https://www.berliner-zeitung.de/en/the-story-behind-that-white-s-on-a-green-background-li.147825
- Wikipedia — Module:Adjacent stations/Berlin U-Bahn and /Berlin S-Bahn (official VBB RGB specs)
- Wikimedia Commons — Template:Berlin transit icons (FF Transit origin of badge icons)
- Wikipedia (de) — Dynamisches Auskunfts- und Informationssystem (DAISY): display behavior, `3'` convention, blinking
- S-Bahn Berlin — Information at the train station: https://sbahn.berlin/en/plan-a-journey/practical-help-on-the-way/digital-information-options/information-at-the-train-station/
