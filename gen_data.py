#!/usr/bin/env python3
"""Build src/data.json for the 2K27 Lab from research tables + LockerCodes scrapes."""
import json, re, glob, os
ROOT = os.path.dirname(os.path.abspath(__file__)); LC = os.environ.get("LC_DIR", "/workspace/lc/")
def ht(s):
    m = re.match(r"(\d)'(\d+)", s); return int(m[1]) * 12 + int(m[2])

COST = {"cheap": [1, 3, 4, 5], "mid": [2, 4, 5, 6], "exp": [3, 5, 6, 7]}
CHEAP = "Aerial Wizard,Ghost Stepper,Hook Specialist,Paint Prodigy,Post Powerhouse,Post Spin Catalyst,Rise Up,Mini Marksman,Post Fade Phenom,Break Starter,Dimer,High-Flying Denier,Immovable Enforcer,Off-Ball Pest,Post Lockdown,Sync Snatcher,Brick Wall,Pogo Stick".split(",")
MID = "Physical Finisher,Set and Fire,Static Middy,Handles for Days,Pace,Strong Handle,Versatile Visionary,Ankle Braces,Glove,Interceptor,Boxout Boss,Bruiser,Slippery Off-Ball,Work Horse".split(",")
def cost_of(n): return "cheap" if n in CHEAP else "mid" if n in MID else "exp"

B = []
def add(cat, n, op, reqs, mn="5'9", mx="7'4", desc=""):
    B.append({"n": n, "cat": cat, "op": op, "r": [[a, t] for a, t in reqs], "mn": ht(mn), "mx": ht(mx), "c": cost_of(n), "d": desc})
