import re
with open(r'D:\长征文化\_controls_check.js', encoding='utf-8') as f:
    js = f.read()

# Functions referenced in initControls
refd = ['stopSpeech', 'readCurrentContent', 'showSpeedSelector', 'hideSpeedSelector',
        'togglePause', 'skipToNext', 'restartAutowalk', 'toggleArmySelector',
        'openSparkForm', 'stopAutowalk', 'toggleMessageBoard', 'toggleBasemap',
        'closeNodePanel', 'startAutowalk', 'selectAutowalkSpeed',
        'getSegmentRoutePoints', 'animateMovement', 'arriveAtNode']

for fn in sorted(refd):
    # Check if function is defined (not just called)
    pat_def = re.compile(rf'(^|\n)\s*(function\s+{fn}|{fn}\s*=\s*function)')
    if pat_def.search(js):
        print(f'  DEF  {fn}')
    else:
        # Check if it's referenced at all
        if fn in js:
            print(f'  CALL {fn}')
        else:
            print(f'  ABSENT {fn}')
