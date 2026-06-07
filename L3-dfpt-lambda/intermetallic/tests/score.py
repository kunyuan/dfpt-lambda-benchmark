#!/usr/bin/env python3
"""Score L3 λ predictions vs the paper reference (gold). λ within TOL; ω_log within TOL if gold present."""
import argparse, csv, json, sys
TOL=0.15
def rd(p):
    with open(p) as f: return {r["case_id"]:r for r in csv.DictReader(f)}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--pred",required=True); ap.add_argument("--gold",required=True); ap.add_argument("--json",default="result.json")
    a=ap.parse_args(); gold=rd(a.gold); pred=rd(a.pred)
    if set(pred)!=set(gold):
        print(f"FAIL: ids {sorted(pred)} != gold {sorted(gold)}"); json.dump({"pass":False,"error":"id mismatch"},open(a.json,"w")); sys.exit(1)
    ok=True; res=[]; cost=0.0
    for cid,g in sorted(gold.items()):
        lg=float(g["lambda"]); p=pred[cid]
        try: lp=float(p["lambda"])
        except Exception as e: print(f"FAIL {cid}: bad row {e}"); json.dump({"pass":False},open(a.json,"w")); sys.exit(1)
        dl=abs(lp-lg)/abs(lg); passed=dl<=TOL; msg=f"  {cid}: λ {lp} vs {lg} ({dl:+.1%})"
        if g.get("omega_log_K"):
            try:
                wg=float(g["omega_log_K"]); wp=float(p.get("omega_log_K","nan")); dw=abs(wp-wg)/abs(wg)
                passed=passed and dw<=TOL; msg+=f"  ω_log {wp} vs {wg} ({dw:+.1%})"
            except Exception: passed=False; msg+="  ω_log MISSING"
        try: cost+=float(p.get("core_hours","nan"))
        except Exception: pass
        ok=ok and passed; res.append({"case_id":cid,"pass":passed}); print(msg+f" -> {'PASS' if passed else 'FAIL'}")
    print(f"\ntotal cost: {cost:g} core-hours (reported)\nRESULT: {'PASS' if ok else 'FAIL'}")
    json.dump({"pass":ok,"tolerance":TOL,"total_core_hours":cost,"cases":res},open(a.json,"w"),indent=2)
    sys.exit(0 if ok else 1)
if __name__=="__main__": main()
