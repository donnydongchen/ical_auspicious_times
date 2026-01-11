import re

with open('cal_trunkBranch_enhanced.ics', 'r', encoding='utf-8') as f:
    content = f.read()

auspicious_count = content.count("『吉")
inauspicious_count = content.count("『凶")

print(f"Enhanced file has:")
print(f"  吉 markers: {auspicious_count}")
print(f"  凶 markers: {inauspicious_count}")

events = content.split('BEGIN:VEVENT')[1:]
auspicious_events = []
inauspicious_events = []

for event in events:
    summary_match = re.search(r'SUMMARY:([^\n]+)', event)
    if summary_match:
        summary = summary_match.group(1)
        if summary.startswith('『吉'):
            auspicious_events.append(event)
        elif summary.startswith('『凶'):
            inauspicious_events.append(event)

print(f"\nLogic would create:")
print(f"  Auspicious events: {len(auspicious_events)}")
print(f"  Inauspicious events: {len(inauspicious_events)}")
