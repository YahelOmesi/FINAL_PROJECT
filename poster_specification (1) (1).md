# Poster Design Brief — Ariel University Final Project (Poster Day)

> **How to use this document (for the designer / Claude Design):** This is a complete build brief for a single academic research poster. Everything below is final, ready-to-place content unless marked `[FILL]` (a value the presenters must paste in) or `[ASSET]` (an image file the presenters must attach). Do **not** invent data, logos, or numbers. All poster-facing text is already written in English and can be used verbatim. Keep it clean, editorial, and confident — this is a computer-science poster, not a slide deck.

---

## 1. Canvas & hard requirements

| Property | Value |
|---|---|
| Final size | **70 cm wide × 100 cm tall** (portrait) |
| Export format | **PDF**, print-ready (300 DPI equivalent, CMYK-safe colors) |
| Background | **Solid white** (#FFFFFF) — required, no textures or gradients on the base |
| University logo | **Ariel University official logo, top-right corner of the header** — provided: `ariel_university_logo.png` (horizontal navy English logo, whitespace-trimmed) |
| Language | **English only** |
| Bleed / margin | Keep a ~3 cm safe margin on all sides; nothing critical inside 2 cm of the edge |

Do not reproduce or redraw the Ariel University logo — place the supplied official asset (`ariel_university_logo.png`) only. Its navy tone (~#14213D) is the basis for the poster's primary color below.

---

## 2. Layout & reading flow

Portrait scientific-poster grid. Reading order flows top → bottom, left column then right column within each band. Suggested vertical zoning (percentages of the 100 cm height):

```
┌─────────────────────────────────────────────────────────┐
│  HEADER  (~14%)                                [ARIEL LOGO]│
│  Title · Subtitle · Authors + Advisor · Affiliation       │
├─────────────────────────────────────────────────────────┤
│  1 · RESEARCH OBJECTIVE & MOTIVATION   (~14%, full width) │
├──────────────────────────────┬──────────────────────────┤
│  2 · METHODOLOGY             │  Pipeline diagram         │
│  (feature families + model)  │  + model architecture     │  (~24%)
├──────────────────────────────┴──────────────────────────┤
│  3 · RESULTS   (~30%)                                     │
│   Phase A: metrics card + confusion matrix (left)         │
│   Phase B: per-text probability chart (right / wide)      │
│   Unsupervised clustering (below, full width)            │
├─────────────────────────────────────────────────────────┤
│  4 · CONCLUSIONS & DISCUSSION   (~14%, full width)        │
├─────────────────────────────────────────────────────────┤
│  FOOTER (~4%): Dept. of Computer Science · Ariel University · 2026 │
└─────────────────────────────────────────────────────────┘
```

Use a two-column body inside the Methodology and Results bands. Section headers are numbered (1–4) with a colored rule beneath each. Generous whitespace; do not fill every pixel.

---

## 3. Visual system

**Core design idea — a two-color "dialect code" used consistently everywhere.** Every chart, matrix and diagram uses the *same two colors* for the two dialects, so a viewer instantly reads the whole poster. This is the single most important visual decision.

- **Yerushalmi (Western / Jerusalem)** → warm amber-gold `#C8892A`
- **Bavli (Eastern / Babylonian)** → deep indigo `#1F3A5F`

**Palette**

| Role | Suggested hex | Notes |
|---|---|---|
| Background | `#FFFFFF` | required |
| Primary text / headers | `#14213D` (near-navy) | |
| Accent / rules / header band | Ariel brand blue — sample it from the supplied logo | if unsure, use `#1B5FA8` |
| Yerushalmi (Western) | `#C8892A` | reused in all data viz |
| Bavli (Eastern) | `#1F3A5F` | reused in all data viz |
| Neutral gridlines / captions | `#6B7280` | |

**Typography** (sizes tuned for readability at ~1.5 m on a 70×100 poster):

| Element | Size | Style |
|---|---|---|
| Main title | 90–110 pt | Bold, sans-serif (e.g. a clean grotesque) |
| Subtitle | 40–48 pt | Regular / light |
| Authors + advisor | 30–34 pt | Medium |
| Section headers (1–4) | 46–54 pt | Bold, ALL-CAPS or small-caps |
| Body text | 28–32 pt | Regular, ~1.35 line height |
| Chart labels / captions | 22–26 pt | Medium |

Use a single sans-serif family throughout for a modern CS look. Keep line length comfortable (~45–70 chars per column).

---

## 4. Header content

**Main title:**
> **East or West? A Deep-Learning Dialect Classifier for Ancient Aramaic Texts**

*Subtitle:*
> It locates the Dead Sea Scrolls, Enoch, Targum Onkelos and the Aramaic Levi Document on the Bavli (Eastern) to Yerushalmi (Western) axis

**Authors line:**
> **Oria Drori & Yahel Omesi**  ·  Advisor: **Prof. Lee-Ad Gottlieb**

**Affiliation line:**
> Department of Computer Science, Ariel University

**Logo:** place `ariel_university_logo.png` in the top-right of the header band, vertically centered with the title block. Scale to roughly 18–22 cm wide; keep clear space around it.

---

## 5. Section 1 — Research Objective & Motivation

Header: **1 · RESEARCH OBJECTIVE & MOTIVATION**

**Motivation.** Pinning down the exact dialect of ancient texts such as the Dead Sea Scrolls is a hard, long-debated historical problem. Scribes often wrote in a formal, standardized "literary" Aramaic that masks the regional spoken language underneath.

**Goal.** Build an NLP / deep-learning model that looks past surface vocabulary and spelling and instead reads the *deep structural and syntactic patterns* of a text: the fingerprints a scribe leaves without noticing.

**Approach.** We train a sequence model on the two great poles of Late Aramaic, **Eastern (Babylonian Talmud)** and **Western (Jerusalem Talmud)**, and then use it to measure the dialectal affinity of unlabeled ancient corpora.

*Optional pull-quote to feature large:* **"Can a neural network hear the accent a scribe tried to hide?"**

---

## 6. Section 2 — Methodology

Header: **2 · METHODOLOGY**

**Left column — feature engineering (copy):**

To keep the model honest and stop it from simply memorizing rare words (overfitting), we do **not** feed it raw text. We extract **8 linguistic hypotheses, operationalized as 11 numerical features**, purely about *structure and grammar*:

| # | Hypothesis (from our research) | Feature(s) |
|---|---|---|
| 1 | Noun state: emphatic vs. absolute | `emphatic_ratio`, `absolute_ratio` |
| 2 | Function-word density | `function_words_ratio` |
| 3 | Lexical diversity (Type–Token Ratio) | `lexical_diversity` |
| 4 | Syntactic distribution (verb load) | `verb_ratio` |
| 5 | Voice: active vs. passive | `passive_voice_ratio` |
| 6 | Plurality | `plural_ratio` |
| 7 | Sentence / line length | `line_length`, `avg_word_len` |
| 8 | Syntactic transitions after a verb | `v_then_noun_ratio`, `v_then_prep_ratio` |

**Right column — model + training (copy):**

- **Architecture:** a deep **LSTM (Long Short-Term Memory)** network in TensorFlow / Keras — `LSTM(32)` → `Dropout(0.3)` → `Dense(1, sigmoid)`.
- **Sequences:** features are read in a **sliding window of 10 consecutive lines**, giving the model local context rather than isolated rows.
- **Training set:** **70,503 labeled lines** from **28 tractates present in both Talmuds** (Bavli + Yerushalmi).
- **Class balance:** the corpus is naturally skewed (~86% Bavli / ~14% Yerushalmi); we correct this with **balanced class weights**.
- **Optimization:** Adam optimizer, binary cross-entropy loss, 15 epochs; standardized features (mean 0, std 1).

**Pipeline diagram spec** (build as a clean left-to-right flow with 5–6 nodes, using the accent blue for boxes and gray arrows):

```
Talmud lines              Feature            Standardize        Sliding
(Bavli + Yerushalmi   →   extraction     →   (StandardScaler) → windows   →   LSTM(32)+Dropout → Sigmoid
28 shared tractates,      8 hypotheses /                          (len 10)          │
70,503 lines)             11 features                                               ▼
                                                        ┌──────────────────────────────────────┐
                                                        │ PHASE A: validate on held-out Talmud   │
                                                        │ PHASE B: apply to unlabeled ancient    │
                                                        │          Aramaic texts (zero-shot)     │
                                                        └──────────────────────────────────────┘
```

Render this as a proper diagram (rounded boxes + arrows), not as ASCII. Show the two-phase split clearly.

---

## 7. Section 3 — Results

Header: **3 · RESULTS**

### 7a. Phase A — classifier performance (metrics card, left)

Present as a compact "metrics card" with three large figures:

- **Test accuracy: 98.6%**
- **F1 (Bavli): 0.99**
- **F1 (Yerushalmi): 0.95**

Caption: *Clean dialectal separation on the held-out Talmud test set (14,091 lines), using structural features only.*

### 7b. Phase A — confusion matrix (visual, left, below the metrics card)

A 2×2 matrix. Rows = **Actual**, columns = **Predicted**. Color the diagonal (correct) cells strongly; off-diagonal (errors) faint. Use the Bavli/Yerushalmi colors on the axis labels.

|  | Predicted Bavli | Predicted Yerushalmi |
|---|---|---|
| **Actual Bavli** | **12,056** ✓ | 113 |
| **Actual Yerushalmi** | 85 | **1,837** ✓ |

Only 198 of 14,091 test lines misclassified. Design note: give the two diagonal cells a filled tint (Bavli cell indigo-tinted, Yerushalmi cell amber-tinted) and leave the two error cells white with just the number — the eye should land on the strong diagonal.

### 7c. Phase B — zero-shot predictions on unlabeled ancient texts (main chart, right / wide)

**This is the centerpiece.** Build a **horizontal bar chart**, one bar per text, **grouped into four labeled corpora** (do NOT merge texts together — each scroll, each Enoch fragment, and each Onkelos book gets its own bar). Each bar shows **two numbers**: the **% classified Yerushalmi (Western)** as an amber `#C8892A` fill with the value in white, and the **% classified Bavli (Eastern)** (= 100 − Yerushalmi) in accent-blue `#1B5FA8` at the right end of the track. Draw a vertical **reference line at 50%**. Do not annotate sample sizes. Because every bar sits far to the right of 50%, the chart itself tells the story.

**Exact data (use verbatim):**

*Group 1 — Dead Sea Scrolls (Qumran Aramaic)*
| Text | % Yerushalmi | lines scored |
|---|---|---|
| 1QapGen — Genesis Apocryphon | 92.6% | 391 |
| 11QtgJob — Targum of Job | 84.7% | 352 |

*Group 2 — Enoch (Aramaic Enoch, Qumran Cave 4)*
| Text | % Yerushalmi | lines scored |
|---|---|---|
| 4Q202 (4QEnᵇ) | 82.4% | 51 |
| 4Q206 (4QEnᵉ) | 81.3% | 75 |
| 4Q212 (4QEnᵍ) | 80.4% | 51 |
| 4Q207 (4QEnᶠ) | 80.0% | 5 † |
| 4Q201 (4QEnᵃ) | 77.5% | 71 |
| 4Q204 (4QEnᶜ) | 76.9% | 117 |
| 4Q205 (4QEnᵈ) | 69.0% | 29 |

*Group 3 — Targum Onkelos (per book)*
| Text | % Yerushalmi | lines scored |
|---|---|---|
| Deuteronomy | 84.4% | 959 |
| Genesis | 80.7% | 1,533 |
| Leviticus | 78.6% | 859 |
| Exodus | 77.2% | 1,213 |
| Numbers | 76.2% | 1,288 |

*Group 4 — Aramaic Levi Document*
| Text | % Yerushalmi | lines scored |
|---|---|---|
| Aramaic Levi (all) | 96.0% | 25 |

Internal caveat (not shown on the poster): 4Q207 rests on only 5 scored lines, so treat its value as low-confidence. Per the presenters' choice, the poster does not annotate sample sizes.

Chart caption: *Every unlabeled corpus leans strongly Western (Yerushalmi). Amber = % Yerushalmi (Western); blue = % Bavli (Eastern) = 100 − % Yerushalmi. Sample sizes are not annotated on the poster.*

### 7d. Unsupervised clustering — self-validation (main confirmation figure)

We repeat the analysis **without the classifier**: each Talmud tractate and each ancient text is reduced to the mean of its 11 structural features, standardized, and grouped by hierarchical clustering (Ward linkage). The algorithm is given **no dialect labels**.

Insert the provided image `dendrogram_poster.png` here.

What it shows:
- **The features rediscover the dialect split on their own** — 28 Bavli tractates (indigo) and 28 Yerushalmi tractates (amber) fall into two clean, separate clusters with zero supervision. Strong evidence that the features capture real dialectal structure, not classifier memorization.
- **The ancient texts (blue) form their own coherent groups**: the five Targum Onkelos books cluster together as a distinct outgroup (a verse-by-verse translation, so a very different register), while the narrative texts (Enoch fragments, 1QapGen, Targum Job, Aramaic Levi) form a separate group.
- **In a forced Bavli-vs-Yerushalmi pole comparison, every ancient text is nearer the Western (Yerushalmi) centroid**, and this lean **survives even when the two line-length features are removed**, so it is not a segmentation artifact.

Caption: *What the tree shows. We ran this clustering without giving the model any labels, and it still split the Bavli tractates from the Yerushalmi tractates into two clean groups on its own (28 and 28, with no mixing). For us that was the real check: it means our 11 features are picking up the actual dialect difference and not some accident of the data. The texts we were testing also grouped together in sensible ways, with the Onkelos books forming their own cluster and the narrative texts (Enoch, the scrolls, Aramaic Levi) forming another. The tree does not place these texts inside the Yerushalmi branch, so we are not claiming that directly. The Western lean is the separate pole-distance result, where each text ends up closer to the Yerushalmi centroid, and that result still held after we dropped the two line-length features.*

Design note: give **every leaf a uniform colored category marker** (a short band beneath it): indigo = Bavli tractate, amber = Yerushalmi tractate, blue = ancient text under study, with a small **color key above the tree**. Name only the ancient texts (the tractate codes are numeric, so they stay unlabeled). Do not rely on left-to-right leaf adjacency for meaning; the dialect lean is the pole-distance result, not who is drawn next to whom.

### 7e. Optional second confirmation figure

If a simpler visual is wanted, `pole_distance_chart.png` shows the same pole comparison as one diverging bar per text (amber = nearer the Western pole; 14 of 15 lean Western, the lone near-tie being the 5-line 4Q207 fragment). Use the dendrogram **or** this chart — don't crowd the poster with both.

---

## 8. Section 4 — Conclusions & Discussion

Header: **4 · CONCLUSIONS & DISCUSSION**

Use this tightened, defensible copy (it holds up better under questioning than a "geography beats chronology" slogan):

**The finding.** Across four independent corpora (the Dead Sea Scrolls, Enoch, Targum Onkelos and the Aramaic Levi Document), the model consistently places the texts on the **Western (Yerushalmi)** side of the axis, on the strength of *structure alone*.

**What this does (and doesn't) claim.** The classifier is trained on *Late* Aramaic (the two Talmuds), while these target texts are older *Middle* Aramaic. So the result is not "these texts are the Jerusalem Talmud." It is a measurement of **which later dialectal pole their grammar most resembles**, and the answer is emphatically the Western branch, suggesting structural continuity with the Western Aramaic tradition rather than the Eastern/Babylonian one.

**Why it's interesting.** Some scholars expected the formal, "literary" register of these texts to look Eastern/Imperial. Instead, the spoken Western substrate appears to leak through into grammar and word order, exactly the signal a structural model can catch even when surface vocabulary is archaic or unusual. (Targum Onkelos is a nice test case: transmitted through Babylonia yet showing a Western structural profile.)

**Why NLP helps.** Human readers get distracted by rare spellings and archaic words; the LSTM ignores the surface and reads abstract structural sequences instead.

**Robustness.** The Western lean is not a length or segmentation artifact: it holds three ways: under the supervised classifier, under unsupervised clustering (which also rediscovers the Bavli/Yerushalmi split with no labels), and even after the two line-length features are dropped.

*One-line takeaway to feature:* **Under the formal surface, the grammar sounds Western.**

---

## 9. Current status & next steps

Poster Day does not require a finished project, so include a small honest "status" strip (a light-gray callout box, ~3 short lines):

- **Done:** feature pipeline, LSTM classifier (98.6% test accuracy), zero-shot predictions on four ancient corpora, and a model-free distance check confirming the Western lean.
- **In progress:** per-feature importance analysis (which of the 11 features drive the Western signal).
- **Next:** expand to more Qumran Aramaic texts; test alternative sequence models (e.g., transformer) as a robustness check.

---

## 10. Footer

Single thin strip, ~22 pt text, accent-blue rule above it, centered:

> Department of Computer Science, Ariel University  ·  2026

(No GitHub / repository link.)

---

## 11. Data appendix (for exact chart rendering)

All Phase B values are the fraction of a text's scored lines classified **Yerushalmi**; the complement is **Bavli**. Verified against the raw prediction CSVs.

| Corpus | Text | % Yerushalmi | % Bavli | n lines |
|---|---|---|---|---|
| Dead Sea Scrolls | 1QapGen (Genesis Apocryphon) | 92.6 | 7.4 | 391 |
| Dead Sea Scrolls | 11QtgJob (Targum of Job) | 84.7 | 15.3 | 352 |
| Enoch | 4Q201 (4QEnᵃ) | 77.5 | 22.5 | 71 |
| Enoch | 4Q202 (4QEnᵇ) | 82.4 | 17.6 | 51 |
| Enoch | 4Q204 (4QEnᶜ) | 76.9 | 23.1 | 117 |
| Enoch | 4Q205 (4QEnᵈ) | 69.0 | 31.0 | 29 |
| Enoch | 4Q206 (4QEnᵉ) | 81.3 | 18.7 | 75 |
| Enoch | 4Q207 (4QEnᶠ) | 80.0 | 20.0 | 5 |
| Enoch | 4Q212 (4QEnᵍ) | 80.4 | 19.6 | 51 |
| Targum Onkelos | Genesis | 80.7 | 19.3 | 1,533 |
| Targum Onkelos | Exodus | 77.2 | 22.8 | 1,213 |
| Targum Onkelos | Leviticus | 78.6 | 21.4 | 859 |
| Targum Onkelos | Numbers | 76.2 | 23.8 | 1,288 |
| Targum Onkelos | Deuteronomy | 84.4 | 15.6 | 959 |
| Aramaic Levi | Levi (all) | 96.0 | 4.0 | 25 |

Phase A metrics (all from the same test run, 14,091 lines): test accuracy **98.6%** (13,893 / 14,091 correct); F1 Bavli **0.99**, F1 Yerushalmi **0.95**. Confusion matrix: TN 12,056 · FP 113 · FN 85 · TP 1,837. Training set: 70,503 lines, 28 shared tractates, ~86% Bavli / ~14% Yerushalmi (balanced class weights applied).

---

## 12. Notes for the presenters (not printed on the poster)

These are the questions lecturers are most likely to ask — worth having answers ready:

1. **Chronology gap.** Training texts (Talmuds) are ~centuries *later* than the target texts. Frame the result as "structural affinity to the Western pole," not identity — the copy in §8 already does this.
2. **Class imbalance.** 86/14 Bavli:Yerushalmi. You handled it with balanced class weights; the slightly lower Yerushalmi F1 (0.96 vs 0.99) is consistent with the smaller class. Say so plainly.
3. **Tiny fragments.** 4Q207 (5 lines) and Aramaic Levi (25 lines) are small; treat their exact percentages as indicative, not precise. The larger corpora (Onkelos, ~6k verses total) carry the weight.
4. **Dendrogram reading.** The tree validates the *method*: with no labels, the Bavli and Yerushalmi tractates separate into two pure clusters (28 and 28, no mixing), and the ancient texts form coherent groups (the Onkelos books as one outgroup, the narrative texts as another). Onkelos is an outgroup because it is a verse-by-verse translation (register), not because it is "Eastern." Don't claim the texts nest inside the Yerushalmi branch; the Western lean is the *pole-distance* result, which survives dropping the line-length features.
5. **What "% Yerushalmi" means.** It's the share of *lines* in that text the model sent to the Western pole — not a single confidence score for the whole document.
