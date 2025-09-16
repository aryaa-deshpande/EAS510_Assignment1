from pathlib import Path
from rules import rule_metadata, rule_ssdeep, rule_template

CUTOFF = 60  # score needed to decide a MATCH

class SimpleDetective:
    """
    Load original images and score new images against them using 3 rules.
    """
    def __init__(self):
        # dictionary: original filename -> path
        self.targets = {}

    def register_targets(self, folder):
        # load all originals from a folder
        folder = Path(folder)
        for p in folder.iterdir():
            if p.is_file():
                self.targets[p.name] = str(p)

    def _score_one(self, img_path, target_name):
        # compare one test image against one target image
        tpath = self.targets[target_name]
        notes = []   # keep rule explanations
        total = 0    # running score

        # apply Rule 1: metadata
        s, n = rule_metadata(img_path, tpath)
        total += s; notes.append(n)

        # apply Rule 2: ssdeep fuzzy hash
        s, n = rule_ssdeep(img_path, tpath)
        total += s; notes.append(n)

        # apply Rule 3: template matching
        s, n = rule_template(img_path, tpath)
        total += s; notes.append(n)

        return total, notes

    def find_best_match(self, img_path):
        # compare one test image to all originals and pick the best score
        best_score = -1
        best_name = None
        best_notes = []

        for name in self.targets:
            score, notes = self._score_one(img_path, name)
            if score > best_score:
                best_score, best_name, best_notes = score, name, notes

        # final decision based on cutoff
        decision = "MATCH" if best_score >= CUTOFF else "REJECT"
        return {
            "score": best_score,
            "target": best_name,
            "decision": decision,
            "notes": best_notes,
        }