# Quick Reference Guide

## The Task
Enhance `cal_trunkBranch.ics` summaries by adding auspiciousness markers (吉/凶) from `good_bad_time.ics`

## The Files
```
good_bad_time.ics          cal_trunkBranch.ics
───────────────────        ──────────────────
~673 events (daily)        ~113,898 events (every 2 hours)
13 time slots/day          13 events/day
1 line per day             ~6 lines per day (per VEVENT)
```

## The Linking
```
Both files use YYYYMMDD dates
Both files reference "time stem-branch" (e.g., 丙子, 庚寅, 辛卯)
good_bad_time tells you: 丙子 = 吉 or 凶
cal_trunkBranch asks: what's my 丙子 classification?
```

## Quick Example
```
Input (cal_trunkBranch):
  Date: 20250101
  Time: 丙子
  Summary: 『丙子时 庚午日 丙子月 甲辰龙年』

Lookup (good_bad_time):
  20250101 entry: "丙子吉 ..."
  Found: 丙子 = 吉

Output (enhanced cal_trunkBranch):
  『吉 丙子时 庚午日 丙子月 甲辰龙年』
```

## The Algorithm (Pseudo-code)

### Step 1: Build Dictionary
```
dictionary = {}
for each day in good_bad_time:
    date = extract_date(event)
    summary_line = extract_summary(event)
    for each_timeslot in summary_line.split():
        ganzhi = timeslot[0:2]     # First 2 chars
        marker = timeslot[2]        # Last 1 char (吉 or 凶)
        dictionary[date][ganzhi] = marker
```

### Step 2: Enhance cal_trunkBranch
```
for each event in cal_trunkBranch:
    date = extract_date(event)
    time_ganzhi = extract_time(event.summary)
    marker = dictionary[date][time_ganzhi]
    new_summary = insert_marker_in_summary(event.summary, marker)
    update event.summary = new_summary
```

## Extraction Functions

### Extract Date
```python
date = dtstart[:8]  # "20250101T230000" → "20250101"
```

### Extract Time Ganzhi
```python
import re
match = re.search(r'『(\S{2})时', summary)
time_ganzhi = match.group(1)  # "『丙子时..." → "丙子"
```

### Insert Marker
```python
marker = "吉"  # or "凶"
new_summary = f"『{marker} {original[1:-1]}』"
# "『丙子时...』" → "『吉 丙子时...』"
```

## File Format Patterns

### good_bad_time.ics Pattern
```
DTSTART;VALUE=DATE:20250101
SUMMARY:丙子吉 丁丑吉 戊寅凶 己卯吉 庚辰凶 辛巳凶 壬午吉 癸未凶 甲申吉 乙酉吉 丙戌凶 丁亥凶 戊子凶
```
- Note: VALUE=DATE (no time)
- 13 slots per line (space-separated)

### cal_trunkBranch.ics Pattern (Before)
```
DTSTART:20250101T230000
SUMMARY:『丙子时 庚午日 丙子月 甲辰龙年』
```
- Note: Full timestamp with time
- Full-width brackets 『』
- 4 ganzhi elements

### cal_trunkBranch.ics Pattern (After)
```
DTSTART:20250101T230000
SUMMARY:『吉 丙子时 庚午日 丙子月 甲辰龙年』
```
- Marker inserted after opening bracket
- Everything else unchanged

## Validation Checklist

- [ ] Dictionary built with all dates
- [ ] All date keys in format YYYYMMDD
- [ ] All ganzhi codes are 2 characters
- [ ] All markers are either 吉 or 凶
- [ ] Enhanced summaries still have 4 ganzhi elements
- [ ] Brackets remain 『』 (full-width)
- [ ] No data loss
- [ ] File remains valid ICS format

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Lookup fails | Date not in good_bad | Log & skip enhancement |
| Ganzhi mismatch | Wrong extraction | Check regex pattern |
| Wrong marker | Parse error | Verify slot format |
| Corrupt file | Write error | Backup original first |
| Wrong encoding | UTF-8 issue | Ensure UTF-8 throughout |

## Performance Notes

- Dictionary build: O(n) where n ≈ 8,749
- Enhancement loop: O(m) where m ≈ 113,898
- Total: O(n + m) ≈ O(122,647)
- Expected runtime: < 1 second
- Memory usage: < 1 MB

## Implementation Hints

1. **Parser Choice**: Use regex or ICS parser library
2. **Dictionary Type**: Python dict, JavaScript object, etc.
3. **File I/O**: Read entire file → process → write
4. **Backup**: Save original before overwriting
5. **Validation**: Verify ICS format after modification

## Test Cases (Already Verified)

✓ Test 1: 20250101 丙子 → 吉  
✓ Test 2: 20250102 庚寅 → 吉  
✓ Test 3: 20250102 辛卯 → 吉  
✓ Test 4: 20250101 戊寅 → 凶  

All tested successfully with sample data!

---

**Ready to implement?**  
All investigation and planning is complete. The solution is well-understood and ready for coding.
