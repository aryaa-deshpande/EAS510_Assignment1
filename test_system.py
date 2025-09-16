import argparse
from pathlib import Path
from forensics_detective import SimpleDetective

# run the detector over every image in a folder
def run_folder(det, folder):
    folder = Path(folder)
    print(f"\n=== {folder} ===")
    for p in sorted(folder.iterdir()):
        if not p.is_file():
            continue  # skip subfolders
        # get best match + rule notes for this image
        r = det.find_best_match(str(p))
        print(f"\nProcessing: {p.name}")
        for line in r["notes"]:
            print(line)  # per-rule reasoning
        print(f"Final Score: {r['score']}/100 -> {r['decision']} to {r['target']}")

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

    # run on modified set (should match an original)
    if Path(args.modified).exists():
        run_folder(det, args.modified)

    # run on random set (should be rejected)
    if Path(args.random).exists():
        run_folder(det, args.random)

if __name__ == "__main__":
    main()