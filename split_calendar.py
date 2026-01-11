#!/usr/bin/env python3
"""
Calendar Split Script
Split cal_trunkBranch_enhanced.ics into two separate files by auspiciousness
"""

import re
from pathlib import Path

INPUT_FILE = "cal_trunkBranch_enhanced.ics"
AUSPICIOUS_FILE = "cal_trunkBranch_auspicious.ics"
INAUSPICIOUS_FILE = "cal_trunkBranch_inauspicious.ics"

def progress_bar(current, total, width=50):
    """Simple progress bar"""
    if total == 0:
        return
    percent = current / total
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)
    print(f'\r[{bar}] {current}/{total} ({100*percent:.1f}%)', end='', flush=True)

def split_calendar():
    """Split calendar into auspicious and inauspicious files"""
    
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "Calendar Split Script".center(78) + "║")
    print("║" + "Splitting by auspiciousness markers (吉/凶)".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    print(f"[1/3] Reading {INPUT_FILE}...")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract header (everything before first VEVENT)
    header_match = re.search(r'(.*?)BEGIN:VEVENT', content, re.DOTALL)
    header = header_match.group(1) if header_match else ""
    
    # Extract footer (everything after last VEVENT)
    footer_match = re.search(r'END:VEVENT(.*)', content, re.DOTALL)
    footer = footer_match.group(1) if footer_match else ""
    
    # Split by VEVENT
    print("[2/3] Splitting events by auspiciousness...")
    events = content.split('BEGIN:VEVENT')[1:]
    
    auspicious_events = []
    inauspicious_events = []
    skipped = 0
    
    for idx, event in enumerate(events):
        progress_bar(idx + 1, len(events))
        
        # Extract SUMMARY line to check marker
        summary_match = re.search(r'SUMMARY:([^\n]+)', event)
        if not summary_match:
            skipped += 1
            continue
        
        summary = summary_match.group(1)
        
        # Classify by marker
        if summary.startswith('『吉'):
            auspicious_events.append(event)
        elif summary.startswith('『凶'):
            inauspicious_events.append(event)
        else:
            # Unenhanced event (no marker)
            skipped += 1
    
    print()
    print(f"\n✓ Split complete:")
    print(f"  Auspicious events (吉): {len(auspicious_events)}")
    print(f"  Inauspicious events (凶): {len(inauspicious_events)}")
    print(f"  Skipped (unenhanced): {skipped}")
    
    print(f"\n[3/3] Writing split files...")
    
    # Function to create complete ICS file
    def write_ics_file(filepath, events, calendar_name):
        # Update X-WR-CALNAME in header
        updated_header = re.sub(
            r'X-WR-CALNAME:[^\n]*',
            f'X-WR-CALNAME:{calendar_name}',
            header
        )
        
        # Build file content
        file_content = updated_header
        for event in events:
            file_content += f'BEGIN:VEVENT{event}'
        file_content += footer
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        # Verify line count
        line_count = len(file_content.split('\n'))
        event_count = len(events)
        
        return line_count, event_count
    
    # Write both files
    lines_auspicious, count_auspicious = write_ics_file(
        AUSPICIOUS_FILE, 
        auspicious_events,
        "Auspicious Times"
    )
    
    lines_inauspicious, count_inauspicious = write_ics_file(
        INAUSPICIOUS_FILE,
        inauspicious_events,
        "Inauspicious Times"
    )
    
    print("\n" + "="*80)
    print("SPLIT COMPLETE - SUMMARY REPORT")
    print("="*80)
    
    print(f"\n📊 Event Distribution:")
    print(f"  Total events processed: {len(events)}")
    print(f"  Auspicious (吉):        {count_auspicious}")
    print(f"  Inauspicious (凶):      {count_inauspicious}")
    print(f"  Skipped (unenhanced):   {skipped}")
    print(f"  ────────────────────────")
    print(f"  Total in output:        {count_auspicious + count_inauspicious}")
    
    print(f"\n📁 Output Files:")
    print(f"  {AUSPICIOUS_FILE}")
    print(f"    Events: {count_auspicious}")
    print(f"    Lines:  {lines_auspicious}")
    
    print(f"\n  {INAUSPICIOUS_FILE}")
    print(f"    Events: {count_inauspicious}")
    print(f"    Lines:  {lines_inauspicious}")
    
    print(f"\n✅ Files successfully created!")
    print("="*80)

if __name__ == "__main__":
    split_calendar()