F, S, P, D, R, Y = "Finishing", "Shooting", "Playmaking", "Defense", "Rebounding", "Physicals"
add(F,'Aerial Wizard','OR',[('DD',[60,70,80,94]),('SD',[60,70,80,93])],desc="Finish alley-oops from a teammate and putbacks off an offensive rebound (in-game text).")
add(F,'Float Game','OR',[('CS',[65,80,90,96]),('DL',[65,85,93,95])])
add(F,'Ghost Stepper','OR',[('CS',[55,77,86,94]),('PC',[55,77,86,94])],desc="Boosts step-through layups and close shots that come after a fake.")
add(F,'Hook Specialist','AND',[('CS',[60,75,87,94]),('PC',[55,65,80,90])])
add(F,'Layup Mixmaster','AND',[('DL',[70,83,90,99])],mx="7'0")
add(F,'Paint Prodigy','AND',[('CS',[60,85,90,96])],mn="6'3")
add(F,'Physical Finisher','AND',[('DL',[60,80,90,96]),('STR',[60,70,80,90])])
add(F,'Post Powerhouse','AND',[('PC',[60,75,85,95]),('STR',[65,79,86,95])],mn="6'5")
add(F,'Post Spin Catalyst','AND',[('PC',[65,83,91,99])],mn="6'1")
add(F,'Posterizer','AND',[('DD',[73,87,93,99]),('VERT',[65,75,80,90])])
add(F,'Rise Up','AND',[('SD',[60,81,90,99]),('VERT',[55,62,66,70])],mn="6'5")
add(S,'Arc Cadence','AND',[('3PT',[70,86,91,98])],mx="6'11",desc="Off-the-dribble threes (creator description).")
add(S,'Deadeye','OR',[('MID',[65,85,92,99]),('3PT',[65,85,92,99])],desc="Reduces the penalty from closing-out defenders.")
add(S,'Limitless Range','AND',[('3PT',[83,89,93,99])],desc="Extends effective three-point range.")
add(S,'Mini Marksman','OR',[('MID',[60,79,94,99]),('3PT',[60,79,94,99])],mx="6'4",desc="Activates vs defenders 3+ inches taller (creator description).")
add(S,'Post Fade Phenom','AND',[('MID',[60,71,84,91]),('PC',[55,74,84,93])])
add(S,'Quick Trigger','OR',[('MID',[80,88,95,99]),('3PT',[80,88,95,99])])
add(S,'Set and Fire','AND',[('3PT',[60,78,89,97])],desc="Boosts set-foot three-pointers.")
add(S,'Smooth Operator','AND',[('MID',[70,87,93,99])],desc="Off-the-dribble mid-range (creator description). games.gg lists ≤6'11\"; NBA2KLab/LGC list no limit.")
add(S,'Static Middy','AND',[('MID',[55,75,85,95])],desc="Set mid-range; Reddit reports it also fires on corner 3s.")
add(P,'Ankle Assassin','AND',[('BH',[75,86,93,96])],mx="6'10")
add(P,'Bail Out','AND',[('PA',[85,93,96,99])])
add(P,'Break Starter','AND',[('PA',[65,77,89,97])],desc="Full-court outlet passes off defensive rebounds.")
add(P,'Dimer','AND',[('PA',[50,70,86,95])])
add(P,'Handles for Days','AND',[('BH',[71,81,90,95])],mx="7'0")
add(P,'Lightning Launch','AND',[('SWB',[68,75,86,91])],mx="6'11",desc="Speeds up launches when attacking from the perimeter (in-game text).")
add(P,'Pace','AND',[('SWB',[70,80,88,93])],mx="6'10",desc="Raises the ball handler's speed when sprinting.")
add(P,'Strong Handle','AND',[('BH',[60,67,73,78]),('STR',[75,82,89,95])],mx="6'11")
add(P,'Unpluckable','OR',[('BH',[65,80,92,97]),('PC',[65,86,96,999])])
add(P,'Versatile Visionary','AND',[('PA',[65,80,90,99])])
add(D,'Ankle Braces','AND',[('PERD',[60,86,93,95]),('AGI',[65,82,89,92])],mx="6'9")
add(D,'Challenger','AND',[('PERD',[71,82,92,98])],mx="6'11")
add(D,'Glove','AND',[('STL',[70,83,93,99])],mx="7'0")
add(D,'High-Flying Denier','AND',[('BLK',[68,78,88,92]),('VERT',[60,74,80,83])],mn="6'3")
add(D,'Immovable Enforcer','AND',[('PERD',[62,72,84,91]),('STR',[71,82,85,92])])
add(D,'Interceptor','AND',[('STL',[60,77,90,97])])
add(D,'Off-Ball Pest','OR',[('INTD',[60,76,85,93]),('PERD',[55,68,80,89])])
add(D,'Paint Patroller','AND',[('INTD',[60,71,77,84]),('BLK',[70,84,93,99])],mn="6'5")
add(D,'Pick Dodger','AND',[('PERD',[73,83,90,97]),('AGI',[71,81,88,91])],mx="6'10")
add(D,'Post Lockdown','AND',[('INTD',[65,82,88,93]),('STR',[65,74,80,88])],mn="6'5")
add(D,'Seatbelt','AND',[('PERD',[75,85,91,99]),('AGI',[70,77,80,86])],mx="6'9")
add(D,'Wall Up','AND',[('INTD',[80,85,95,99]),('STR',[75,80,90,92])],mn="6'5")
add(R,'Boxout Boss','AND',[('DREB',[65,75,90,98]),('STR',[60,76,88,94])],mn="6'3")
add(R,'Breaker','AND',[('OREB',[65,82,92,98]),('STR',[70,79,90,96])],mn="6'3")
add(R,'Crasher','AND',[('OREB',[60,80,93,99]),('VERT',[60,65,67,70])])
add(R,'Possession Closer','AND',[('DREB',[67,87,95,99]),('VERT',[60,65,67,70])])
add(R,'Sync Snatcher','OR',[('OREB',[55,70,82,90]),('DREB',[55,70,82,90])])
add(Y,'Brick Wall','AND',[('STR',[75,83,95,99])],mn="6'5")
add(Y,'Bruiser','AND',[('STR',[71,84,93,99])])
add(Y,'Flash','AND',[('SPD',[70,82,87,95]),('AGI',[60,78,81,91])],desc="Faster off-ball movement in transition on offense or defense.")
add(Y,'Pogo Stick','AND',[('VERT',[63,70,80,90])])
add(Y,'Slippery Off-Ball','AND',[('SPD',[57,73,85,94]),('AGI',[57,65,77,90])],mx="6'9")
add(Y,'Work Horse','OR',[('AGI',[60,75,85,95]),('STR',[60,75,85,95])],desc="Faster when chasing loose balls.")

ALIASES = [
 {"a": "Set Shot Specialist", "to": "Set and Fire", "note": "2K24/25 set-shot badge; 2K27's equivalent is Set and Fire (set-foot 3PT)."},
 {"a": "Catch and Shoot", "to": "Set and Fire", "note": "Not a 2K27 badge; closest is Set and Fire."},
 {"a": "Rebound Chaser", "to": "Sync Snatcher", "note": "2K25/26 badge, not in 2K27. Closest: Sync Snatcher / Possession Closer / Crasher."},
 {"a": "Boxout Beast", "to": "Boxout Boss", "note": "2K25/26 name. 2K27 uses Boxout Boss."},
 {"a": "Anchor", "to": "Paint Patroller", "note": "2K25/26 rim-protection badge, not in 2K27. Closest: Paint Patroller / High-Flying Denier."},
 {"a": "Pogo Stick", "to": "Pogo Stick", "note": "Same name in 2K27."},
 {"a": "Limitless Range (2K25)", "to": "Limitless Range", "note": "Same name; 2K27 thresholds 83/89/93/99."},
]
ATTRS = [["CS","Close Shot","F"],["DL","Driving Layup","F"],["DD","Driving Dunk","F"],["SD","Standing Dunk","F"],["PC","Post Control","F"],
 ["MID","Mid-Range","S"],["3PT","Three-Point","S"],["FT","Free Throw","S"],["PA","Pass Accuracy","P"],["BH","Ball Handle","P"],["SWB","Speed With Ball","P"],
 ["INTD","Interior Defense","D"],["PERD","Perimeter Defense","D"],["STL","Steal","D"],["BLK","Block","D"],["OREB","Offensive Rebound","R"],["DREB","Defensive Rebound","R"],
 ["SPD","Speed","Y"],["AGI","Agility","Y"],["STR","Strength","Y"],["VERT","Vertical","Y"]]

