# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Your community, and what your classifier sorts posts into. Three or four
     sentences. -->

The community is Usenet in 1993 — four long-running discussion groups
(`rec.sport.baseball`, `sci.space`, `comp.sys.mac.hardware`,
`talk.politics.guns`) as preserved in the 20 Newsgroups archive. TakeMeter
sorts a post into one of four labels: `sport`, `science`, `hardware` and
`politics`.

The four labels are deliberately **not** the four newsgroups. A post that
argues a space programme should be cancelled is `politics` even though it was
posted to `sci.space`, and a post working through the physics of a fire is
`science` even though it was posted to a gun group. The classifier is meant to
sort by what a post is *doing*, not by where it was filed.


---

## Label Taxonomy

<!-- Each label: a one-sentence definition and two real examples from your
     reading. Then your decision rule for the hardest boundary.

     The decision rule is worth a point on its own and it's the thing most
     people leave out. Every taxonomy has a hardest boundary. Name yours. -->

### `sport`

**Definition:** Discusses athletic competition — games, players, teams,
standings or results; look for team and player names, scores, box-score lines
and league structure.

**Example 1:** (`ng043`)
> The only effect the infield fly has is to make the batter out, thereby
> removing the force on the runners on base.

**Example 2:** (`ng144`)
> What I would suggest is perhaps batting Bonds, Williams, and Clark 3-4-5, the
> reason being that I feel Bonds' potential basestealing abilities are wasted
> when he's stuck behind two slow runners.

### `science`

**Definition:** Explains or discusses how something in the natural world works
— space, physics, chemistry, medicine; look for mechanisms, measurements,
observations or experimental results.

**Example 1:** (`ng124`)
> Vulcan as a planet inside Mercury was hypothesized to explain a perturbation
> of Mercury's orbit that could not be explained by the known planets.

**Example 2:** (`ng112`)
> Any lunar satellite needs fuel to do regular orbit corrections, and when its
> fuel runs out it will crash within months.

### `hardware`

**Definition:** Discusses computing or information technology — machines,
components, peripherals, software or engineering practice; look for product
names, specifications, configuration problems and troubleshooting.

**Example 1:** (`ng045`)
> I have an external drive connected to my IIsi. This is never recognized and
> mounted on system startup. I can mount it with the SCSI control panel.

**Example 2:** (`ng128`)
> I bought a StyleWriter II a couple months ago, and lately, when I print
> something, I notice white lines or "gaps" running through the line being
> printed.

### `politics`

**Definition:** Argues for or against a policy, law or official decision — what
should be funded, cancelled, banned or negotiated; look for advocacy, rights
claims, and references to legislation, agencies and officials.

**Example 1:** (`ng172`)
> In Texas, it is legal to carry handguns while "traveling", and also to and
> from sporting activities. Chapter 46 of the Texas State Penal Code does NOT
> restrict long guns.

**Example 2:** (`ng186`) — a space post that is `politics`, not `science`:
> if you launch this from the US (or are a US citizen), you will need a launch
> permit from the Office of Commercial Space Transportation [...] The threshold
> at which OCST licensing kicks in is roughly 100km.

### The hardest boundary

**Which two labels:** `science` vs `politics`.

Almost every space post sits near this line. The same subject — a launcher, a
telescope, a lunar base — appears both as a thing being explained and as a
thing being argued over, often in the same thread and sometimes by the same
poster.

**The decision rule I used every time:**

> **What the post argues for decides, not what it is about.** A post that
> explains a mechanism is `science` even when the subject is a government
> programme. A post that argues something should be funded, cancelled, licensed
> or banned is `politics` even when the subject is orbital mechanics.

The cleanest pair this produced is `ng141` and `ng196`, both about projecting
advertising onto the sky. `ng141` asks whether a laser could do it — a question
about what is physically possible, so `science`. `ng196` asks whether it is
*desirable* and attacks the people who want it, so `politics`. Same topic,
different act, different label.

The rule also runs the other way, which is what makes it do work: `ng002`
reasons carefully about the combustion physics of CS gas, but it does so to
rebut the FBI's account of a fire, so it is `politics`, not `science`.


---

## The Dataset

