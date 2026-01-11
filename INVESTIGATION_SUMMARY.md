# Investigation & Planning Summary

## Overview
The task is to enhance the `cal_trunkBranch.ics` file by adding auspicious/inauspicious markers (吉/凶) from the `good_bad_time.ics` file.

## File Analysis

### good_bad_time.ics
- **Purpose**: Daily time auspiciousness guide
- **Structure**: One event per day with 13 time slots per day
- **Date Format**: `DTSTART;VALUE=DATE:YYYYMMDD` (date-only)
- **Summary**: Space-separated list of time-ganzhi + marker pairs
  - Example: `丙子吉 丁丑吉 戊寅凶 己卯吉 庚辰凶 ...`
  - Each pair: 2-character ganzhi code + 1-character marker (吉=auspicious, 凶=inauspicious)
  - 13 pairs per line (matches ancient Chinese 12-hour system with overlap)

### cal_trunkBranch.ics  
- **Purpose**: Complete yearly calendar with full ganzhi (8-character destiny chart)
- **Structure**: One event per 2-hour time slot (13 events per day)
- **Timestamp Format**: `DTSTART:YYYYMMDDTHHMMSS` (full timestamp)
- **Summary**: `『HH时 DD日 MM月 YY年』` format
  - Example: `『丙子时 庚午日 丙子月 甲辰龙年』`
  - Contains 4 ganzhi elements: 时(hour), 日(day), 月(month), 年(year)
  - Wrapped in full-width brackets `『』`

## Linking Strategy

### 1. **Date Matching**
Both files use the same calendar dates:
- Extract YYYYMMDD from `DTSTART` (first 8 characters)
- Match to corresponding day in good_bad_time.ics

### 2. **Time Stem-Branch Extraction**
From cal_trunkBranch SUMMARY:
- Extract the 2 characters immediately before "时"
- Regex: `『(\S{2})时`
- Examples:
  - `『丙子时...』` → ganzhi = `丙子`
  - `『庚寅时...』` → ganzhi = `庚寅`
  - `『辛卯时...』` → ganzhi = `辛卯`

### 3. **Lookup Process**
```
date = "20250102"
time_ganzhi = "庚寅"
lookup[date][time_ganzhi] = "吉"
```

### 4. **Summary Enhancement**
Transform:
- From: `『丙子时 庚午日 丙子月 甲辰龙年』`
- To: `『吉 丙子时 庚午日 丙子月 甲辰龙年』`
  or `『凶 丙子时 庚午日 丙子月 甲辰龙年』`

## Verified Examples

### Example 1: January 1, 2025
**good_bad_time.ics (20250101)**:
```
SUMMARY:丙子吉 丁丑吉 戊寅凶 己卯吉 庚辰凶 辛巳凶 壬午吉 癸未凶 甲申吉 乙酉吉 丙戌凶 丁亥凶 戊子凶
```

**cal_trunkBranch.ics**:
```
DTSTART:20250101T230000
SUMMARY:『丙子时 庚午日 丙子月 甲辰龙年』
→ Enhanced: 『吉 丙子时 庚午日 丙子月 甲辰龙年』  (丙子吉)
```

### Example 2: January 2, 2025 - 03:00
**good_bad_time.ics (20250102)**:
```
SUMMARY:戊子凶 己丑凶 庚寅吉 辛卯吉 壬辰凶 癸巳吉 甲午凶 乙未凶 丙申吉 丁酉凶 戊戌吉 己亥吉 庚子吉
```

**cal_trunkBranch.ics**:
```
DTSTART:20250102T030000
SUMMARY:『庚寅时 辛未日 丙子月 甲辰龙年』
→ Enhanced: 『吉 庚寅时 辛未日 丙子月 甲辰龙年』  (庚寅吉)
```

### Example 3: January 2, 2025 - 05:00
```
DTSTART:20250102T050000
SUMMARY:『辛卯时 辛未日 丙子月 甲辰龙年』
→ Enhanced: 『吉 辛卯时 辛未日 丙子月 甲辰龙年』  (辛卯吉)
```

## Implementation Plan (Not Yet Implemented)

### Phase 1: Build Lookup Dictionary
- Parse good_bad_time.ics
- Extract DTSTART (date) and SUMMARY (time slots)
- For each time slot, parse: `ganzhi + marker`
- Store in dictionary: `lookup[date][ganzhi] = marker`

### Phase 2: Process cal_trunkBranch.ics
- Read cal_trunkBranch.ics line by line or event by event
- For each VEVENT:
  - Extract DTSTART to get date (YYYYMMDD)
  - Extract time ganzhi from SUMMARY using regex
  - Look up marker in dictionary
  - Construct new SUMMARY with marker prepended

### Phase 3: Write Enhanced File
- Replace all SUMMARY fields in cal_trunkBranch.ics
- Save to same file or backup + replace
- Verify file integrity (valid iCalendar format)

## Key Considerations

✅ **Confirmed Working Aspects**:
- Date matching via YYYYMMDD extraction
- Time ganzhi extraction via regex pattern `『(\S{2})时`
- Marker lookup (吉/凶 always present in good_bad summaries)
- Summary enhancement format

⚠️ **Edge Cases to Handle**:
1. **Midnight boundary**: Events at 23:00 on day N start at 23:00 but end after midnight
   - Check: Does DTSTART date or DTEND date get used? (Should be DTSTART)
2. **Missing dates**: What if a date in cal_trunkBranch has no entry in good_bad_time?
   - Solution: Log warning, skip enhancement for that event
3. **Character encoding**: UTF-8 for Chinese characters
   - Both files appear to be UTF-8 encoded ✓

## File Statistics

| Metric | good_bad_time.ics | cal_trunkBranch.ics |
|--------|------------------|-------------------|
| Total lines | 8,768 | 113,898 |
| Total events | ~673 | ~113,898 |
| Events per day | 1 | 13 |
| Date range | 2025-2027 | ~30 years (spanning multiple years) |
| Summary type | 13 time slots | Single time slot |

## Next Steps

Once approval is given, will implement:
1. Full parser for good_bad_time.ics with dictionary building
2. Iterative processor for cal_trunkBranch.ics
3. Safe file writing with backup
4. Validation and verification of results
