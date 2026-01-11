#!/usr/bin/env python3
"""
Analysis script to understand the structure of both calendar files
and plan the mapping strategy.
"""

import re
from collections import defaultdict
from datetime import datetime, timedelta

def parse_ics_file(filename):
    """Parse ICS file and extract events with timestamps and summaries"""
    events = []
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        # Split by BEGIN:VEVENT / END:VEVENT
        event_blocks = content.split('BEGIN:VEVENT')[1:]
        
        for block in event_blocks:
            if 'END:VEVENT' in block:
                block = block.split('END:VEVENT')[0]
                
                # Extract key fields
                dtstart_match = re.search(r'DTSTART[^:]*:([^\n]+)', block)
                dtend_match = re.search(r'DTEND[^:]*:([^\n]+)', block)
                summary_match = re.search(r'SUMMARY:([^\n]+)', block)
                
                if dtstart_match and summary_match:
                    dtstart = dtstart_match.group(1).strip()
                    dtend = dtend_match.group(1).strip() if dtend_match else None
                    summary = summary_match.group(1).strip()
                    
                    events.append({
                        'dtstart': dtstart,
                        'dtend': dtend,
                        'summary': summary
                    })
    
    return events

print("=" * 80)
print("ANALYZING GOOD_BAD_TIME.ICS")
print("=" * 80)

good_bad_events = parse_ics_file('good_bad_time.ics')
print(f"Total events: {len(good_bad_events)}")
print(f"\nFirst 5 events from good_bad_time.ics:")
for i, event in enumerate(good_bad_events[:5]):
    print(f"\nEvent {i+1}:")
    print(f"  DTSTART: {event['dtstart']}")
    print(f"  DTEND: {event['dtend']}")
    print(f"  SUMMARY: {event['summary']}")
    
    # Parse the summary to extract time slots
    summary = event['summary']
    time_slots = summary.split()
    print(f"  Parsed time slots: {len(time_slots)} items")
    for j, slot in enumerate(time_slots[:5]):
        print(f"    {j}: {slot}")

print("\n" + "=" * 80)
print("ANALYZING CAL_TRUNKBRANCH.ICS")
print("=" * 80)

trunk_events = parse_ics_file('cal_trunkBranch.ics')
print(f"Total events: {len(trunk_events)}")
print(f"\nFirst 10 events from cal_trunkBranch.ics:")
for i, event in enumerate(trunk_events[:10]):
    print(f"\nEvent {i+1}:")
    print(f"  DTSTART: {event['dtstart']}")
    print(f"  Summary snippet: {event['summary'][:50]}...")

print("\n" + "=" * 80)
print("KEY OBSERVATIONS")
print("=" * 80)

# Observation 1: Structure of summaries
print("\n1. good_bad_time.ics structure:")
print("   - Each VEVENT covers one DATE (e.g., DTSTART;VALUE=DATE:20250101)")
print("   - SUMMARY contains 13 time slots with ganzhi (干支) + auspicious/inauspicious marker (吉/凶)")
print("   - Format: 丙子吉 丁丑吉 戊寅凶 ... (13 x 2-hour slots)")

print("\n2. cal_trunkBranch.ics structure:")
print("   - Each VEVENT covers a specific time slot (2-hour period)")
print("   - DTSTART/DTEND are timestamps with times (DTSTART:20250101T010000)")
print("   - SUMMARY contains '『时 日 月 年』' format")
print("   - Needs to be enhanced with the 吉/凶 marker from good_bad_time.ics")

print("\n3. Mapping strategy:")
print("   - Match based on DATE from DTSTART")
print("   - Extract the 2-character ganzhi from LOCATION or SUMMARY (last element)")
print("   - Find corresponding entry in good_bad_time SUMMARY for that date")
print("   - Prefix the trunk branch SUMMARY with the 吉/凶 marker")

# Example: Let's trace through the first event
print("\n" + "=" * 80)
print("EXAMPLE MAPPING")
print("=" * 80)

trunk_event = trunk_events[0]
print(f"\nTrunk branch event (cal_trunkBranch.ics):")
print(f"  DTSTART: {trunk_event['dtstart']}")
print(f"  SUMMARY: {trunk_event['summary']}")
# Extract the time stem-branch from location or summary
location_match = re.search(r'甲辰 丙子 庚午 (\S+)$', trunk_event['summary'].replace('『', '').replace('』', '').strip())
if location_match:
    time_ganzhi = location_match.group(1)
    print(f"  Extracted time ganzhi: {time_ganzhi}")
    
    # Find corresponding date
    dtstart_date = trunk_event['dtstart'][:8]  # YYYYMMDD
    print(f"  Date: {dtstart_date}")
    
    # Find the corresponding good_bad event
    for good_bad_event in good_bad_events:
        if good_bad_event['dtstart'] == dtstart_date:
            print(f"\nMatching good_bad_time event:")
            print(f"  DATE: {good_bad_event['dtstart']}")
            print(f"  SUMMARY: {good_bad_event['summary']}")
            
            # Parse the summary to find the auspicious marker
            time_slots = good_bad_event['summary'].split()
            for slot in time_slots:
                if slot.startswith(time_ganzhi):
                    marker = '吉' if '吉' in slot else '凶'
                    print(f"  Found matching slot: {slot}")
                    print(f"  Marker to use: {marker}")
                    
                    new_summary = f"『{marker} {trunk_event['summary'][1:-1]}』"
                    print(f"  New SUMMARY: {new_summary}")
            break

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)
print("""
1. Parse good_bad_time.ics into a lookup dictionary:
   - Key: DATE (YYYYMMDD)
   - Value: Dictionary mapping ganzhi (2-char) → marker (吉/凶)

2. Iterate through cal_trunkBranch.ics events:
   - Extract date from DTSTART
   - Extract time ganzhi (last 2 characters from the 4-element ganzhi sequence)
   - Look up in the good_bad dictionary
   - Prepend marker to SUMMARY

3. Replace all SUMMARY fields in cal_trunkBranch.ics with enhanced versions
""")
