# Acceptance criteria — TakeMeter

Five criteria that say what "working" means for this classifier, written in
unit 5 **before** anything was trained.

**All five are yours this time.** None are given. You've had two projects of
practice.

An acceptance criterion names a number. *"The model is accurate"* is an
opinion. *"Every label has an F1 of at least 0.60 on the held-out set"* is a
criterion.

Under each, write a sentence or two on **why that number**. A reason that says
something about your data or your taxonomy earns credit — *"I picked 0.60 F1
for `reaction` because it's my smallest label and I only have about 50
examples of it"*. A reason that could be attached to any project does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

Not numbers that sound impressive. Three labels means a coin-flip guesser gets
about 33%, so a target of 0.40 is barely a target. Your number should sit
somewhere you'd honestly call useful.

**Cover at least three of these five areas.** They're here as prompts, not as a
form to fill in — a criterion that fits none of them is fine if it names a
number.

| Area | A question it could answer |
|---|---|
| Overall accuracy | How often does it need to be right to be worth using? |
| Per-label performance | Is one label allowed to be much worse than the others? |
| Balance | How lopsided can your label counts get before it's a problem? |
| Consistency | If someone else labelled the same posts, how often should you agree? |
| Confidence | Should a confident prediction be right more often than an unsure one? |

Two things worth knowing before you pick numbers, because both will affect
whether you hit them:

- **Your smallest label will have the jumpiest score.** If a label has 50
  examples, about 8 land in the test split. An F1 computed on 8 examples moves
  a lot between seeds. A target for that label should be looser than one for
  your biggest label, and saying so is a good reason.
- **Unit 6 tests across three seeds, and the target has to hold across all
  three.** A target of 0.65 against results of 0.71, 0.62, 0.68 is a **miss**.
  Pick with that in mind — it is stricter than it first sounds.

---

## 1. Overall accuracy of at least 90 percent on the held-out test set, on all three seeds

<!-- Your criterion. It must name a number. -->



**Why this target:** The four labels come from four newsgroups with almost no
shared vocabulary — Powerbooks, box scores, orbits, the Second Amendment — so a
model that can't clear 90 isn't reading the obvious signal. The split is
stratified, 10 posts per label in the test set, so 90 percent means at most 4
errors out of 40. I'm holding it across all three seeds because one lucky split
isn't evidence.



---

## 2. Labelling a 25-post sample a second time, we disagree on at most 1 post

<!-- Your criterion. -->



**Why this target:** The definitions plus decision rules 1-4 settle every case I
found while building the set, including the posts where topic and argument pull
apart (ng011, ng028, ng055, ng103, ng139). What they don't settle is rule 5, the
tie-break on word count — that one asks for a judgment two people can make
differently. One disagreement out of 25 is room for exactly that, and no more.



---

## 3. Every label's F1 is within 0.10 of the best label's F1, on all three seeds

<!-- Your criterion. -->



**Why this target:** Counts are exactly 50/50/50/50 and the split is stratified,
so no label is starved of training examples and none is favoured by a majority
prior. If one label still trails the best by more than 0.10, that's the taxonomy
leaking, not the data. I expect `politics` to be the one at risk, because rule 1
pulls cross-cutting posts into it from all three other topics.



---

## 4. Of predictions where the top class probability is at least 0.80, at least 90 percent are correct

<!-- Your criterion. -->



**Why this target:** A confidence score is only worth having if I can act on it,
so the threshold has to be named — 0.80 is where I'd be willing to skip a manual
check. The risk this criterion is actually testing: the posts that break rule 1
are topically unambiguous. A gun-control post arguing from medical evidence
*looks* like confident `science`. If my wrong predictions are the confident ones,
this is where it shows up.



---

## 5. Each label's predicted share of the test set is within 8 points of 25 percent, on all three seeds

<!-- Your criterion. -->



**Why this target:** Stratifying makes the test set exactly 10 per label, so the
true share is 25 percent by construction and any skew in the predictions is the
model's bias rather than the luck of the draw. 8 points is 3 posts out of 40 —
tight enough to catch a model that's collapsing toward one label, loose enough
that ordinary single-post errors don't trip it.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 6 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Every label performs acceptably

         The model performs well on all labels.

         **Why this target:** ...

         > **Revised in unit 6:** Every label has an F1 of at least 0.60 on
         > the held-out set.
         >
         > **Why revised:** "performs well" gave me nothing to check. I
         > couldn't produce a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "Overall accuracy of at least 0.65" → "at least 0.55", because
            0.65 turned out to be optimistic for 200 examples.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
