import argparse
from pathlib import Path
from forensics_detective import SimpleDetective

def run_folder(det, folder):
    folder = Path(folder)
    print(f"\n=== {folder} ===")
    for p in sorted(folder.iterdir()):
        if not p.is_file():
            continue
        r = det.find_best_match(str(p))
        print(f"\nProcessing: {p.name}")
        for line in r["notes"]:
            print(line)
        print(f"Final Score: {r['score']}/100 -> {r['decision']} to {r['target']}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--originals", default="EAS510_Assignment1/originals")
    ap.add_argument("--modified",  default="EAS510_Assignment1/modified_images")
    ap.add_argument("--random",    default="EAS510_Assignment1/random")
    args = ap.parse_args()

    det = SimpleDetective()
    det.register_targets(args.originals)

    if Path(args.modified).exists():
        run_folder(det, args.modified)
    if Path(args.random).exists():
        run_folder(det, args.random)

if __name__ == "__main__":
    main()