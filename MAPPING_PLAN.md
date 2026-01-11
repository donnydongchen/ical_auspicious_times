# Calendar File Mapping Analysis

## File Structures

### good_bad_time.ics
- **Total events**: ~673 events (one per day)
- **Date range**: DTSTART;VALUE=DATE:YYYYMMDD (date-only format)
- **Summary format**: Contains 13 time slots for a single day
  - Each slot: `干支` + `吉` or `凶`
  - Example: `丙子吉 丁丑吉 戊寅凶 己卯吉 庚辰凶 辛巳凶 壬午吉 癸未凶 甲申吉 乙酉吉 丙戌凶 丁亥凶 戊子凶`
  - 13 time slots per day (Chinese 12-hour system with 13 periods)

### cal_trunkBranch.ics
- **Total events**: ~113,898 events (multiple per day - one per 2-hour time slot)
- **Timestamp format**: DTSTART:YYYYMMDDTHHMMSS (with specific times)
- **Summary format**: `『time月 日 month year』`
  - Example: `『丙子时 庚午日 丙子月 甲辰龙年』`
  - Contains 4 ganzhi elements: 年(year), 月(month), 日(day), 时(hour/time)

## Mapping Strategy

### 1. **Lookup Dictionary Creation**
Build a dictionary from `good_bad_time.ics`:
```
{
  '20250101': {
    '丙子': '吉',    # Extract from "丙子吉"
    '丁丑': '吉',
    '戊寅': '凶',
    ...
  },
  '20250102': {
    ...
  }
}
```

### 2. **Time Stem-Branch Extraction**
From `cal_trunkBranch.ics` event:
- **Current SUMMARY**: `『丙子时 庚午日 丙子月 甲辰龙年』`
- **Extract time stem-branch** (时 = 2-character code): `丙子`
- **Extract date** from DTSTART: `20250101` (first 8 chars of `20250101T010000`)

### 3. **Lookup & Enhancement**
```
Date: 20250101
Time: 丙子
Lookup: good_bad_time['20250101']['丙子'] → '吉'
New SUMMARY: 『吉 丙子时 庚午日 丙子月 甲辰龙年』
```

## Implementation Plan

1. **Parse good_bad_time.ics**
   - Extract DTSTART (date) and SUMMARY (time slots)
   - Build lookup dictionary mapping (date, ganzhi) → (吉/凶)

2. **Parse cal_trunkBranch.ics**
   - For each event:
     - Extract DTSTART (to get date)
     - Extract time ganzhi from SUMMARY (extract 2-char code before "时")
     - Look up the auspicious/inauspicious marker
     - Prepend marker with space to existing SUMMARY

3. **Update cal_trunkBranch.ics**
   - Replace all SUMMARY lines with enhanced versions

## Example Trace

### Event from cal_trunkBranch.ics
```
DTSTART:20250101T230000
DTEND:20250101T005959
SUMMARY:『丙子时 庚午日 丙子月 甲辰龙年』
LOCATION:甲辰 丙子 庚午 丙子
```

### Corresponding good_bad_time.ics entry
```
DTSTART;VALUE=DATE:20250101
SUMMARY:丙子吉 丁丑吉 戊寅凶 ...
```

### Mapping
- Extract date: `20250101`
- Extract time: `丙子` (from "丙子时")
- Lookup in good_bad: `good_bad['20250101']['丙子']` = `吉`
- **Result**: `『吉 丙子时 庚午日 丙子月 甲辰龙年』`

## Key Observations

1. **13 time slots per day**: good_bad_time.ics uses 13 periods (ancient Chinese timekeeping)
2. **Direct stem-branch matching**: The 2-character codes in good_bad_time SUMMARY match exactly with the time element in cal_trunkBranch SUMMARY
3. **Date-based grouping**: All events for a single date in cal_trunkBranch map to one entry in good_bad_time
4. **Prefix format**: The marker should be placed inside the brackets, right after the opening bracket and space

## Edge Cases to Consider

1. **Multi-year coverage**: Both files span multiple years - ensure proper lookup
2. **Boundary times**: Events near midnight (23:00-01:00) - verify date handling
3. **Missing dates**: What if good_bad_time doesn't have an entry for a date in cal_trunkBranch?
4. **Encoding**: Ensure UTF-8 handling for Chinese characters (吉/凶)
