import csv
import os
import random
import re

from sklearn.datasets import fetch_20newsgroups

CATEGORIES = [
    "rec.sport.baseball",
    "sci.space",
    "comp.sys.mac.hardware",
    "talk.politics.guns",
]
PER_CLASS = 50
MIN_CHARS = 150
MAX_CHARS = 700

# Eleven of the sampled posts had no topical content left once decision rule 4
# stripped the signature block — a typo correction, a Star Trek aside, an
# apology for a late reply. Nothing can label those, so each is swapped for
# another post from the same newsgroup, identified by a phrase from its body.
# Replacements are held to a higher floor than MIN_CHARS so none of them is
# thin in the same way.
MIN_REPLACEMENT_CHARS = 300
REPLACEMENTS = {
    "ng017": ("rec.sport.baseball", "home of the AAA Richmond Braves"),
    "ng085": ("talk.politics.guns", "conspiracy on our hands"),
    "ng097": ("talk.politics.guns", "If the body had been denatured"),
    "ng112": ("sci.space", "lunar satellite needs fuel to do regular orbit"),
    "ng124": ("sci.space", "Vulcan as a planet inside Mercury"),
    "ng127": ("sci.space", "interstellar grains are very poor radiators"),
    "ng129": ("sci.space", "Atlas was the first-generation US ICBM"),
    "ng137": ("sci.space", "differential arrival time techinique"),
    "ng152": ("sci.space", "mechanical chest compression"),
    "ng153": ("sci.space", "Proton has been used in 2, 3, and 4 stage"),
    "ng154": ("sci.space", "Orion concept as actually proposed"),
}

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "raw_posts.csv")
KEY = os.path.join(HERE, "data", "source_groups.csv")

bundle = fetch_20newsgroups(
    subset="all",
    categories=CATEGORIES,
    remove=("headers", "footers", "quotes"),
    random_state=42,
)

cleaned_posts = []
for text, target in zip(bundle.data, bundle.target):
    cleaned = re.sub(r"\s+", " ", text).strip()
    if cleaned.count(">") > 2:
        continue
    # target indexes bundle.target_names (sorted), not CATEGORIES
    cleaned_posts.append((bundle.target_names[target], cleaned))

by_class = {name: [] for name in CATEGORIES}
for name, cleaned in cleaned_posts:
    if MIN_CHARS <= len(cleaned) <= MAX_CHARS:
        by_class[name].append(cleaned)

print("eligible after length+quote filter:")
for name, items in by_class.items():
    print(f"  {name:28} {len(items)}")

rng = random.Random(42)
rows = []
for name in CATEGORIES:
    pool = by_class[name]
    picked = rng.sample(pool, PER_CLASS)
    for text in picked:
        rows.append({"text": text, "source_group": name})

rng.shuffle(rows)
for i, row in enumerate(rows, start=1):
    row["id"] = f"ng{i:03d}"

sampled = {row["text"] for row in rows}
for row in rows:
    if row["id"] not in REPLACEMENTS:
        continue
    group, phrase = REPLACEMENTS[row["id"]]
    matches = [
        cleaned
        for name, cleaned in cleaned_posts
        if name == group
        and MIN_REPLACEMENT_CHARS <= len(cleaned) <= MAX_CHARS
        and cleaned not in sampled
        and phrase in cleaned
    ]
    if len(matches) != 1:
        raise SystemExit(
            f"{row['id']}: {len(matches)} posts match {phrase!r} in {group}"
        )
    row["text"] = matches[0]
    sampled.add(matches[0])

if len({row["text"] for row in rows}) != len(rows):
    raise SystemExit("duplicate post text after replacement")

# Labelling is the slow part, so never clobber it: carry label and note across
# by id. The id -> text mapping is fixed by the seed and REPLACEMENTS above.
existing = {}
if os.path.exists(OUT):
    with open(OUT, newline="", encoding="utf-8") as f:
        for old in csv.DictReader(f):
            existing[old["id"]] = (old.get("label", ""), old.get("note", ""))

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id", "text", "label", "note"])
    w.writeheader()
    for row in rows:
        label, note = existing.get(row["id"], ("", ""))
        w.writerow(
            {"id": row["id"], "text": row["text"], "label": label, "note": note}
        )

with open(KEY, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id", "source_group"])
    w.writeheader()
    for row in rows:
        w.writerow({"id": row["id"], "source_group": row["source_group"]})

lengths = sorted(len(r["text"]) for r in rows)
labelled = sum(1 for r in rows if existing.get(r["id"], ("", ""))[0])
print(f"\nwrote {len(rows)} rows -> {OUT}")
print(f"chars: min {lengths[0]}, median {lengths[len(lengths)//2]}, max {lengths[-1]}")
print(f"labels carried over: {labelled}/{len(rows)}")