# ---- animations from LockerCodes scrapes ----
A = []
def load(f, cols, cat, group):
    p = LC + f
    if not os.path.exists(p): return
    for line in open(p).read().splitlines()[1:]:
        c = [x.strip() for x in line.split('|')]
        if len(c) < len(cols): continue
        r = dict(zip(cols, c))
        try: mn, mx = ht(r['min']), ht(r['max'])
        except Exception: continue
        req = {}
        for k in ['DD','SD','VERT','BH','SWB','DL','PA','PC','AGI','SPD','MID','3PT','SHOT']:
            if k in r and r[k] not in ('', '0'):
                try: req[k] = int(r[k])
                except: pass
        mode = "OR" if cat.startswith("Shot:") else "AND"
        A.append({"n": r['name'], "g": group, "cat": cat, "req": req, "mode": mode, "mn": mn, "mx": mx})
load('all-dribble-moves_dribble-style.txt', ['name','SWB','min','max'], 'Dribble Style', 'Dribble')
load('all-dribble-moves_signature-size-up.txt', ['name','BH','min','max'], 'Signature Size-Up', 'Dribble')
for f in sorted(glob.glob(LC + 'all-dribble-moves_*.txt')):
    f = f.split('/')[-1]; k = f.replace('all-dribble-moves_', '').replace('.txt', '')
    if k in ('dribble-style', 'signature-size-up'): continue
    load(f, ['name','BH','min','max'], k.replace('-', ' ').title(), 'Dribble')
load('all-dunks_contact-dunks.txt', ['name','DD','SD','VERT','min','max'], 'Contact Dunks', 'Dunk')
load('all-dunks_signature-dunks.txt', ['name','DD','SD','VERT','min','max'], 'Signature Dunks', 'Dunk')
load('all-dunks_dunk-packages.txt', ['name','DD','SD','VERT','min','max'], 'Dunk Packages', 'Dunk')
load('all-dunks_alley-oops.txt', ['name','DD','SD','VERT','min','max'], 'Alley-Oops', 'Dunk')
load('jumpshots.txt', ['name','min','max','SHOT'], 'Jump Shot Base (partial 100/781)', 'Shooting')
for f, nm in [('all-shot-animations_dribble-pull-ups.txt','Shot: Pull-Up'),('all-shot-animations_go-to-shots.txt','Shot: Go-To'),
              ('all-shot-animations_hop-jumpers.txt','Shot: Hop Jumper'),('all-shot-animations_spin-jumpers.txt','Shot: Spin Jumper')]:
    load(f, ['name','min','max','MID','3PT'], nm, 'Shooting')
load('layups.txt', ['name','DL','min','max'], 'Layup Package', 'Finishing')
load('post-moves.txt', ['name','min','max','PC'], 'Post Moves', 'Finishing')
load('pass-styles.txt', ['name','PA','min','max'], 'Pass Style', 'Passing')
load('motion-styles.txt', ['name','AGI','SPD','min','max'], 'Motion Style (partial 100/353)', 'Motion')
# dedupe
seen = set(); A2 = []
for a in A:
    k = (a['n'], a['cat'])
    if k in seen: continue
    seen.add(k); A2.append(a)
A = A2
# Requested but NOT in the verified scrape -> flagged, no invented numbers
UNVERIFIED = [
 {"n": "Steve Francis (size-up / combos)", "cat": "Dribble", "note": "Not present in the LockerCodes Sep 3 tables we scraped. Check NBA 2K HQ / in-game Builder."},
 {"n": "Patty Mills (jump shot base)", "cat": "Jump Shot Base", "note": "Jump-shot base list was only partially scraped (A–Ay, 100/781). Requirement not verified."},
 {"n": "Tracy McGrady (jump shot base)", "cat": "Jump Shot Base", "note": "Not in the partial jump-shot scrape. T-Mac Breakdown Combo (BH 85, 6'5\"–6'9\") IS verified."},
 {"n": "Jarrett Culver (jump shot base)", "cat": "Jump Shot Base", "note": "Not in the partial jump-shot scrape."},
]
PASS_NOTES = {
 "Tyrese Haliburton": "#1 practical meta at ≤91: fast windup, high release, a few flashy whips (r/NBA2k, tposegaming).",
 "Jason Williams": "Flashiest package; 'normal passes are slow', mainly the elbow pass as its flashy (r/NBA2k Aug 2026).",
 "Magic Johnson": "Unique full-court outlet animations ('only one with special long passes'); slower/telegraphed in half court unless very high PA.",
 "LeBron James": "Most-cited outlet style for bigs: 'super fast fling' full-court tap pass.",
 "Nikola Jokic": "Big-man one-handed post/overhead passes; outlets reported as telegraphed.",
 "Darius Garland": "Top high-PA style (92).", "Mike Conley": "95 PA; smooth, fast.", "Domantas Sabonis": "Budget big-man option (75)."}

