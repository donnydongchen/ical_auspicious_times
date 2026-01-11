# Visual Mapping Diagram

## File Structure Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    good_bad_time.ics                            │
│  (Daily auspiciousness guide - 673 events, 1 per day)           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  DTSTART;VALUE=DATE:20250101                                    │
│  SUMMARY: 丙子吉 丁丑吉 戊寅凶 己卯吉 庚辰凶 辛巳凶 ...        │
│           [13 time slots with markers]                          │
│                                                                   │
│  DTSTART;VALUE=DATE:20250102                                    │
│  SUMMARY: 戊子凶 己丑凶 庚寅吉 辛卯吉 壬辰凶 癸巳吉 ...        │
│           [13 time slots with markers]                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    BUILD LOOKUP DICTIONARY
                            ↓
     ┌──────────────────────────────────────────┐
     │ lookup = {                               │
     │   "20250101": {                           │
     │     "丙子": "吉",  "丁丑": "吉",        │
     │     "戊寅": "凶",  "己卯": "吉",        │
     │     ...                                  │
     │   },                                     │
     │   "20250102": {                           │
     │     "戊子": "凶",  "己丑": "凶",        │
     │     "庚寅": "吉",  "辛卯": "吉",        │
     │     ...                                  │
     │   },                                     │
     │   ...                                    │
     │ }                                        │
     └──────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    cal_trunkBranch.ics                           │
│  (Detailed calendar - 113,898 events, 13 per day)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  For each VEVENT:                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ DTSTART:20250101T230000 ──────────┐                      │   │
│  │ SUMMARY:『丙子时 庚午日 丙子月 甲辰龙年』 ─────┐        │   │
│  │                                    │                  │        │
│  │ Extract:                           │                  │        │
│  │  • Date: 20250101 (from DTSTART) ──┤                  │        │
│  │  • Time: 丙子 (from SUMMARY)  ─────┤                  │        │
│  │                                    │                  │        │
│  │ Lookup: lookup["20250101"]["丙子"] → "吉"             │        │
│  │                                         │              │        │
│  │ Result: 『吉 丙子时 庚午日 丙子月 甲辰龙年』◄───────┤        │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ DTSTART:20250102T030000                                  │   │
│  │ SUMMARY:『庚寅时 辛未日 丙子月 甲辰龙年』             │   │
│  │ Date: 20250102, Time: 庚寅                              │   │
│  │ Lookup: lookup["20250102"]["庚寅"] → "吉"              │   │
│  │ Result: 『吉 庚寅时 辛未日 丙子月 甲辰龙年』          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ... (repeat for all 113,898 events)                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Parsing Logic Flow

```
┌────────────────────┐
│  Parse good_bad_   │
│  time.ics          │
└────────┬───────────┘
         │
         ↓
┌────────────────────────────────────────────┐
│  For each line with "DTSTART;VALUE=DATE"   │
│  Extract: date = YYYYMMDD                  │
└────────┬───────────────────────────────────┘
         │
         ↓
┌────────────────────────────────────────────┐
│  For same event, extract SUMMARY           │
│  Split by spaces                           │
│  For each token: ganzhi + marker           │
│    ganzhi = token[:-1]  (all but last)     │
│    marker = token[-1]   (last char)        │
│    lookup[date][ganzhi] = marker           │
└────────┬───────────────────────────────────┘
         │
         ↓
┌────────────────────────────────────────────┐
│  Complete Lookup Dictionary Built          │
│  Ready to process cal_trunkBranch.ics      │
└────────┬───────────────────────────────────┘
         │
         ↓
┌────────────────────────────────────────────┐
│  Parse cal_trunkBranch.ics                 │
│  For each VEVENT block:                    │
│    1. Extract DTSTART                      │
│    2. Extract date = first 8 chars         │
│    3. Extract SUMMARY line                 │
│    4. Regex: 『(\S{2})时' → time_ganzhi   │
│    5. Lookup: lookup[date][time_ganzhi]   │
│    6. If found, prepend marker to summary  │
│    7. Replace SUMMARY in event             │
└────────┬───────────────────────────────────┘
         │
         ↓
┌────────────────────────────────────────────┐
│  Write enhanced cal_trunkBranch.ics        │
│  All SUMMARY fields now include marker     │
└────────────────────────────────────────────┘
```

## Data Format Examples

