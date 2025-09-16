import argparse
import json
from pathlib import Path
from forensics_detective import SimpleDetective

GROUND_TRUTH_PATH = Path("EAS510_Assignment1/ground_truth.json")

def load_gt():
    # ground truth: modified filename -> original filename
    return json.loads(GROUND_TRUTH_PATH.read_text()) if GROUND_TRUTH_PATH.exists() else {}

# run the detector over every image in a folder and keep simple stats
def run_folder(det, folder, truth=None):
    folder = Path(folder)
    print(f"\n=== {folder} ===")

    stats = {"total": 0, "correct": 0, "false_positives": 0}
    is_modified = "modified" in str(folder)
    is_random = "random" in str(folder)
    gt = truth or {}

    for p in sorted(folder.iterdir()):
        if not p.is_file():
            continue  # skip subfolders

        r = det.find_best_match(str(p))

        # per-image log (same as before)
        print(f"\nProcessing: {p.name}")
        for line in r["notes"]:
            print(line)  # rule reasoning
        print(f"Final Score: {r['score']}/100 -> {r['decision']} to {r['target']}")

        # update counters
        stats["total"] += 1
        if is_modified:
            # correct only if it's a MATCH to the expected original filename
            expected = gt.get(p.name)  # e.g., "original_12.jpg"
            predicted = Path(r["target"]).name if r["target"] else None
            if expected and r["decision"] == "MATCH" and predicted == expected:
                stats["correct"] += 1
        elif is_random:
            if r["decision"] == "MATCH":
                stats["false_positives"] += 1

    # folder-level summaries (useful while debugging)
    if is_modified and stats["total"]:
        acc = 100.0 * stats["correct"] / stats["total"]
        print(f"\nSummary ({folder}): correct={stats['correct']}/{stats['total']} acc={acc:.1f}%")
    if is_random and stats["total"]:
        print(f"Summary ({folder}): false_positives={stats['false_positives']}/{stats['total']}")

    return stats

def main():
    # CLI paths (default to the assignment folders)
    ap = argparse.ArgumentParser()
    ap.add_argument("--originals", default="EAS510_Assignment1/originals")
    ap.add_argument("--modified",  default="EAS510_Assignment1/modified_images")
    ap.add_argument("--random",    default="EAS510_Assignment1/random")
    args = ap.parse_args()

    # load originals once
    det = SimpleDetective()
    det.register_targets(args.originals)

    # load ground truth map (for accuracy on modified set)
    truth = load_gt()

    # run folders
    mod_stats = {"total": 0, "correct": 0}
    rand_stats = {"total": 0, "false_positives": 0}

    if Path(args.modified).exists():
        mod_stats = run_folder(det, args.modified, truth)
    if Path(args.random).exists():
        rand_stats = run_folder(det, args.random, truth)

    # always print the final two lines (what the grader looks for)
    print("\n=== Final Summary ===")
    print(f"Modified images: {mod_stats.get('correct',0)}/{mod_stats.get('total',0)}")
    print(f"Random images false positives: {rand_stats.get('false_positives',0)}/{rand_stats.get('total',0)}")

if __name__ == "__main__":
    main()