TAKEOVERS = [
 {"n":"Shot Artist","cat":"Shooting","op":"OR","r":[["3PT",89],["MID",89]],"note":"Patch 2.0 retimed the window."},
 {"n":"Calibrated","cat":"Shooting","op":"OR","r":[["3PT",85],["MID",85]],"note":"Patch 2.0 retimed the window."},
 {"n":"Zip Code","cat":"Shooting","op":"OR","r":[["3PT",91]],"note":"Gate 91 (NBA2KLab/LockerCodes)."},
 {"n":"Navigator","cat":"Finishing","op":"AND","r":[["DL",85]],"note":"Patch 2.0 retimed."},
 {"n":"Airspace","cat":"Finishing","op":"AND","r":[["DD",87],["VERT",75]],"note":"Nerfed in Patch 2.0; Rim Guardian counters it."},
 {"n":"Inside Touch","cat":"Finishing","op":"AND","r":[["CS",85]],"note":""},
 {"n":"Detonator","cat":"Finishing","op":"AND","r":[["SD",85]],"note":"Nerfed in Patch 2.0."},
 {"n":"Paint Surgeon","cat":"Finishing","op":"AND","r":[["CS",80],["PC",75]],"note":""},
 {"n":"Dishmaster","cat":"Playmaking","op":"AND","r":[["PA",80]],"note":""},
 {"n":"Rim Guardian","cat":"Defense","op":"AND","r":[["INTD",80],["BLK",80]],"note":"Counters Airspace after Patch 2.0."},
 {"n":"Demolition","cat":"Rebounding","op":"AND","r":[["STR",88]],"note":""},
 {"n":"See The Future","cat":"Rebounding","op":"AND","r":[["OREB",85],["DREB",85]],"note":""},
 {"n":"Second Chance","cat":"Rebounding","op":"AND","r":[["OREB",80]],"note":""},
 {"n":"Muscle","cat":"Rebounding","op":"AND","r":[["OREB",80],["DREB",80],["STR",80]],"note":"Listed as 80/80/80; the exact attribute trio is our reading — verify in game."},
 {"n":"Hydration Hero","cat":"Any","op":"AND","r":[],"note":"Any slot; prevents Adrenaline/Stamina drain."},
 {"n":"Blur / Cook (Playmaking)","cat":"Playmaking","op":"NA","r":[],"note":"Gate not verified in our sources."},
 {"n":"Glue / Hawk (Defense)","cat":"Defense","op":"NA","r":[],"note":"Gate not verified in our sources."},
]

CB_SOURCES = [
 {"id":"rep","n":"REP","max":11,"items":["Rookie VI","Starter I","Starter IV","Starter VII","Veteran I","Veteran IV","Veteran VI","Elite I","Elite III","Legend (+2)",""],"note":"Rookie VI, Starter I/IV/VII, Veteran I/IV/VI, Elite I/III (+1 each), Legend (+2)"},
 {"id":"season","n":"Season Pass (Lv 40 free track)","max":9,"note":"1 per season. S1 ended; S2 Lv 40 earnable now; S3–S9 add 7 more."},
 {"id":"crew","n":"Crew","max":4,"note":"Crew levels 16 / 22 / 29 / 40 (7 days membership each)."},
 {"id":"life","n":"Lifetime Challenges","max":2,"note":"200 and 400 challenges completed."},
 {"id":"spec","n":"Build Specialization","max":2,"note":"Goal 9. Only usable in the specialized category or Free Throw (official 2K27)."},
]

PAIRS_SEEN = [
 ["Set and Fire","Deadeye","6'5\" xUncleCaino (classic pairing per NBA2KLab)"],
 ["Limitless Range","Arc Cadence","6'3\" _Blixx"],["Pace","Challenger","6'3\" _Blixx"],["Handles for Days","Versatile Visionary","6'3\" _Blixx"],
 ["Lightning Launch","Interceptor","6'3\" _Blixx"],["Deadeye","Mini Marksman","6'3\" _Blixx"],["Set and Fire","Glove","6'3\" _Blixx (+2 slot)"],
 ["Handles for Days","Lightning Launch","6'3\" owner build (in-game)"],["Pace","Flash","6'3\" owner build (in-game)"],["Ankle Assassin","Layup Mixmaster","6'3\" owner build (in-game)"],
 ["Mini Marksman","Deadeye","6'3\" owner build (in-game)"],["Arc Cadence","Smooth Operator","6'5\" xUncleCaino"],["Handles for Days","Ankle Assassin","6'5\" xUncleCaino"],
 ["Seatbelt","Limitless Range","6'5\" xUncleCaino"],["Sync Snatcher","Work Horse","7'0\" owner build (in-game, decoded)"],["Dimer","Versatile Visionary","7'0\" owner build (in-game, decoded)"],
]

