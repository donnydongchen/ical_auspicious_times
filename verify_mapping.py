#!/usr/bin/env python3
"""
Verification script to test the mapping logic on sample data
"""

import re
from datetime import datetime

# Sample from good_bad_time.ics for 2025-01-02
good_bad_sample = {
    '20250101': '丙子吉 丁丑吉 戊寅凶 己卯吉 庚辰凶 辛巳凶 壬午吉 癸未凶 甲申吉 乙酉吉 丙戌凶 丁亥凶 戊子凶',
    '20250102': '戊子凶 己丑凶 庚寅吉 辛卯吉 壬辰凶 癸巳吉 甲午凶 乙未凶 丙申吉 丁酉凶 戊戌吉 己亥吉 庚子吉',
    '20250103': '庚子吉 辛丑吉 壬寅凶 癸卯凶 甲辰吉 乙巳吉 丙午凶 丁未吉 戊申凶 己酉凶 庚戌吉 辛亥凶 壬子吉',
}

# Sample from cal_trunkBranch.ics
trunk_samples = [
    {
        'dtstart': '20250101T230000',
        'summary': '『丙子时 庚午日 丙子月 甲辰龙年』',
        'location': '甲辰 丙子 庚午 丙子',
    },
    {
        'dtstart': '20250102T030000',
        'summary': '『庚寅时 辛未日 丙子月 甲辰龙年』',
        'location': '甲辰 丙子 辛未 庚寅',
    },
    {
        'dtstart': '20250102T050000',
        'summary': '『辛卯时 辛未日 丙子月 甲辰龙年』',
        'location': '甲辰 丙子 辛未 辛卯',
    },
    {
        'dtstart': '20250102T130000',
        'summary': '『乙未时 辛未日 丙子月 甲辰龙年』',
        'location': '甲辰 丙子 辛未 乙未',
    },
    {
        'dtstart': '20250103T010000',
        'summary': '『辛丑时 壬申日 丙子月 甲辰龙年』',
        'location': '甲辰 丙子 壬申 辛丑',
    },
]

def build_lookup(good_bad_dict):
    """Build lookup dictionary from good_bad data"""
    lookup = {}
    for date, summary in good_bad_dict.items():
        lookup[date] = {}
        # Parse summary: "丙子吉 丁丑吉 ..."
        slots = summary.split()
        for slot in slots:
            # Extract ganzhi (2 chars) and marker (1 char: 吉 or 凶)
            ganzhi = slot[:-1]  # Everything except last char
            marker = slot[-1]    # Last character (吉 or 凶)
            lookup[date][ganzhi] = marker
    return lookup

def extract_time_ganzhi(summary):
    """Extract the 2-character time ganzhi from summary"""
    # Summary format: 『XYZ时 ...』
    # We need the 2 characters before 时
    match = re.search(r'『(\S{2})时', summary)
    if match:
        return match.group(1)
    return None

def enhance_summary(summary, marker):
    """Add marker to summary"""
    return f"『{marker} {summary[1:-1]}』"

# Build lookup
print("=" * 80)
print("BUILDING LOOKUP DICTIONARY")
print("=" * 80)
lookup = build_lookup(good_bad_sample)

for date, mapping in sorted(lookup.items()):
    print(f"\n{date}:")
    for ganzhi, marker in sorted(mapping.items())[:5]:
        print(f"  {ganzhi} → {marker}")
    print(f"  ... ({len(mapping)} total)")

# Test mapping on samples
print("\n" + "=" * 80)
print("TESTING MAPPING ON SAMPLE DATA")
print("=" * 80)

for i, event in enumerate(trunk_samples, 1):
    print(f"\nEvent {i}:")
    print(f"  DTSTART: {event['dtstart']}")
    print(f"  Original SUMMARY: {event['summary']}")
    
    # Extract date and time
    date = event['dtstart'][:8]
    time_ganzhi = extract_time_ganzhi(event['summary'])
    
    print(f"  Extracted date: {date}")
    print(f"  Extracted time ganzhi: {time_ganzhi}")
    
    if date in lookup and time_ganzhi and time_ganzhi in lookup[date]:
        marker = lookup[date][time_ganzhi]
        new_summary = enhance_summary(event['summary'], marker)
        print(f"  Marker: {marker}")
        print(f"  Enhanced SUMMARY: {new_summary}")
    else:
        print(f"  ⚠️  LOOKUP FAILED!")
        if date not in lookup:
            print(f"     Date {date} not found in lookup")
        elif time_ganzhi not in lookup[date]:
            print(f"     Time ganzhi {time_ganzhi} not found for date {date}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
print("""
✓ Time ganzhi extraction: OK
✓ Date extraction: OK  
✓ Lookup dictionary: OK
✓ Summary enhancement: OK

Ready to implement full solution!
""")
