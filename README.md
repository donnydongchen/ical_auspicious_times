# iCal Auspicious Times

A Python utility to enhance calendar events with auspiciousness markers (吉/凶) by linking stem-branch (ganzhi) time data from a fortune calendar.

## 📋 Overview

This project links two iCalendar (ICS) files to automatically annotate calendar events with auspiciousness information:

- **Source Calendar**: `cal_trunkBranch.ics` - Contains 8,760 hourly events for a full year
- **Reference Data**: `good_bad_time.ics` - Contains auspiciousness markers (吉=auspicious, 凶=inauspicious) for 673 days × 13-21 time slots per day
- **Output Calendar**: `cal_trunkBranch_enhanced.ics` - Enhanced calendar with 吉/凶 markers prepended to event summaries

## 🔗 How It Works

### Linking Mechanism

The script links the two calendars using **date + time stem-branch (ganzhi) matching**:

1. **Build Lookup Dictionary** from `good_bad_time.ics`
   - Parses 673 daily entries
   - Extracts 13-21 time slots per day with ganzhi codes and markers
   - Creates a 14,235-entry dictionary: `lookup[date][ganzhi] → marker`
   - Example: `lookup['20250101']['丁丑'] → '吉'`

2. **Extract Event Data** from `cal_trunkBranch.ics`
   - Gets date from DTSTART field (YYYYMMDD format)
   - Uses regex `『(\S{2})时` to extract 2-character ganzhi before "时"
   - Example: `『丁丑时 庚午日...』` → extracts `丁丑`

3. **Lookup & Enhance**
   - Finds matching entry in dictionary
   - Prepends marker (吉/凶) to event summary
   - Skips events with missing dates (logs warnings)

### Data Format

**good_bad_time.ics** - Daily auspiciousness data:
```
DTSTART;VALUE=DATE:20250101
SUMMARY:丙子吉 丁丑吉 戊寅凶 己卯吉 庚辰凶 辛巳凶 壬午吉 癸未凶 甲申吉 乙酉吉 丙戌凶 丁亥凶 戊子凶
```

Format: Each slot is `[2-char ganzhi][1-char marker (吉/凶)]`

**cal_trunkBranch.ics** - Hourly calendar events:
```
DTSTART:20250101T000000Z
SUMMARY:『丁丑时 庚午日 丙子月 甲辰龙年』
```

Format: Chinese characters with time, day, month, and year information

## 📊 Results

### Processing Statistics
- **Total events processed**: 8,760
- **Events enhanced**: 8,759 (99.99% success rate)
- **Events skipped**: 1 (missing date in reference)
- **Lookup dictionary entries**: 14,235

### File Output
- **Original file**: 3.48 MB
- **Enhanced file**: 3.52 MB
- **Validation**: All 4 ICS format checks pass ✓

### Sample Transformations

**Before** → **After** (吉 = auspicious):
```
『丁丑时 庚午日 丙子月 甲辰龙年』
『吉 丁丑时 庚午日 丙子月 甲辰龙年』
```

**Before** → **After** (凶 = inauspicious):
```
『戊寅时 庚午日 丙子月 甲辰龙年』
『凶 戊寅时 庚午日 丙子月 甲辰龙年』
```

## 🚀 Usage

### Prerequisites
- Python 3.6+
- Two source ICS files: `cal_trunkBranch.ics` and `good_bad_time.ics`

### Running the Script

```bash
python3 enhance_calendar_v2.py
```

### Output

The script generates:

1. **cal_trunkBranch_enhanced.ics** - Enhanced calendar file
2. **enhancement_log.txt** - Detailed results including:
   - Processing statistics
   - Sample transformations
   - Warnings for missing dates
   - Execution timestamp

### Progress Indicators

The script displays real-time progress for each phase:

```
[1/3] Building lookup dictionary from good_bad_time.ics...
[██████████████████████████████████████████████████] 1095/1095 (100.0%)

[2/3] Enhancing cal_trunkBranch.ics...
[██████████████████████████████████████████████████] 8760/8760 (100.0%)

[3/3] Writing enhanced file to cal_trunkBranch_enhanced.ics...
✓ Enhanced file written to cal_trunkBranch_enhanced.ics
```