def A_(d): return d
# ---------- BUILDS ----------
# ladders: list of gains per breaker application (len<5 => hard cap after that many). 'cap': max potential before breakers (if current<cap -> MyPoints lock)
BUILDS = []
def build(id_, name, pos, h, wt, ws, attrs, ladders=None, caps=None, kind="mine", note="", pools=None, loadouts=None, cb_avail=None, src=""):
    BUILDS.append({"id": id_, "name": name, "pos": pos, "h": h, "wt": wt, "ws": ws, "a": attrs, "lad": ladders or {}, "cap": caps or {},
                   "kind": kind, "note": note, "pools": pools or {"F":12,"S":14,"P":12,"D":12,"R":4,"Y":6}, "lo": loadouts or {}, "cbAvail": cb_avail, "src": src})
# 6'3" Hash-Sinking Slasher (section 10/12; DD now 84 after breaker)
b5 = dict(CS=66,DL=90,DD=84,SD=27,PC=25,MID=81,**{'3PT':92},FT=66,PA=70,BH=95,SWB=88,INTD=25,PERD=84,STL=83,BLK=34,OREB=26,DREB=28,SPD=88,AGI=81,STR=47,VERT=80)
lo_pg_rec = {
 "fuse": [["Set and Fire","Deadeye",1],["Limitless Range","Arc Cadence",1],["Handles for Days","Lightning Launch",1],["Pace","Flash",1]],
 "eq": {"Deadeye":3,"Arc Cadence":3,"Mini Marksman":2,"Smooth Operator":1,"Set and Fire":3,"Limitless Range":2,
        "Handles for Days":4,"Pace":3,"Ankle Assassin":3,"Lightning Launch":3,"Dimer":2,
        "Seatbelt":1,"Interceptor":2,"Off-Ball Pest":3,"Challenger":1,
        "Layup Mixmaster":3,"Aerial Wizard":2,"Posterizer":1,"Flash":3,"Work Horse":1},
 "tk": ["Shot Artist","Navigator","Hydration Hero","",""],
 "why": "Section 12.3 fresh loadout: converged from _Blixx (6'3\"), xUncleCaino (6'5\"), Quil (6'4\"), oFAB. No Quick Trigger (his preference)."}
lo_pg_3s = json.loads(json.dumps(lo_pg_rec)); lo_pg_3s["why"] = "Same core for 3s; Challenger B kept for switch-heavy 3v3 (our pick)."
build("hash63","6'3\" Hash-Sinking Slasher","PG",75,178,76,b5,
      ladders=dict(DL=[1],DD=[4,3,1,1],SD=[15],MID=[1],**{'3PT':[1,1,1,1]},FT=[7],PA=[3],SWB=[1],PERD=[2],STL=[4,3],OREB=[14],SPD=[1],AGI=[2],STR=[10],VERT=[3]),
      caps=dict(CS=76,PC=42,INTD=40,BLK=35,DREB=45), note="98 OVR · 6'4\" WS. Lock by name = MyPoints first (confirmed in game: Close Shot to 76). DD 84 after first breaker.",
      pools={"F":12,"S":18,"P":15,"D":14,"R":0,"Y":8}, loadouts={"rec":lo_pg_rec,"3s":lo_pg_3s}, src="2k27_research.md §10, §12")
b1 = dict(CS=75,DL=71,DD=32,SD=27,PC=40,MID=85,**{'3PT':99},FT=70,PA=61,BH=86,SWB=88,INTD=50,PERD=81,STL=90,BLK=33,OREB=25,DREB=49,SPD=95,AGI=91,STR=42,VERT=65)
build("bandit64","6'4\" Shot-Hunting Bandit (2-Way Athletic Iso Sniper)","PG",76,190,80,b1,
      ladders=dict(CS=[4,3],DL=[2,2],DD=[12,10],SD=[15,12],PC=[12,9],MID=[1,1],FT=[7,6],PA=[4,4],BH=[1,1],SWB=[1,1],INTD=[10,8],PERD=[3,2],STL=[2],BLK=[14,11],OREB=[13,12],DREB=[9,7],SPD=[1,1],AGI=[1,1],STR=[11,9],VERT=[4,4]),
      note="99 3PT · 2 breakers left. #1 rec: Perimeter D ×2 (4 Silver D badges).", src="2k27_research.md §4, §6")
