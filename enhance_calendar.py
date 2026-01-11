#!/usr/bin/env python3
"""
Calendar Enhancement Script
Enhance cal_trunkBranch.ics with auspiciousness markers from good_bad_time.ics
"""

import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Configuration
GOOD_BAD_FILE = "good_bad_time.ics"
TRUNK_FILE = "cal_trunkBranch.ics"
OUTPUT_FILE = "cal_trunkBranch_enhanced.ics"
LOG_FILE = "enhancement_log.txt"

# Global tracking
stats = {
    'total_events': 0,
    'enhanced_events': 0,
    'skipped_events': 0,
    'missing_lookups': 0,
    'samples': [],
    'warnings': []
}

def progress_bar(current, total, width=50):
    """Simple progress bar"""
    percent = current / total
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)
    print(f'\r[{bar}] {current}/{total} ({100*percent:.1f}%)', end='', flush=True)

def build_lookup_dictionary():
    """Build lookup dictionary from good_bad_time.ics"""
    lookup = defaultdict(dict)
    
    print("[1/3] Building lookup dictionary from good_bad_time.ics...")
    
    with open(GOOD_BAD_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by VEVENT
    events = content.split('BEGIN:VEVENT')[1:]
    
    for idx, event in enumerate(events):
        progress_bar(idx + 1, len(events))
        # Extract date
        date_match = re.search(r'DTSTART;VALUE=DATE:(\d{8})', event)
        if not date_match:
            continue
        
        date = date_match.group(1)
        
        # Extract summary with 13 time slots
        summary_match = re.search(r'SUMMARY:([^\n]+)', event)
        if not summary_match:
            continue
        
        summary = summary_match.group(1)
        
        # Parse each time slot: "ganzhi + marker"
        slots = summary.split()
        for slot in slots:
            if len(slot) >= 3:  # At least 2 chars ganzhi + 1 char marker
                ganzhi = slot[:-1]  # Everything except last char
                marker = slot[-1]    # Last char (吉 or 凶)
                lookup[date][ganzhi] = marker
    
    print(f"\n✓ Built lookup dictionary with {sum(len(v) for v in lookup.values())} entries\n")
    return lookup

def enhance_summary(summary, date, lookup):
    """
    Enhance a summary by prepending the auspiciousness marker
    Returns: (enhanced_summary, marker_found)
    """
    # Extract time ganzhi from summary: 『XX时
    match = re.search(r'『(\S{2})时', summary)
    if not match:
        return summary, False
    
    time_ganzhi = match.group(1)
    
    # Look up in dictionary
    if date in lookup and time_ganzhi in lookup[date]:
        marker = lookup[date][time_ganzhi]
        enhanced = f"『{marker} {summary[1:-1]}』"
        return enhanced, True
    
    return summary, False

def enhance_trunk_branch(lookup):
    """Enhance cal_trunkBranch.ics with markers"""
    print("[2/3] Enhancing cal_trunkBranch.ics...\n")
    
    with open(TRUNK_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Count total events for progress bar
    total_events = sum(1 for line in lines if 'BEGIN:VEVENT' in line)
    
    output_lines = []
    current_event = []
    event_count = 0
    
    for line in lines:
        if 'BEGIN:VEVENT' in line:
            current_event = [line]
            event_count += 1
            progress_bar(event_count, total_events)
        elif 'END:VEVENT' in line:
            current_event.append(line)
            
            # Process the event
            event_text = ''.join(current_event)
            enhanced_event = process_event(event_text, lookup)
            output_lines.append(enhanced_event)
            
            current_event = []
        else:
            current_event.append(line)

def process_event(event_text, lookup):
    """Process a single VEVENT block"""
    lines = event_text.split('\n')
    enhanced_lines = []
    
    # Extract date from DTSTART
    date_match = re.search(r'DTSTART:(\d{8})', event_text)
    date = date_match.group(1) if date_match else None
    
    # Extract original summary
    summary_line_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('SUMMARY:'):
            summary_line_idx = i
            break
    
    # Process lines
    for i, line in enumerate(lines):
        if i == summary_line_idx and date:
            summary = line.replace('SUMMARY:', '', 1)
            enhanced_summary, found = enhance_summary(summary, date, lookup)
            
            if found:
                enhanced_lines.append(f'SUMMARY:{enhanced_summary}')
                stats['enhanced_events'] += 1
                
                # Store sample
                if len(stats['samples']) < 5:
                    stats['samples'].append({
                        'date': date,
                        'before': f'SUMMARY:{summary}',
                        'after': f'SUMMARY:{enhanced_summary}'
                    })
            else:
                enhanced_lines.append(line)
                stats['skipped_events'] += 1
                
                if date:
                    match = re.search(r'『(\S{2})时', summary)
                    if match:
                        time_ganzhi = match.group(1)
                        warning = f"No marker found for {date}/{time_ganzhi}"
                        if warning not in stats['warnings']:
                            stats['warnings'].append(warning)
                        stats['missing_lookups'] += 1
        else:
            enhanced_lines.append(line)
    
    return '\n'.join(enhanced_lines)

def validate_output_file():
    """Validate the output file is valid ICS"""
    print("\nValidating output file...")
    
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'starts_with_BEGIN:VCALENDAR': content.startswith('BEGIN:VCALENDAR'),
        'ends_with_END:VCALENDAR': content.strip().endswith('END:VCALENDAR'),
        'has_VEVENT_blocks': 'BEGIN:VEVENT' in content and 'END:VEVENT' in content,
        'event_count_matches': content.count('BEGIN:VEVENT') == content.count('END:VEVENT'),
    }
    
    all_valid = all(checks.values())
    
    for check_name, result in checks.items():
        status = '✓' if result else '✗'
        print(f"  {status} {check_name}: {'PASS' if result else 'FAIL'}")
    
    return all_valid

def generate_report():
    """Generate and display completion report"""
    print("\n" + "="*80)
    print("ENHANCEMENT COMPLETE - SUMMARY REPORT")
    print("="*80)
    
    print(f"\n📊 Statistics:")
    print(f"  Total events processed:  {stats['total_events']:,}")
    print(f"  Events enhanced:         {stats['enhanced_events']:,} ({100*stats['enhanced_events']/max(stats['total_events'],1):.1f}%)")
    print(f"  Events skipped:          {stats['skipped_events']:,}")
    print(f"  Missing lookups:         {stats['missing_lookups']}")
    
    print(f"\n📁 Output:")
    print(f"  New file created:        {OUTPUT_FILE}")
    
    output_file_size = Path(OUTPUT_FILE).stat().st_size / (1024*1024)
    original_file_size = Path(TRUNK_FILE).stat().st_size / (1024*1024)
    print(f"  Original file size:      {original_file_size:.2f} MB")
    print(f"  Enhanced file size:      {output_file_size:.2f} MB")
    
    print(f"\n✅ Validation Results:")
    is_valid = validate_output_file()
    print(f"  Overall status:          {'VALID ✓' if is_valid else 'INVALID ✗'}")
    
    if stats['samples']:
        print(f"\n📝 Sample Transformations (first {len(stats['samples'])} events):")
        for i, sample in enumerate(stats['samples'], 1):
            print(f"\n  Sample {i} - Date: {sample['date']}")
            print(f"    Before: {sample['before'][:70]}{'...' if len(sample['before']) > 70 else ''}")
            print(f"    After:  {sample['after'][:70]}{'...' if len(sample['after']) > 70 else ''}")
    
    if stats['warnings'][:5]:
        print(f"\n⚠️  First 5 Warnings (total: {len(stats['warnings'])}):")
        for warning in stats['warnings'][:5]:
            print(f"    • {warning}")
    
    # Write log file
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("ENHANCEMENT LOG\n")
        f.write("="*80 + "\n\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Source file: {TRUNK_FILE}\n")
        f.write(f"Output file: {OUTPUT_FILE}\n")
        f.write(f"Lookup source: {GOOD_BAD_FILE}\n\n")
        
        f.write("STATISTICS:\n")
        f.write(f"  Total events: {stats['total_events']:,}\n")
        f.write(f"  Enhanced: {stats['enhanced_events']:,}\n")
        f.write(f"  Skipped: {stats['skipped_events']:,}\n")
        f.write(f"  Missing lookups: {stats['missing_lookups']}\n\n")
        
        f.write("WARNINGS:\n")
        for warning in stats['warnings']:
            f.write(f"  • {warning}\n")
        
        f.write("\n\nSAMPLES:\n")
        for i, sample in enumerate(stats['samples'], 1):
            f.write(f"\nSample {i}:\n")
            f.write(f"  Date: {sample['date']}\n")
            f.write(f"  {sample['before']}\n")
            f.write(f"  {sample['after']}\n")
    
    print(f"\n📋 Log file saved to:    {LOG_FILE}")
    print("\n" + "="*80)

def main():
    """Main execution"""
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "Calendar File Enhancement Script".center(78) + "║")
    print("║" + "Enhancing cal_trunkBranch.ics with auspiciousness markers".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    # Step 1: Build lookup
    lookup = build_lookup_dictionary()
    
    # Step 2: Enhance trunk branch
    enhance_trunk_branch(lookup)
    
    # Step 3: Generate report
    generate_report()

if __name__ == '__main__':
    main()
