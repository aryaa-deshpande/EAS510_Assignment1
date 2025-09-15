import argparse
from pathlib import Path
from forensics_detective import SimpleDetective
import json
from pathlib import Path

import json
GT_PATH = Path("ground_truth.json")

def load_gt():
    return json.loads(GT_PATH.read_text()) if GT_PATH.exists() else {}
# def run_folder(det, folder):
#     folder = Path(folder)
#     print(f"\n=== {folder} ===")
#     for p in sorted(folder.iterdir()):
#         if not p.is_file():
#             continue
#         r = det.find_best_match(str(p))
#         print(f"\nProcessing: {p.name}")
#         for line in r["notes"]:
#             print(line)
#         print(f"Final Score: {r['score']}/100 -> {r['decision']} to {r['target']}")

from pathlib import Path

def run_folder(det, folder, truth=None):
    print(f"\n=== Processing {folder} ===")
    correct, total, false_pos = 0, 0, 0
    gt = truth or {}

    for p in Path(folder).glob("*"):
        if not p.is_file():
            continue

        res = det.find_best_match(str(p))

        # --- PRINT THE RULE REASONING (assignment requires this) ---
        print(f"\nProcessing: {p.name}")
        for line in res["notes"]:
            print(line)
        print(f"Final Score: {res['score']}/100 -> {res['decision']} to {res['target']}")

        # --- METRICS ---
        total += 1
        if "modified" in folder:
            # expected = original filename from GT, e.g. "original_03.jpg"
            expected = gt.get(p.name)
            # predicted = just the name of the matched original (strip any path)
            predicted = Path(res["target"]).name if res["target"] else None
            if expected is not None and res["decision"] == "MATCH" and predicted == expected:
                correct += 1
        elif "random" in folder:
            if res["decision"] == "MATCH":
                false_pos += 1

    if "modified" in folder and total:
        print(f"\nSummary ({folder}): correct={correct}/{total} acc={(100*correct/total):.1f}%")
    if "random" in folder and total:
        print(f"Summary ({folder}): false_positives={false_pos}/{total}")
        print(f"Summary ({folder}): false_positives={false_pos}/{total}")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--originals", default="EAS510_Assignment1/originals")
    ap.add_argument("--modified",  default="EAS510_Assignment1/modified_images")
    ap.add_argument("--random",    default="EAS510_Assignment1/random")
    args = ap.parse_args()

    det = SimpleDetective()
    det.register_targets(args.originals)

    truth = load_gt()
    if Path(args.modified).exists():
        run_folder(det, args.modified, truth)
    if Path(args.random).exists():
        run_folder(det, args.random, truth)

if __name__ == "__main__":
    main()