b2 = dict(CS=64,DL=68,DD=87,SD=39,PC=46,MID=70,**{'3PT':80},FT=59,PA=58,BH=83,SWB=84,INTD=62,PERD=92,STL=90,BLK=48,OREB=34,DREB=52,SPD=91,AGI=88,STR=89,VERT=89)
build("post66","6'6\" 2-Way Slashing Posterizer (Pesky Posterizing Point)","PG",78,230,83,b2,
      ladders=dict(CS=[4,4],DL=[2,2],DD=[1],SD=[11,10],PC=[11,8],MID=[2,2],**{'3PT':[1,1]},FT=[8,7],PA=[4,4],BH=[1,1],INTD=[8,7],PERD=[1,1],STL=[1,1],BLK=[10,8],OREB=[14,11],DREB=[8,7],SPD=[1,1],VERT=[1,1]),
      note="98/99 OVR · 6'11\" WS · 2 breakers. #1 rec: Ball Handle ×2 (Coby White / Luka / LaVine size-ups).", src="2k27_research.md §7")
b3 = dict(CS=94,DL=44,DD=87,SD=25,PC=25,MID=95,**{'3PT':89},FT=71,PA=70,BH=72,SWB=73,INTD=26,PERD=76,STL=70,BLK=29,OREB=30,DREB=25,SPD=85,AGI=82,STR=75,VERT=78)
build("verde67","6'7\" Verde SG","SG",79,210,78,b3,
      ladders=dict(DD=[1,1,1,1,1],MID=[1],**{'3PT':[1]},FT=[6,5,5],PA=[3,3,3],BH=[1,1,1],SWB=[1,1,1],PERD=[2,1,1],SPD=[1,1,1,1],AGI=[1,1,1,1],STR=[4,3,3],VERT=[2,2,2]),
      caps=dict(DL=73,SD=47,PC=49,STL=77,INTD=51,BLK=33,OREB=42,DREB=45), note="95/95 OVR (not fully upgraded) · 3 breakers. #1 rec: DD ×2 + Vert ×1 (Pro Contact Off One).", src="2k27_research.md §8")
b4 = dict(CS=78,DL=71,DD=87,SD=47,PC=51,MID=95,**{'3PT':89},FT=67,PA=70,BH=86,SWB=76,INTD=65,PERD=85,STL=83,BLK=42,OREB=34,DREB=55,SPD=83,AGI=82,STR=85,VERT=75)
build("demon68","6'8\" Deadeye Demon SF","SF",80,216,80,b4,
      ladders=dict(CS=[2,2],DL=[1,1],DD=[1],SD=[6,6],PC=[3,3],MID=[1,1],**{'3PT':[1,1]},FT=[7,5],PA=[2,2],SWB=[1,1],INTD=[4,4],PERD=[2,1],STL=[1],BLK=[10,8],OREB=[13,10],DREB=[6,6],SPD=[1,1],AGI=[1],STR=[1,1],VERT=[1,1]),
      note="99 OVR, all at cap · 2 breakers. #1 rec: 3PT ×2 → 91 (Arc Cadence Gold).", src="2k27_research.md §9")
bc = dict(CS=72,DL=50,DD=70,SD=81,PC=60,MID=80,**{'3PT':86},FT=65,PA=91,BH=55,SWB=50,INTD=85,PERD=65,STL=65,BLK=84,OREB=93,DREB=95,SPD=60,AGI=55,STR=90,VERT=80)
lo_c_rec = {"fuse":[["Sync Snatcher","Work Horse",1],["Dimer","Versatile Visionary",1],["Possession Closer","Boxout Boss",1],["Crasher","Paint Patroller",1]],
 "eq":{"Aerial Wizard":2,"Rise Up":2,"Set and Fire":2,"Deadeye":2,"Static Middy":2,"Dimer":3,"Break Starter":3,"Versatile Visionary":3,
       "Paint Patroller":2,"High-Flying Denier":2,"Immovable Enforcer":1,"Post Lockdown":2,"Interceptor":1,
       "Sync Snatcher":4,"Possession Closer":3,"Crasher":3,"Breaker":3,"Boxout Boss":3,"Brick Wall":2,"Work Horse":3},
 "tk":["Calibrated","Hydration Hero","Dishmaster","Rim Guardian","Demolition"],
 "why":"§11.7 Rec loadout: rim protection, boards, screens, outlets. Wall Up → Post Lockdown + Interceptor. Pairings after Sync/Dimer are our picks — verify Builder legality."}
lo_c_3s = {"fuse":[["Deadeye","Static Middy",1],["Sync Snatcher","Work Horse",1],["Possession Closer","Boxout Boss",1],["Crasher","Paint Patroller",1]],
 "eq":{"Aerial Wizard":2,"Rise Up":2,"Set and Fire":2,"Deadeye":2,"Static Middy":2,"Limitless Range":1,"Dimer":3,"Versatile Visionary":3,
       "Paint Patroller":2,"High-Flying Denier":2,"Immovable Enforcer":1,"Off-Ball Pest":3,
       "Sync Snatcher":4,"Possession Closer":3,"Crasher":3,"Breaker":3,"Boxout Boss":3,"Bruiser":2,"Pogo Stick":3},
 "tk":["Calibrated","Hydration Hero","Dishmaster","Rim Guardian","See The Future"],
 "why":"Deadeye→Static Middy reaction is our pick (verify Builder). §11.8 3s loadout: switches + pick-and-pop. Fuse moves to Deadeye (S→G), frees tokens for Limitless B; Bruiser S + Pogo G."}
