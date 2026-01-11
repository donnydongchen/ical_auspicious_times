#!/usr/bin/env python3
"""
Calendar Enhancement Script (Extended)
Enhance cal_trunkBranch.ics with:
1. Auspiciousness markers from good_bad_time.ics
2. Pengzu taboos from pengzu_100_taboos.ics
Then split into auspicious and inauspicious files
"""

import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Configuration
GOOD_BAD_FILE = "good_bad_time.ics"
PENGZU_FILE = "pengzu_100_taboos.ics"
TRUNK_FILE = "cal_trunkBranch.ics"
ENHANCED_FILE = "cal_trunkBranch_enhanced.ics"
AUSPICIOUS_FILE = "cal_trunkBranch_auspicious.ics"
INAUSPICIOUS_FILE = "cal_trunkBranch_inauspicious.ics"
LOG_FILE = "enhancement_log.txt"

# Global tracking
stats = {
    'total_events': 0,
    'enhanced_events': 0,
    'taboo_added': 0,
    'skipped_events': 0,
    'missing_lookups': 0,
    'samples': [],
    'warnings': []
}

def progress_bar(current, total, width=50):
    """Simple progress bar"""
    if total == 0:
        return
    percent = current / total
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)
    print(f'\r[{bar}] {current}/{total} ({100*percent:.1f}%)', end='', flush=True)

def build_lookup_dictionary():
    """Build lookup dictionary from good_bad_time.ics"""
    lookup = defaultdict(dict)
    
    print("[1/5] Building lookup dictionary from good_bad_time.ics...")
    
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

def build_taboo_dictionary():
    """Build lookup dictionary from pengzu_100_taboos.ics"""
    taboo_lookup = defaultdict(list)
    
    print("[2/5] Building taboo lookup from pengzu_100_taboos.ics...")
    
    with open(PENGZU_FILE, 'r', encoding='utf-8') as f:
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
        
        # Extract summary with taboos
        summary_match = re.search(r'SUMMARY:([^\n]+)', event)
        if not summary_match:
            continue
        
        summary = summary_match.group(1)
        
        # Parse taboos separated by comma
        # Format: "庚不经络 织机虚张,午不苫盖 屋主更张"
        # Extract stem character (first char) and taboo text
        taboo_pairs = summary.split(',')
        for taboo_pair in taboo_pairs:
            taboo_pair = taboo_pair.strip()
            if not taboo_pair:
                continue
            
            # Extract stem character (first character of the pair)
            stem = taboo_pair[0]  # e.g., '庚' from '庚不经络 织机虚张'
            taboo_lookup[date].append((stem, taboo_pair))
    
    print(f"\n✓ Built taboo dictionary with {sum(len(v) for v in taboo_lookup.values())} taboo entries\n")
    return taboo_lookup

def enhance_summary(summary, date, marker_lookup, taboo_lookup):
    """Enhance a summary with marker and taboos
    
    Format: 『{marker} [{taboo}] {original_content}』
    """
    # Extract time ganzhi from summary: 『XX时
    match = re.search(r'『(\S{2})时', summary)
    if not match:
        return summary, False, False
    
    time_ganzhi = match.group(1)
    time_stem = time_ganzhi[0]  # First character only (e.g., '庚' from '庚辰')
    
    enhanced = summary
    marker_found = False
    taboo_found = False
    
    # Look up marker
    marker = None
    if date in marker_lookup and time_ganzhi in marker_lookup[date]:
        marker = marker_lookup[date][time_ganzhi]
        marker_found = True
    
    # Look up taboos for this date and stem
    taboos = []
    if date in taboo_lookup:
        for stem, taboo_text in taboo_lookup[date]:
            if stem == time_stem:
                taboos.append(taboo_text)
                taboo_found = True
    
    # Build enhanced summary
    if marker_found or taboo_found:
        # Start building the enhanced summary
        content = summary[1:-1]  # Remove 『 and 』
        
        # Build the new content with marker and taboos
        parts = []
        if marker:
            parts.append(marker)
        
        for taboo in taboos:
            parts.append(f"[{taboo}]")
        
        enhanced = f"『{' '.join(parts)} {content}』"
        
        return enhanced, marker_found, taboo_found
    
    return summary, False, False

def process_event(event_text, marker_lookup, taboo_lookup):
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
            enhanced_summary, marker_found, taboo_found = enhance_summary(
                summary, date, marker_lookup, taboo_lookup
            )
            
            if marker_found or taboo_found:
                enhanced_lines.append(f'SUMMARY:{enhanced_summary}')
                stats['enhanced_events'] += 1
                if taboo_found:
                    stats['taboo_added'] += 1
                
                # Store sample
                if len(stats['samples']) < 5:
                    stats['samples'].append({
                        'date': date,
                        'before': f'SUMMARY:{summary.strip()}',
                        'after': f'SUMMARY:{enhanced_summary}'
                    })
            else:
                enhanced_lines.append(line)
                stats['skipped_events'] += 1
                
                if date:
                    match = re.search(r'『(\S{2})时', summary)
                    if match:
                        time_ganzhi = match.group(1)
                        warning = f"No enhancement found for {date}/{time_ganzhi}"
                        if warning not in stats['warnings']:
                            stats['warnings'].append(warning)
                        stats['missing_lookups'] += 1
        else:
            enhanced_lines.append(line)
    
    return '\n'.join(enhanced_lines)

