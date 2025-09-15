from pathlib import Path
from rules import rule_metadata, rule_ssdeep, rule_template

CUTOFF = 60  # final score needed to call it a MATCH

class SimpleDetective:
    """
    Load originals and score any image against them with 3 rules.
    """
    def __init__(self):
        self.targets = {}  # name -> path

    def register_targets(self, folder):
        folder = Path(folder)
        for p in folder.iterdir():
            if p.is_file():
                self.targets[p.name] = str(p)

    def _score_one(self, img_path, target_name):
        tpath = self.targets[target_name]
        notes = []
        total = 0

        s, n = rule_metadata(img_path, tpath); total += s; notes.append(n)
        s, n = rule_ssdeep(img_path, tpath);   total += s; notes.append(n)
        s, n = rule_template(img_path, tpath); total += s; notes.append(n)

        return total, notes

    def find_best_match(self, img_path):
        best_score = -1
        best_name = None
        best_notes = []

        for name in self.targets:
            score, notes = self._score_one(img_path, name)
            if score > best_score:
                best_score, best_name, best_notes = score, name, notes

        decision = "MATCH" if best_score >= CUTOFF else "REJECT"
        return {
            "score": best_score,
            "target": best_name,
            "decision": decision,
            "notes": best_notes,
        }