build("pp70","7'0\" PlayShot Paint Protector C","C",84,260,90,bc,
      note="91 Pass Acc · Tyrese Haliburton pass style. Attribute sheet reconstructed (≈) from his computed max tiers in §11.3 — enter exact values from your screen.",
      pools={"F":6,"S":13,"P":9,"D":15,"R":13,"Y":8}, loadouts={"rec":lo_c_rec,"3s":lo_c_3s}, src="2k27_research.md §11 + pass-settings research")
# Community / comp meta templates (illustrative; tagged as such)
build("blixx63","6'3\" Ball-Hawking 3PT Slasher (_Blixx, post-patch)","PG",75,175,75,
      dict(CS=39,DL=47,DD=87,SD=25,PC=25,MID=80,**{'3PT':99},FT=38,PA=80,BH=92,SWB=93,INTD=64,PERD=82,STL=93,BLK=59,OREB=25,DREB=57,SPD=84,AGI=75,STR=25,VERT=75),
      kind="pro", note="From his Oct 10 X screenshot: 3PT 99, Mid 80, BH 92, SWB 93, Pass 80, PerD 82, Steal 93, DD 87, Vert 75. Other ratings are ESTIMATES (not shown in the post). Token pools estimated.",
      pools={"F":10,"S":19,"P":15,"D":17,"R":1,"Y":8},
      loadouts={"rec":{"fuse":[["Pace","Challenger",1],["Handles for Days","Versatile Visionary",1],["Lightning Launch","Interceptor",1],["Limitless Range","Arc Cadence",1],["Deadeye","Mini Marksman",1],["Set and Fire","Glove",2]],
       "eq":{"Aerial Wizard":3,"Posterizer":2,"Smooth Operator":1,"Set and Fire":4,"Limitless Range":4,"Deadeye":4,"Mini Marksman":4,"Arc Cadence":4,"Static Middy":2,
             "Pace":4,"Handles for Days":3,"Lightning Launch":4,"Ankle Assassin":2,"Versatile Visionary":2,"Dimer":2,"Break Starter":2,
             "Glove":3,"Challenger":2,"Interceptor":3,"Seatbelt":1,"Off-Ball Pest":3,"Sync Snatcher":1,"Pogo Stick":2,"Flash":1,"Work Horse":1},
       "tk":["Shot Artist","","","",""],"why":"Decoded from https://x.com/_Blixx/status/2109014475533959235"}}, src="X @_Blixx Oct 10, 2026")
build("sharp62","6'2\" PlaySharp (+5 3PT breaker → 99) · Comp Pro-Am / Rec","PG",74,180,78,
      dict(CS=70,DL=85,DD=60,SD=25,PC=30,MID=85,**{'3PT':94},FT=80,PA=82,BH=92,SWB=90,INTD=30,PERD=80,STL=85,BLK=30,OREB=25,DREB=35,SPD=90,AGI=86,STR=40,VERT=70),
      ladders={"3PT":[1,1,1,1,1]}, kind="meta", note="Meta TEMPLATE (illustrative, not a single creator's exact sheet). +5 3PT breakers 94→99 = HOF shooting + Mini Marksman HOF.", src="community meta (Quil/oFAB/Blixx convergence)")
build("iso64","6'4\" 2-Way Iso Creator · Rec / 3v3","PG",76,195,82,
      dict(CS=75,DL=88,DD=86,SD=30,PC=40,MID=88,**{'3PT':91},FT=75,PA=75,BH=91,SWB=88,INTD=40,PERD=86,STL=84,BLK=40,OREB=28,DREB=45,SPD=87,AGI=82,STR=55,VERT=78),
      kind="meta", note="Meta TEMPLATE (illustrative). Breaker targets: DD 86→89 (Pro Contact Off One), 3PT 91→93 (Limitless G).", src="community meta")
build("lock66","6'6\" Lockdown (Two-Way Lock) · Comp / Rec","SG",78,215,85,
      dict(CS=65,DL=75,DD=80,SD=40,PC=40,MID=75,**{'3PT':80},FT=65,PA=65,BH=75,SWB=75,INTD=70,PERD=92,STL=90,BLK=65,OREB=35,DREB=60,SPD=88,AGI=86,STR=82,VERT=80),
      kind="meta", note="Meta TEMPLATE. Seatbelt/Immovable Enforcer/Bruiser are 'required for perimeter defenders' (r/NBA2k).", src="r/NBA2k + xUncleCaino lockdown loadout")
build("backend67","6'7\" Backend PF · Rec","PF",79,235,86,
      dict(CS=80,DL=72,DD=85,SD=75,PC=55,MID=78,**{'3PT':80},FT=65,PA=65,BH=65,SWB=62,INTD=82,PERD=80,STL=70,BLK=78,OREB=70,DREB=80,SPD=78,AGI=74,STR=86,VERT=82),
      kind="meta", note="Meta TEMPLATE (illustrative). Rise Up/Post Lockdown/Boxout Boss eligible at 6'7\".", src="community meta")