### Input: good_bad_time.ics Event
```
BEGIN:VEVENT
DTSTAMP:20260105T015232Z
UID:4f20e2fd-ad30-4b75-8064-6128c1619855
DTSTART;VALUE=DATE:20250101
DTEND;VALUE=DATE:20250102
STATUS:CONFIRMED
SUMMARY:丙子吉 丁丑吉 戊寅凶 己卯吉 庚辰凶 辛巳凶 壬午吉 癸未凶 甲申吉 乙酉吉 丙戌凶 丁亥凶 戊子凶
END:VEVENT
```

Parse flow:
```
DTSTART value: 20250101 → date = "20250101"
SUMMARY value: "丙子吉 丁丑吉 戊寅凶 ..."
Split: ["丙子吉", "丁丑吉", "戊寅凶", ...]

For "丙子吉":
  ganzhi = "丙子吉"[:-1] = "丙子"
  marker = "丙子吉"[-1] = "吉"
  lookup["20250101"]["丙子"] = "吉"

For "戊寅凶":
  ganzhi = "戊寅凶"[:-1] = "戊寅"
  marker = "戊寅凶"[-1] = "凶"
  lookup["20250101"]["戊寅"] = "凶"

... and so on for all 13 slots
```

### Input: cal_trunkBranch.ics Event (BEFORE)
```
BEGIN:VEVENT
DTSTART:20250101T230000
DTEND:20250101T005959
UID:20241231T230001_ganzhi_1@YangH9
CREATED:20241231T230001
LAST-MODIFIED:20251209T204916
SUMMARY:『丙子时 庚午日 丙子月 甲辰龙年』
LOCATION:甲辰 丙子 庚午 丙子
DESCRIPTION:甲辰龙年 丙子月 庚午日 丙子时\n甲辰 丙子 庚午 丙子\n\n更新时间：2025-12-09
STATUS:CONFIRMED
TRANSP:TRANSPARENT
SEQUENCE:1
END:VEVENT
```

Transformation:
```
DTSTART: 20250101T230000
  → Extract date: "20250101"

SUMMARY: 『丙子时 庚午日 丙子月 甲辰龙年』
  → Regex match: 『(\S{2})时
  → time_ganzhi = "丙子"

Lookup: lookup["20250101"]["丙子"] = "吉"

Enhancement:
  Original: 『丙子时 庚午日 丙子月 甲辰龙年』
  Enhanced: 『吉 丙子时 庚午日 丙子月 甲辰龙年』
```

### Output: cal_trunkBranch.ics Event (AFTER)
```
BEGIN:VEVENT
DTSTART:20250101T230000
DTEND:20250101T005959
UID:20241231T230001_ganzhi_1@YangH9
CREATED:20241231T230001
LAST-MODIFIED:20251209T204916
SUMMARY:『吉 丙子时 庚午日 丙子月 甲辰龙年』
LOCATION:甲辰 丙子 庚午 丙子
DESCRIPTION:甲辰龙年 丙子月 庚午日 丙子时\n甲辰 丙子 庚午 丙子\n\n更新时间：2025-12-09
STATUS:CONFIRMED
TRANSP:TRANSPARENT
SEQUENCE:1
END:VEVENT
```

## Mapping Summary Table

| Date | Time (Ganzhi) | From good_bad_time | Enhanced Summary |
|------|---------------|-------------------|------------------|
| 20250101 | 丙子 | 吉 | 『吉 丙子时 庚午日 丙子月 甲辰龙年』 |
| 20250101 | 丁丑 | 吉 | 『吉 丁丑时 庚午日 丙子月 甲辰龙年』 |
| 20250101 | 戊寅 | 凶 | 『凶 戊寅时 庚午日 丙子月 甲辰龙年』 |
| 20250102 | 庚寅 | 吉 | 『吉 庚寅时 辛未日 丙子月 甲辰龙年』 |
| 20250102 | 辛卯 | 吉 | 『吉 辛卯时 辛未日 丙子月 甲辰龙年』 |
| 20250103 | 甲辰 | 吉 | 『吉 甲辰时 壬申日 丙子月 甲辰龙年』 |

## Processing Statistics

- **Dictionary build**: Parse ~673 events × 13 slots = ~8,749 entries
- **Enhancement processing**: Scan ~113,898 events, look up each in dictionary
- **Hit rate**: Should be close to 100% (all dates in trunk should have entries in good_bad)
- **Processing time**: Expected < 1 second for entire operation
- **File size**: No change (replacement, not addition)