def enhance_trunk_branch(marker_lookup, taboo_lookup):
    """Enhance cal_trunkBranch.ics with markers and taboos"""
    print("[3/5] Enhancing cal_trunkBranch.ics...\n")
    
    with open(TRUNK_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count total events for progress bar
    total_events = content.count('BEGIN:VEVENT')
    
    # Extract header (everything before first VEVENT)
    header_match = re.search(r'(.*?)BEGIN:VEVENT', content, re.DOTALL)
    header = header_match.group(1) if header_match else ""
    
    # Extract footer (everything after last VEVENT)
    footer_match = re.search(r'END:VEVENT\s*$', content, re.DOTALL)
    if footer_match:
        footer_start = footer_match.start() + len('END:VEVENT')
        footer = content[footer_start:]
    else:
        footer = ""
    
    # Split and process events
    events = content.split('BEGIN:VEVENT')[1:]
    enhanced_events = []
    
    for idx, event in enumerate(events):
        progress_bar(idx + 1, len(events))
        enhanced_event = process_event(event, marker_lookup, taboo_lookup)
        enhanced_events.append(enhanced_event)
    
    print()
    
    # Write enhanced file
    print(f"[4/5] Writing enhanced file to {ENHANCED_FILE}...")
    
    enhanced_content = header
    for event in enhanced_events:
        enhanced_content += f'BEGIN:VEVENT{event}'
    enhanced_content += footer
    
    with open(ENHANCED_FILE, 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print(f"✓ Enhanced file written to {ENHANCED_FILE}\n")
    
    return enhanced_content

def split_into_two_files(content):
    """Split enhanced calendar into auspicious and inauspicious files"""
    print("[5/5] Splitting into auspicious and inauspicious files...\n")
    
    # Extract header and footer
    header_match = re.search(r'(.*?)BEGIN:VEVENT', content, re.DOTALL)
    header = header_match.group(1) if header_match else ""
    
    # Match the LAST END:VEVENT to get true footer
    footer_match = re.search(r'END:VEVENT\s*$', content, re.DOTALL)
    if footer_match:
        footer_start = footer_match.start() + len('END:VEVENT')
        footer = content[footer_start:]
    else:
        footer = ""
    
    # Split events
    events = content.split('BEGIN:VEVENT')[1:]
    
    auspicious_events = []
    inauspicious_events = []
    skipped = 0
    
    for idx, event in enumerate(events):
        progress_bar(idx + 1, len(events))
        
        # Extract SUMMARY to check for marker
        summary_match = re.search(r'SUMMARY:([^\n]+)', event)
        if not summary_match:
            skipped += 1
            continue
        
        summary = summary_match.group(1)
        
        # Classify by first marker character
        if summary.startswith('『吉'):
            auspicious_events.append(event)
        elif summary.startswith('『凶'):
            inauspicious_events.append(event)
        else:
            skipped += 1
    
    print()
    
    # Function to write split file
    def write_split_file(filepath, events, calendar_name):
        updated_header = re.sub(
            r'X-WR-CALNAME:[^\n]*',
            f'X-WR-CALNAME:{calendar_name}',
            header
        )
        
        file_content = updated_header
        for event in events:
            file_content += f'BEGIN:VEVENT{event}'
        file_content += footer
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        return len(events)
    
    # Write both files
    auspicious_count = write_split_file(
        AUSPICIOUS_FILE,
        auspicious_events,
        "Auspicious Times"
    )
    
    inauspicious_count = write_split_file(
        INAUSPICIOUS_FILE,
        inauspicious_events,
        "Inauspicious Times"
    )
    
    return auspicious_count, inauspicious_count, skipped

def validate_output_file():
    """Validate the output file is valid ICS"""
    with open(ENHANCED_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'starts_with_BEGIN:VCALENDAR': content.startswith('BEGIN:VCALENDAR'),
        'ends_with_END:VCALENDAR': content.strip().endswith('END:VCALENDAR'),
        'has_VEVENT_blocks': 'BEGIN:VEVENT' in content and 'END:VEVENT' in content,
        'event_count_matches': content.count('BEGIN:VEVENT') == content.count('END:VEVENT'),
    }
    
    return checks

def generate_report():
    """Generate and display completion report"""
    print("\n" + "="*80)
    print("ENHANCEMENT COMPLETE - SUMMARY REPORT")
    print("="*80)
    
    print(f"\n📊 Statistics:")
    print(f"  Total events processed:  {stats['total_events']:,}")
    enhancement_pct = 100*stats['enhanced_events']/max(stats['total_events'],1)
    print(f"  Events enhanced:         {stats['enhanced_events']:,} ({enhancement_pct:.1f}%)")
    print(f"  Events with taboos:      {stats['taboo_added']:,}")
    print(f"  Events skipped:          {stats['skipped_events']:,}")
    print(f"  Missing lookups:         {stats['missing_lookups']}")
    
    print(f"\n📁 Output:")
    print(f"  Enhanced file:           {ENHANCED_FILE}")
    print(f"  Auspicious file:         {AUSPICIOUS_FILE}")
    print(f"  Inauspicious file:       {INAUSPICIOUS_FILE}")
    
    # File sizes
    enhanced_size = Path(ENHANCED_FILE).stat().st_size / (1024*1024)
    auspicious_size = Path(AUSPICIOUS_FILE).stat().st_size / (1024*1024)
    inauspicious_size = Path(INAUSPICIOUS_FILE).stat().st_size / (1024*1024)
    original_size = Path(TRUNK_FILE).stat().st_size / (1024*1024)
    
    print(f"\n💾 File Sizes:")
    print(f"  Original:                {original_size:.2f} MB")
    print(f"  Enhanced:                {enhanced_size:.2f} MB")
    print(f"  Auspicious:              {auspicious_size:.2f} MB")
    print(f"  Inauspicious:            {inauspicious_size:.2f} MB")
    
    # Validation
    print(f"\n✅ Validation Results:")
    checks = validate_output_file()
    for check, result in checks.items():
        status = "PASS" if result else "FAIL"
        print(f"  ✓ {check}: {status}")
    
    overall = all(checks.values())
    print(f"  Overall status:          {'VALID ✓' if overall else 'INVALID ✗'}")
    
    # Samples
    if stats['samples']:
        print(f"\n📝 Sample Transformations (first {len(stats['samples'])} events):")
        for idx, sample in enumerate(stats['samples'], 1):
            print(f"\n  Sample {idx} - Date: {sample['date']}")
            print(f"    Before: {sample['before']}")
            print(f"    After:  {sample['after']}")
    
    # Warnings
    if stats['warnings']:
        print(f"\n⚠️  First {min(5, len(stats['warnings']))} Warnings (total: {len(stats['warnings'])}):")
        for warning in stats['warnings'][:5]:
            print(f"    • {warning}")
    
    print(f"\n📋 Log file saved to:    {LOG_FILE}\n")
    print("="*80)
    
    # Write log file
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Enhancement Timestamp: {datetime.now().isoformat()}\n\n")
        f.write(f"📊 Statistics:\n")
        f.write(f"  Total events processed:  {stats['total_events']}\n")
        f.write(f"  Events enhanced:         {stats['enhanced_events']}\n")
        f.write(f"  Events with taboos:      {stats['taboo_added']}\n")
        f.write(f"  Events skipped:          {stats['skipped_events']}\n")
        f.write(f"  Missing lookups:         {stats['missing_lookups']}\n\n")
        
        f.write(f"📝 Sample Transformations:\n")
        for idx, sample in enumerate(stats['samples'], 1):
            f.write(f"\n  Sample {idx} - Date: {sample['date']}\n")
            f.write(f"    {sample['before']}\n")
            f.write(f"    {sample['after']}\n")
        
        if stats['warnings']:
            f.write(f"\n⚠️  Warnings (total: {len(stats['warnings'])}):\n")
            for warning in stats['warnings'][:10]:
                f.write(f"    • {warning}\n")

def main():
    """Main execution"""
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "Calendar Enhancement Script (Extended)".center(78) + "║")
    print("║" + "Add markers + taboos, then split by auspiciousness".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    # Count total events
    with open(TRUNK_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    stats['total_events'] = content.count('BEGIN:VEVENT')
    
    # Build lookups
    marker_lookup = build_lookup_dictionary()
    taboo_lookup = build_taboo_dictionary()
    
    # Enhance and write enhanced file
    enhanced_content = enhance_trunk_branch(marker_lookup, taboo_lookup)
    
    # Split into two files
    auspicious_count, inauspicious_count, split_skipped = split_into_two_files(enhanced_content)
    
    # Generate report
    generate_report()
    
    print(f"\n📊 Split Summary:")
    print(f"  Auspicious (吉):        {auspicious_count}")
    print(f"  Inauspicious (凶):      {inauspicious_count}")
    print(f"  Skipped (unenhanced):   {split_skipped}")
    print(f"  ────────────────────────")
    print(f"  Total in output:        {auspicious_count + inauspicious_count}")
    print()

if __name__ == '__main__':
    main()