build("pop70","7'0\" Pop / Inside-Out Big · Rec / 3v3","C",84,255,89,
      dict(CS=78,DL=55,DD=60,SD=82,PC=60,MID=86,**{'3PT':88},FT=70,PA=80,BH=55,SWB=50,INTD=86,PERD=60,STL=55,BLK=86,OREB=70,DREB=88,SPD=60,AGI=55,STR=85,VERT=75),
      kind="meta", note="Meta TEMPLATE (illustrative). Calibrated (85), Limitless B (83), Paint Patroller S, Rim Guardian.", src="community meta")

PASS_PRESET = {
 "rows": [["Skip Pass","Enabled","Hold X / A = skip pass to the farthest receiver in the Left-Stick direction."],
          ["Icon Passing","Pass Type Control","Options: Default / Pass Type Control / Full Receiver Control. PTC: tap icon = normal, double-tap = bounce, hold = lob."],
          ["Icon Lead Passing","On (if shown)","Lead the receiver with the LEFT stick while pressing his icon."],
          ["Pass Target Profile","Custom",""],
          ["Pass Target Direction","85","Weights the literal stick direction. Higher = the game follows your aim (2K dev, Operation Sports)."],
          ["Pass Target Distance","10","Weights toward CLOSER teammates. Lower = stops dumping it to the near guard on outlet flicks."],
          ["Pass Target Openness","5","Low = the AI won't override your aim for a 'more open' near teammate."],
          ["Pro Stick Pass Type","Flashy (if listed)","2K24–26 option (Normal/Flashy). In 2K27 Hold R1/RB + RS flick is the no-look pass."],
          ["Hold Lob Pass Button","Skip Pass",""],["Auto Lob to Moving Receiver","Disabled",""]],
 "inputs": [["No-look / Flashy pass (NEW 2K27)","Hold R1 + flick RS","Hold RB + flick RS"],["Icon pass","Tap R1 → receiver's button","Tap RB → receiver's button"],
            ["Normal / Skip","X / hold X","A / hold A"],["Bounce","Tap ○","Tap B"],["Wrap pass","Double-tap ○","Double-tap B"],["Lob / Alley-oop","△ / double-tap △","Y / double-tap Y"],
            ["Touch pass","X again before catch","A again before catch"],["Fake pass","△ + ○","Y + B"]],
 "src": ["https://nba.2k.com/2k27/features/gameplay/","https://howtovideogame.com/nba-2k27-how-to-flashy-pass-and-call-plays/",
         "https://www.operationsports.com/how-to-do-a-flashy-pass-in-nba-2k27/","https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/814065-pass-target-profile",
         "https://www.lockercodes.io/nba-2k/animation-requirements/pass-styles"]}

SOURCES = [["NBA 2K Support: 2K27 Cap Breakers","https://support.nba2k.com/hc/en-us/articles/54428966585875-NBA-2K27-Cap-Breakers"],
 ["LockerCodes cap breakers (28 total)","https://www.lockercodes.io/nba-2k/cap-breakers"],["NBA2KLab badge requirements","https://www.nba2klab.com/badge-requirements"],
 ["NBA2KLab badge token costs","https://www.nba2klab.com/badge-tokens"],["NBA2KLab Fuse & React pairings","https://www.nba2klab.com/fuse-react-badges"],
 ["LGC badge requirements","https://lgcapp.com/game-tools/nba-2k/badges"],["LockerCodes animation requirements","https://www.lockercodes.io/nba-2k/animation-requirements"],
 ["2K Newsroom: Builder / Tokens / Synergy","https://newsroom.2k.com/news/nbar-2k27-myplayer-builder-introduces-female-myplayers-badge-tokens-and-the-all-new-synergy-system"],
 ["Patch 2.0 summary (CourtCraft)","https://www.2k27lab.com/news/2026-10-08"],["Season 2 Synergy reset","https://www.2k27lab.com/news/2026-10-17"]]

for b in BUILDS:
    b["bodyEst"] = b["id"] in ("bandit64","pp70") or b["kind"]=="meta"
data = {"badges": B, "aliases": ALIASES, "attrs": ATTRS, "anims": A, "unverified": UNVERIFIED, "passNotes": PASS_NOTES, "takeovers": TAKEOVERS,
        "cbSources": CB_SOURCES, "pairs": PAIRS_SEEN, "builds": BUILDS, "pass": PASS_PRESET, "cost": COST, "sources": SOURCES,
        "checked": "Oct 28, 2026 · Season 2 · Patch 2.0"}
os.makedirs(ROOT + "/src", exist_ok=True)
json.dump(data, open(ROOT + "/src/data.json", "w"), separators=(",", ":"))
print(len(B), "badges", len(A), "animations", len(BUILDS), "builds", os.path.getsize(ROOT + "/src/data.json"), "bytes")