<!-- Where you collected from, how you labelled, your counts, and three hard
     cases. -->

**Where the posts came from:** The 20 Newsgroups archive, via
`sklearn.datasets.fetch_20newsgroups`, restricted to four groups
(`rec.sport.baseball`, `sci.space`, `comp.sys.mac.hardware`,
`talk.politics.guns`). `build_dataset.py` strips headers, footers and quoted
text, drops anything with more than two `>` lines, keeps posts between 150 and
700 characters, samples 50 per group under seed 42 and shuffles them into ids
`ng001`–`ng200`. Eleven posts had no topical content left once decision rule 4
stripped the signature block — a typo correction, a Star Trek aside, an apology
for a late reply — and each was swapped for another post from the same group.

**How I labelled them:** Twice, and the first pass was a failure worth
recording. I labelled the first 10 posts by hand and then had an AI pre-label
the remaining 190, which I did not then check post by post. That file looked
finished and was not: the fine-tune trained on it scored **23% accuracy on four
labels**, which is below the 25% a coin-flip guesser gets. The labels carried no
signal for the model to learn, because they did not match the posts — `ng028`,
on Mercury's perihelion and general relativity, was labelled `politics`;
`ng054`, on the Milt Pappas–Frank Robinson trade, was labelled `hardware`.
The second pass re-labelled all 200 from the post text against the written
definitions and the five decision rules, recording in the `note` column which
rule decided each non-obvious case. 140 of the 200 labels changed. 130 rows are
marked `cold` (the label was plain from the post), 51 cite a specific decision
rule, and 23 are flagged `HARD` or `THIN` for the reasons given there.

**Counts per label:**

| Label | Count | Share |
|---|---|---|
| `politics` | 68 | 34.0% |
| `hardware` | 50 | 25.0% |
| `sport` | 45 | 22.5% |
| `science` | 37 | 18.5% |
| **Total** | **200** | 100% |

`politics` is the largest because decision rule 1 is deliberately aggressive: it
pulls space-funding arguments, Waco-conduct posts and gun-law posts in from
every other topic. `science` is the smallest at 37, which means about 6 land in
any test split — its F1 will be the jumpiest number I have.

**Three hard cases**

**1.**
> *The post:* `ng104` — "I thought we were discussing the need to shorten games.
> The arguments which declare this need seem to hinge on the assertion that long
> games bore people [...] If it hasn't, then there *isn't* a problem, and
> there's no need to monkey with things as they are."
>
> *Could have been:* `sport` or `politics`.
>
> *I chose `politics`, because:* my own `sport` definition ends with the
> sentence "A post arguing for a policy about sport is politics, not sport."
> This post argues against a proposed rule change and demands attendance
> evidence before anyone changes anything. The subject is baseball; the act is
> arguing a policy. The rule I wrote decides it against the topic, which is
> exactly what it is for.

**2.**
> *The post:* `ng141` — "I have often thought about, if its possible to have a
> powerfull laser on earth, to light at the Moon, and show lasergraphics at the
> surface so clearly that you can see it with your eyes [...] How about a Coca
> Cola logo at the moon, easy way to target billions of people. Do you know if
> its possible?"
>
> *Could have been:* `science` or `politics`.
>
> *I chose `science`, because:* the post asks whether the thing can be done, not
> whether it should be. It sits in the same orbital-advertising argument as
> `ng015`, `ng101` and `ng196`, all three of which I labelled `politics` — those
> three attack the practice, this one asks about the physics. Rule 1 says what
> the post argues for decides, and this post argues for nothing.

**3.**
> *The post:* `ng197` — "If there is a 'USA Today ftp site' could someone please
> post it to the newsgroup so everyone will stop posting the 'send it to me too'
> articles."
>
> *Could have been:* `sport` or `hardware`.
>
> *I chose `hardware`, because:* the poster wants baseball statistics, so the
> motive is `sport` — but rules 1–3 do not reach this post, and rule 5 says to
> pick the label the post spends most of its words on. Those words are about an
> ftp site and newsgroup posting etiquette, not about baseball. This is the one
> of the three I am least sure of, and I have left it flagged in `labels.csv`.


---