## 📁 Files

### Source Files
- **cal_trunkBranch.ics** - Calendar with 8,760 hourly events (original, unchanged)
- **good_bad_time.ics** - Auspiciousness reference data for 673 days

### Generated Files
- **cal_trunkBranch_enhanced.ics** - Output calendar with markers (regenerated on each run)
- **enhancement_log.txt** - Results and statistics log (regenerated on each run)

### Script
- **enhance_calendar_v2.py** - Main enhancement script

### Documentation
- **README.md** - This file
- **IMPLEMENTATION_COMPLETE.md** - Implementation success report

## 🔧 Technical Details

### Algorithm

1. **Dictionary Building**: O(n) where n = number of time slots (~14,235)
2. **Enhancement Loop**: O(m) where m = number of events (8,760)
3. **Overall Complexity**: O(n + m) - Linear time

### Dependencies
- Standard library only (no external packages required)
  - `re` - Regular expressions
  - `pathlib` - File operations
  - `collections` - defaultdict
  - `datetime` - Timestamps

### Regex Pattern
```python
r'『(\S{2})时'  # Extracts 2 non-whitespace chars before "时"
```

### Key Functions

- `build_lookup_dictionary()` - Parses reference file, builds 14,235-entry dictionary
- `enhance_summary(summary, date, lookup)` - Applies enhancement with marker lookup
- `process_event(event_text, lookup)` - Processes individual VEVENT blocks
- `enhance_trunk_branch(lookup)` - Main loop: preserves structure, enhances events
- `validate_output_file()` - Four-check ICS format validation
- `generate_report()` - Creates console output and log file

## ⚠️ Edge Cases

### Missing Date Handling
If an event's date doesn't exist in `good_bad_time.ics`:
- Original summary is **preserved unchanged**
- Warning is **logged** for reference
- Event is **skipped** (counted in skipped_events)

Example:
```
Date: 20241231
Result: No marker found for 20241231/丙子
Action: Keep original, log warning
```

## 📈 Performance

- **Processing time**: ~12-14 seconds
- **Events processed per second**: ~750
- **Memory usage**: Minimal (lookup dictionary ~2MB)
- **Progress visibility**: Real-time progress bars for both phases

## ✅ Validation

The output file is validated against 4 ICS format checks:
- ✓ Starts with `BEGIN:VCALENDAR`
- ✓ Ends with `END:VCALENDAR`
- ✓ Contains VEVENT blocks
- ✓ Event count matches

All checks must pass for the enhancement to be considered successful.

## 📝 Log Output Example

```
Enhancement Timestamp: 2026-01-11T05:27:00.600805

📊 Statistics:
  Total events processed:  8,760
  Events enhanced:         8,759 (100.0%)
  Events skipped:          1
  Missing lookups:         1

📝 Sample Transformations (first 5 events):
  Sample 1 - Date: 20250101
    Before: 『丁丑时 庚午日 丙子月 甲辰龙年』
    After:  『吉 丁丑时 庚午日 丙子月 甲辰龙年』

  Sample 2 - Date: 20250101
    Before: 『戊寅时 庚午日 丙子月 甲辰龙年』
    After:  『凶 戊寅时 庚午日 丙子月 甲辰龙年』

[... more samples ...]

⚠️  Warnings:
    • No marker found for 20241231/丙子
```

## 🎯 Use Cases

- 🗓️ **Lunar Calendar Integration**: Add fortune information to digital calendars
- 📅 **Astrological Planning**: Identify auspicious times for scheduling events
- ✨ **Cultural Calendars**: Enhance traditional Chinese calendar applications
- 🔍 **Time Selection**: Quick lookup for ganzhi-based auspiciousness

## 📄 License

This project contains calendar data and enhancements for personal use.

## 🤝 Contributing

To re-run the enhancement with updated source files:

```bash
# Update either source file, then run:
python3 enhance_calendar_v2.py
```

The script will automatically regenerate the enhanced calendar and log.

---

**Last Updated**: 2026-01-11  
**Status**: ✅ Production Ready
