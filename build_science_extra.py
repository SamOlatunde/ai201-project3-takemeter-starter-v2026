"""Top up the `science` label so the four classes are closer to balanced.

`labels.csv` came out of `build_dataset.py` at 68 politics / 50 hardware /
45 sport / 37 science: the sci.space sample split roughly 2:1 into posts that
explain something and posts that argue about funding, and rule 1 sent the
second group to `politics`. This script draws 27 more sci.space posts that none
of the project files already use, assigns ids ng201-ng227, and appends them to
`data/labels.csv`, `labels.csv` and `data/source_groups.csv`.

Each post is pinned by a phrase from its body rather than by a sample index, so
the selection is reproducible and does not depend on any RNG. Every phrase must
match exactly one eligible post or the script stops.

Labels were assigned by reading each post against `label_definitions.txt`; the
deciding rule is recorded per row in the `note` column, same as the main pass.
Re-running is safe: rows whose id already exists are left untouched.
"""

import csv
import os
import re

from sklearn.datasets import fetch_20newsgroups

CATEGORIES = [
    "rec.sport.baseball",
    "sci.space",
    "comp.sys.mac.hardware",
    "talk.politics.guns",
]
SOURCE_GROUP = "sci.space"
# Higher floor than build_dataset.py's 150: the point of this pass is posts
# with enough mechanism in them to carry signal.
MIN_CHARS = 300
MAX_CHARS = 700

HERE = os.path.dirname(os.path.abspath(__file__))
LABELS = os.path.join(HERE, "data", "labels.csv")
LABELS_COPY = os.path.join(HERE, "labels.csv")
KEY = os.path.join(HERE, "data", "source_groups.csv")

# Files whose post text is already spoken for. A new row must not duplicate any
# of them, or the held-out split and the staff-agreement set stop being clean.
IN_USE = [
    os.path.join(HERE, "data", "labels.csv"),
    os.path.join(HERE, "labels.csv"),
    os.path.join(HERE, "data", "raw_posts.csv"),
    os.path.join(HERE, "data", "staff_posts.csv"),
    os.path.join(HERE, "data", "practice_labels.csv"),
    os.path.join(HERE, "data", "calibration_ten.csv"),
    os.path.join(HERE, "test_split.csv"),
]

# id -> (phrase that uniquely identifies the post, label, note)
PICKS = [
    ("ng201", "designed to be retrievable, in a pinch",
     "science", "rule 2 - spacecraft array design is not computing"),
    ("ng202", "how much time elapses between launch and the pitch over",
     "science", "rule 2 - 'writing a program' is the frame, ascent trajectory is the content; HARD"),
    ("ng203", "they mention the double sonic booms",
     "science", "cold"),
    ("ng204", "radio clutter from malfunctioning spacecraft",
     "science", "cold"),
    ("ng205", "I think the narrative said it was propelled by dynamite sticks",
     "science", "cold"),
    ("ng206", "self armoring system for venus surface conditions",
     "science", "cold"),
    ("ng207", "Uranus is *not* on the way to Neptune",
     "science", "cold"),
    ("ng208", "The wind behaves like a fluid pipe",
     "science", "cold"),
    ("ng209", "lung diaphram gets too tired to pump the liquid",
     "science", "cold"),
    ("ng210", "If you want bomb grade plutonium use a research reactor",
     "science", "rule 1 - compares reactor types on physical grounds, argues no policy; HARD"),
    ("ng211", "matching the position of it in its orbit on a subsequent mission",
     "science", "cold"),
    ("ng212", "total blackbody temperature -- what a thermal radiator would see",
     "science", "cold"),
    ("ng213", "The source of this temperature is the radiation of starlight",
     "science", "cold"),
    ("ng214", "rocket that used ions or nuclear particles for propolsion",
     "science", "rule 1 - mentions the funding decision in passing, asks how the drive works; HARD"),
    ("ng215", "could it be possible that we are actually seeing much less energetic events",
     "science", "cold"),
    ("ng216", "Very Long Baseline Radio Astronomy coupled to GPS",
     "science", "cold"),
    ("ng217", "a high explosive Orion prototype flew",
     "science", "cold"),
    ("ng218", "reenter the atmosphere sort of sideways",
     "science", "cold"),
    ("ng219", "High Temperature Gas Cooled Fission Reactors",
     "science", "rule 1 - reports the pact and explains the fuel cycle, takes no side; HARD"),
    ("ng220", "If the HGA were pointed att he sun",
     "science", "cold"),
    ("ng221", "A Numerical Study of Gravitational Capture Orbit",
     "science", "cold"),
    ("ng222", "a ball floating between sensors",
     "science", "cold"),
    ("ng223", "we have to send a probe there to get gamma ray spectroscopy done",
     "science", "cold"),
    ("ng224", "The motors and electronics are separate pieces of hardware",
     "science", "rule 2 - says 'hardware' about spacecraft motors, not computing; HARD"),
    ("ng225", "unless the Proton has an oversize shroud",
     "science", "cold"),
    ("ng226", "These burst detectors are just that, burst detectors",
     "science", "cold"),
    ("ng227", "suffer multiple holes with no ++disastrous deflation",
     "science", "cold"),
]


def normalise(text):
    return re.sub(r"\s+", " ", text).strip()


def eligible_posts():
    bundle = fetch_20newsgroups(
        subset="all",
        categories=CATEGORIES,
        remove=("headers", "footers", "quotes"),
        random_state=42,
    )
    posts = []
    for text, target in zip(bundle.data, bundle.target):
        if bundle.target_names[target] != SOURCE_GROUP:
            continue
        cleaned = normalise(text)
        if cleaned.count(">") > 2:
            continue
        if MIN_CHARS <= len(cleaned) <= MAX_CHARS:
            posts.append(cleaned)
    return posts


def already_used():
    used = set()
    for path in IN_USE:
        if not os.path.exists(path):
            continue
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("text"):
                    used.add(normalise(row["text"]))
    return used


def read_rows(path, fieldnames):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return [{k: row.get(k, "") for k in fieldnames} for row in csv.DictReader(f)]


def write_rows(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main():
    posts = eligible_posts()
    used = already_used()
    existing_ids = {row["id"] for row in read_rows(LABELS, ["id"])}

    new_rows, new_key_rows = [], []
    for post_id, phrase, label, note in PICKS:
        if post_id in existing_ids:
            continue
        matches = [p for p in posts if phrase in p and p not in used]
        if len(matches) != 1:
            raise SystemExit(
                f"{post_id}: {len(matches)} unused posts match {phrase!r}"
            )
        used.add(matches[0])
        new_rows.append(
            {"id": post_id, "text": matches[0], "label": label, "note": note}
        )
        new_key_rows.append({"id": post_id, "source_group": SOURCE_GROUP})

    if not new_rows:
        print("nothing to add; all ids already present")
        return

    fields = ["id", "text", "label", "note"]
    rows = read_rows(LABELS, fields) + new_rows
    write_rows(LABELS, fields, rows)
    write_rows(LABELS_COPY, fields, rows)

    key_fields = ["id", "source_group"]
    write_rows(KEY, key_fields, read_rows(KEY, key_fields) + new_key_rows)

    counts = {}
    for row in rows:
        counts[row["label"]] = counts.get(row["label"], 0) + 1
    print(f"added {len(new_rows)} rows -> {len(rows)} total")
    for label in sorted(counts, key=lambda k: -counts[k]):
        print(f"  {label:9} {counts[label]}")


if __name__ == "__main__":
    main()