## The Training Run

<!-- Your starting model, your settings, and anything you changed and why. -->

**Base model:** `distilbert-base-uncased`

**Settings:** 3 epochs, learning rate 2e-5, batch size 16, max length 128
tokens, seed 42.

**Anything I changed from the defaults, and why:** Nothing. The first run and
the second run used identical settings — the only thing that changed between
23% accuracy and 86.7% was the labels. That is the finding of this unit for me:
the settings were never the variable worth touching.

**Split sizes:** Stratified 70/15/15 — **139 train / 31 val / 30 test**.

| Label | train | val | test |
|---|---|---|---|
| `science` | 25 | 6 | 6 |
| `sport` | 31 | 7 | 7 |
| `politics` | 48 | 10 | 10 |
| `hardware` | 35 | 8 | 7 |

Three of the four labels have fewer than 8 examples in the test split —
`science` 6, `sport` 7, `hardware` 7. Only `politics` clears it, at 10. An F1
computed on 6 posts moves by 0.17 if a single post flips, so I expect `science`
to swing hardest across the three seeds next unit, and I am writing that down
now rather than discovering it then.


---

## How I Used AI

<!-- Two specific moments — what you asked, what came back, what you changed.

     ⚠️ Plus disclosure of any pre-labelling. If you had a model pre-label a
     batch and then read and corrected every one, say that. It's an allowed
     workflow and disclosing it costs you nothing. Not disclosing it is the
     problem. -->

**Moment 1**

- *What I asked for:* help finding a dataset I could actually label by hand — a
  real community with enough posts, short enough to read, and with boundaries
  that would not be trivial.
- *What came back:* the 20 Newsgroups archive, with the suggestion of four
  groups whose topics look separable but whose posts overlap in practice, plus
  the `build_dataset.py` sampling script — length filters, the quoted-text
  filter, a fixed seed, and the `REPLACEMENTS` map for posts left empty by rule
  4.
- *What I changed:* I removed post that only had signature. 

**Moment 2**

- *What I asked for:* why my accuracy was so low — 23% on four labels, with the
  model never once predicting `science` or `sport`.
- *What came back:* the diagnosis that it was not a model problem at all. The
  labels carried no signal: the confusion matrix against the posts' actual topic
  was flat, and rows I had marked `cold` — where I recorded applying no decision
  rule — matched the obvious subject of the post only 23% of the time. It also
  checked whether the file was merely misaligned, testing all 200 rotational
  offsets; the best scored 66/200, so there was no shift to undo and no clean
  copy to recover.
- *What I changed:* I re-labelled all 200 posts against the written definitions
  rather than trying to repair the file, and I re-sourced the example ids in
  `label_definitions.txt`, which had been drawn from the broken pass and pointed
  at unrelated posts — rule 1 cited `ng028`, which is pure orbital physics, and
  rule 3 cited `ng040`, which is about Waco.

**Pre-labelling disclosure:**

Both label passes were AI-assisted, and neither was done entirely by hand.

- **First pass:** I labelled `ng001`–`ng010` myself and had an AI pre-label
  `ng011`–`ng200`. I did not read and correct those 190 post by post. That is
  what produced the 23% run. For what it is worth, my own hand-labelled ten were
  not meaningfully better than the AI's 190 when re-checked — 4/10 against 29%
  — so I am not claiming the hand pass was sound either.
- **Second pass:** all 200 labels in the current `labels.csv` were produced by
  an AI reading each post against `label_definitions.txt`, with the deciding
  rule recorded per row in the `note` column. I reviewed the 23 rows it flagged
  `HARD` or `THIN` and the three hard cases written up above. The post text and
  ids were not altered — only the `label` and `note` columns changed, and that
  is verifiable against commit `08023ae`.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy |  |  |  |
| Macro F1 |  |  |  |
| F1 — `label_one` |  |  |  |
| F1 — `label_two` |  |  |  |

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->



---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted |  |  |  |
|---|---|---|---|
| **** |  |  |  |
| **** |  |  |  |
| **** |  |  |  |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->



---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** ___ / 30 = ___%

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**2.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**What the pattern in my disagreements tells me:**



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->



**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
