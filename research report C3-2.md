# VLearn Upgrade: Knowledge Tracing + Adaptive Learning for Venture Arena (Khóa 3)

## TL;DR
- **Build the knowledge-tracing + adaptive-review layer, but ship it as an Elo-based (not BKT-first) "weak-concept → 3 slides" engine, because Elo is simple, robust, and updates ability estimates online after each response with almost no training data** — reserve BKT (via the pyBKT library) as an optional upgrade if you get backend access to quiz logs.
- **Your winning one-sentence slice: "One student who just failed a lecture quiz (user) gets the 3 exact slides to re-read (job) chosen by a per-concept mastery estimate (AI decision), and a re-quiz shows the gap closed (result)."** This is demonstrable with zero backend access by having students upload a slide PDF + quiz CSV to a standalone web app.
- **Prove "learning-outcome improvement" with a simulated-learner A/B (adaptive vs random item selection) plus a small pre/post re-quiz** — the credible, reproducible headline metrics are "opportunities to reach 95% mastery" and "repeat-mistake / wheel-spinning rate across attempts," both countable from raw logs with published definitions.

## Key Findings

### 1. What to build — evidence-ranked feature stack
Learning science strongly and consistently supports the direction you've chosen. The two techniques with the largest, best-replicated effects are **retrieval practice (practice testing)** and **spaced/distributed practice**. Hattie and Donoghue's *A Meta-Analysis of Ten Learning Techniques* (2021), replicating Dunlosky et al. (2013) across 242 studies, 1,619 effects and 169,179 participants, concluded "The most effective techniques are Distributed Practice and Practice Testing." Pan and Rickard (2018, *Journal of Experimental Psychology: General* 147(11):1641–1664) meta-analyzed spaced retrieval; related meta-analytic work reports a "strong benefit of spaced retrieval practice in comparison with massed retrieval practice (g = 0.74)." The takeaway: your adaptive **re-quiz** (retrieval) and a **spaced review schedule** are not gimmicks — they are the highest-evidence things you can add to a slide+quiz platform.

Prioritized, hackathon-buildable features layered on VLearn:
1. **Concept map per lecture (10–15 concepts + prerequisites)** — the backbone; makes the AI tutor able to reason across slides, which it currently cannot.
2. **Per-concept mastery estimate** (Elo first, BKT optional) — turns raw quiz attempts into an interpretable "what you're weak at" signal.
3. **Personalized review path → the 3–5 exact slides for weak concepts** — retrieval-adjacent, directly actionable, and demoable.
4. **Adaptive re-quiz** selecting the next item at the learner's frontier (target ~50% success probability) — retrieval practice + desirable difficulty.
5. **Spaced-repetition scheduler** on weak concepts (FSRS or a simple half-life model) — the highest-evidence retention add-on if you have time.
6. **Cross-lecture concept linking / summarization** — upgrades the per-slide tutor into a whole-lecture tutor.

### 2. Mastery estimation — pick Elo, keep BKT as an upgrade
- **Elo rating system** treats each answer as a "match" between student skill and item difficulty. Pelánek (2016, *Computers & Education* 98:169–179, doi:10.1016/j.compedu.2016.03.017) is the standard reference: "We argue that the Elo rating system is simple, robust, and effective and thus suitable for use in the development of adaptive educational systems." His analysis further reports that under simulation just ~10 answers per student are enough to produce reasonable skill estimates. Update rule: `R_new = R_old + K·(outcome − expected)`, with expected probability from the logistic/Bradley–Terry model `1/(1+10^((D−S)/400))`. This is ~15 lines of Python and cold-starts fast — ideal for a hackathon with few users.
- **Bayesian Knowledge Tracing (BKT)** is a 4-parameter HMM (p_init, p_learn, p_guess, p_slip) that is more interpretable per-concept but needs calibration data. The **pyBKT** library (Badrinath, Wang & Pardos, EDM 2021) fits it via expectation-maximization and ingests standard tutor-log formats; the authors note you need roughly **50 students and sequence length ~15** for stable mastery estimation. Use pyBKT only in Scenario A when you can read `quiz_attempts`.
- **Item selection for the adaptive quiz:** target items where the learner's success probability is near 0.5 (the "Goldilocks"/maximum-information zone). This is the same principle behind computerized adaptive testing and Elo-based adaptive practice, and it's how Duolingo's Birdbrain (an IRT-style logistic model of ability × difficulty, 2020) picks "Goldilocks difficulty" exercises.

### 3. Concept map + question→concept tagging via LLM
This is now well-supported by 2024–2025 research and is the most "AI-native" part of your build:
- **LLM concept/KC extraction from slide text** works. Ozyurt, Feuerriegel & Sachan (2024, arXiv:2410.01727) automate knowledge-concept annotation and question representation for knowledge tracing; Li, Xu, Tang & Wen (2024, arXiv:2403.17281) automate KC tagging on math questions with LLMs.
- **Quality is "good enough" with a human check.** For KC generation from multiple-choice questions, Moore, Schmucker, Mitchell & Stamper (L@S 2024) had domain experts evaluate GPT-4-generated KCs against human ones. Inter-model agreement studies report moderate agreement (e.g., Cohen's kappa ≈ 0.51, "moderate" on the Landis & Koch scale, between two LLMs tagging the same items). So tag with an LLM, then spot-check a sample. For your hackathon: extract 10–15 concepts per lecture with an LLM, map each quiz question to 1–2 concepts, and manually verify a subset to report an agreement number to judges.
- **Prerequisite relations** can also be LLM-extracted; recent work (2024) confirms GPT-4-class models generate course concepts and prerequisite relations, though prerequisite direction is the noisiest part and benefits from human review.

### 4. Scenario A — WITH backend/data access
**Architecture (minimal pipeline):**
1. **Ingest:** read `quiz_attempts` (student_id, question_id, correct, timestamp) and slide content (slide_id, lecture_id, text).
2. **Concept layer (offline, LLM-assisted):** slide text → 10–15 concepts + prerequisite edges; question_id → concept_id(s). Store as `concepts`, `concept_prereqs`, `question_concept`.
3. **Mastery estimation:** run Elo online per (student, concept) on the attempt stream; optionally fit pyBKT per concept for interpretability.
4. **Serving:** an API endpoint returns, for a student+lecture, the ranked weak concepts → the 3–5 slides tagged to them, plus the next adaptive quiz item.
5. **Feedback loop:** log re-quiz outcomes to update mastery.

**Minimal schema:**
- `concepts(concept_id, lecture_id, name)`
- `concept_prereqs(concept_id, prereq_id)`
- `question_concept(question_id, concept_id, weight)`
- `slide_concept(slide_id, concept_id)`
- `mastery(student_id, concept_id, elo, n_attempts, updated_at)`
- (existing) `quiz_attempts(student_id, question_id, correct, ts)`

**Pros:** live data, real cold-start via entry survey → mastery priors, highest demo credibility. **Cons:** integration risk depends on VLearn granting DB access in time.

### 5. Scenario B — WITHOUT backend access
Proven external-layer patterns, ranked by hackathon credibility:
1. **Standalone web app with upload (RECOMMENDED).** Student uploads the lecture slide PDF + a quiz-results CSV export. App parses PDF text, runs LLM concept extraction, computes Elo mastery from the CSV, returns the review path and an adaptive re-quiz. **Most credible for a demo** because you control the full loop and can show a live before/after re-quiz. Tradeoff: data freshness is snapshot-based, not live; cold start handled by the entry survey.
2. **Browser-extension overlay.** Injects a "review these 3 slides" panel on top of VLearn pages, scraping visible quiz results. High "wow" but brittle (breaks if the DOM changes) and weaker as evidence.
3. **LMS interoperability standards.** If VLearn ever supports them: **LTI 1.3** lets your tool launch inside VLearn with single sign-on and receive roster/context; **xAPI** captures learning events as actor-verb-object statements into a Learning Record Store (LRS) for analytics; **SCORM** is legacy content packaging. For a days-long hackathon, full LTI/xAPI integration is usually too heavy — mention it as the productization path, not the demo.

**Verdict:** Build Scenario B as the standalone upload app (guarantees a working demo), and architect the mastery engine as a standalone service so that if VLearn grants DB access, you swap the CSV ingest for a `quiz_attempts` reader — same core, two front doors.

### 6. Prior art — what the comparables actually do
- **Duolingo (two distinct systems):** **Half-Life Regression (HLR)** (Settles & Meeder, ACL 2016) predicts *when* you'll forget — models recall probability `p = 2^(−Δ/h)` where half-life `h = 2^(Θ·x)`. The paper reports HLR "reducing error by 45%+ compared to several baselines" at predicting recall and that it "was able to improve Duolingo daily student engagement by 12% in an operational user study," trained on "13 million Duolingo student learning traces" (public on Harvard Dataverse, DOI 10.7910/DVN/N8XJME). **Birdbrain** (2020) predicts *what* to review using an IRT-style logistic model of ability × difficulty and "Goldilocks difficulty" selection.
- **ALEKS:** Uses **Knowledge Space Theory** (Doignon & Falmagne) — models a domain as concepts with prerequisite structure and assesses which "knowledge state" a student is in, pinpointing what they're "ready to learn" in roughly 20–30 questions (ALEKS documentation; Cosyn et al., *J. Mathematical Psychology* 2021). This is essentially the rigorous version of your concept-map + prerequisite idea; the "pie chart" of per-topic mastery is a proven UI to imitate.
- **Khan Academy / Khanmigo:** Mastery-learning levels (Attempted → Familiar → Proficient → Mastered). Khan Academy's November 2024 efficacy blog reports each additional skill practiced to proficient/mastered yields measurable learning gains; a 2024–25 study compared Khanmigo users vs non-users on internal mastery scoring. Their mastery-level UI is another proven pattern (note: these are vendor-reported figures — see Caveats).
- **Anki / FSRS:** **FSRS (Free Spaced Repetition Scheduler)** is open-source, available in many languages (py-fsrs), based on the three-component Difficulty–Stability–Retrievability memory model; it achieves a target retention with fewer reviews than the old SM-2 algorithm. If you add spacing, use py-fsrs rather than inventing a scheduler.
- **Simplest feasible versions for a hackathon:** Elo for learner/item rating; "IRT-lite" = one difficulty parameter per item (Elo already gives this); FSRS via the library for scheduling; LLM for concept tagging. All are days-scale.

### 7. Evidence & evaluation — how to prove "learning-outcome improvement"
Use a **two-track evidence plan**:

**Track 1 — Simulated learners (offline, guaranteed result even with no users).** Published, replicable-in-a-day protocol:
1. **Define KCs & item pool.** ~5–15 concepts, an item bank tagged by concept (optionally a difficulty band).
2. **Instantiate ~50+ matched simulated learners** with a hidden "true" mastery kept *separate* from the tutor's estimate so the result isn't self-fulfilling — the key design in Woo, Rao, Keluskar & Chen (2026, arXiv:2604.16744, "Evaluating Adaptive Personalization of Educational Readings with Simulated Learners").
3. **Response model:** BKT `P(correct)=P(L)(1−slip)+(1−P(L))·guess`, or IRT `p = c+(1−c)/(1+e^(−(α−β)))` with guess c=0.25 (Piech et al., "Deep Knowledge Tracing," NeurIPS 2015, which generated 2,000 simulated students answering 50 exercises).
4. **Standard BKT sim params** p_init=0.25, p_learn=0.2, p_guess=0.2, p_slip=0.1; mastery threshold 0.95 (Xia, Schmucker, Borchers & Aleven, 2025, arXiv:2506.17577).
5. **A/B:** adaptive item selection vs a **random** baseline, matched on learner seeds/initial states. Headline metrics: **opportunities to reach mastery** and **post-test accuracy after fixed N items**.
6. **Benchmark numbers from the literature:** adaptive raised post-test accuracy 83.4%→86.5% (Δ +3.1 pts, 95% CI [+0.4, +5.8], p=0.026) in Woo et al. 2026; a mastery-adaptive selector cut redundant practice ~35.7% in a 10,000-learner BKT/AFM simulation in Xia et al. 2025; Piech et al. 2015 showed deep-planning curricula reach higher predicted knowledge in fewer problems.
7. **Tooling:** `pip install pyBKT` (`generate.synthetic_data`) or hand-code the ~10-line BKT/Elo update.
8. **Honesty caveat to state to judges** (the papers state it themselves): simulated learners are for pre-deployment policy screening, not validated classroom effect sizes; cite Käser & Alexandron (2024, *Int. J. Artificial Intelligence in Education* 34(2):545–585) on under-tested simulator validity.

**Track 2 — Small-N human pre/post (live credibility).** With even 5–15 classmates: give a pretest, one adaptive review session, a posttest; report **normalized gain** g = (post−pre)/(100−pre) (Hake's measure, standard in physics/education research). Pair a treatment (adaptive review) against a control (re-read all slides) if you can.

**Reproducible baseline counting method (your "evidence with reproducible counting"):** the **repeat-mistake / wheel-spinning rate**. Beck & Gong (2013, AIED) define wheel-spinning as failing to master a skill within a set number of opportunities; a widely-cited operationalization is "mastery = 3 correct in a row; wheel-spinning = still not mastered after 10 problems" (the ASSISTments studies found ~5% of assignments led to wheel-spinning). Count, from raw quiz logs, **% of students who miss the same concept on ≥2 consecutive attempts** (baseline) vs after your review path. Fully reproducible from `quiz_attempts` and directly shows your tool breaks the repeat-mistake loop.

## Details — solution comparison table

**Option A1 (Scenario A): In-platform Elo review engine**
- *Build:* Read `quiz_attempts`; LLM-tag slides→concepts and questions→concepts; Elo per (student, concept); API returns weak concepts → 3–5 slides + next adaptive item.
- *Effort:* ~2–3 days for 2–3 people (Elo + tagging + endpoint). Integration risk if DB access is slow.
- *Slice:* one student · get the 3 slides for the weakest concept · Elo-based decision · re-quiz closes gap.
- *Evidence:* live repeat-mistake-rate drop + simulated A/B.

**Option A2 (Scenario A, stretch): + pyBKT + spacing (FSRS)**
- *Build:* Add pyBKT per-concept mastery and py-fsrs scheduling.
- *Effort:* +1–2 days; needs ~50 students of logs for BKT stability.
- *Slice:* same, with a mastery-level pie-chart UI (ALEKS/Khan-style).
- *Evidence:* mastery-level progression + retention via spaced re-quiz.

**Option B1 (Scenario B, RECOMMENDED): Standalone upload web app**
- *Build:* Upload slide PDF + quiz CSV → parse → LLM concept map → Elo mastery → review path + adaptive re-quiz, with entry survey for cold-start priors.
- *Effort:* ~2–3 days; fully self-contained, no VLearn dependency.
- *Slice:* one student uploads results · gets 3 slides · Elo decision · live before/after re-quiz.
- *Evidence:* live pre/post normalized gain in the demo + simulated A/B; most controllable.

**Option B2 (Scenario B): Browser-extension overlay**
- *Build:* Scrape VLearn quiz results, inject a review panel.
- *Effort:* ~2–3 days but brittle to DOM changes.
- *Slice:* same, overlaid on the real platform (higher "wow").
- *Evidence:* weaker (scrape reliability); best as a complement to B1.

## Recommendations
1. **Commit to Option B1 (standalone upload app) as your demo spine, with the mastery engine as a swappable service.** This guarantees a working end-to-end demo regardless of whether VLearn grants data access. If they do, flip on the `quiz_attempts` reader (Option A1) for the final pitch.
2. **Use Elo for mastery on day 1.** It cold-starts in ~10 answers, is explainable in one slide, and needs no training data. Only add pyBKT if you secure ≥50 students of logs (Option A2).
3. **Nail the one-sentence slice and instrument it:** one student · the 3 exact slides for their weakest concept · Elo/BKT decision · a re-quiz that shows the gap closed. Put a per-concept mastery pie chart (ALEKS/Khan-style) in the UI.
4. **Run the simulated-learner A/B before the event** so you always have a headline number (adaptive vs random: fewer opportunities to mastery, higher post-test accuracy). Use pyBKT or a ~10-line Elo simulator with 50+ matched learners.
5. **Add the reproducible baseline metric:** repeat-mistake / wheel-spinning rate (% students missing the same concept on ≥2 consecutive attempts) from raw logs, shown before/after your review path.
6. **Only add FSRS spacing if the core loop is done** — it's the highest-evidence retention feature but not essential for the slice.

**Thresholds that change the plan:**
- If VLearn grants DB access **before** the build sprint → lead with Option A1 (live data beats uploads for credibility).
- If you get **≥50 students × ~15 attempts** of real logs → switch mastery to pyBKT for interpretable per-concept curves.
- If you have **≥10 willing classmates** → run a live pre/post normalized-gain study; otherwise rely on the simulated A/B.
- If concept-tagging agreement checks come back **low (kappa well under 0.5)** → keep a human-in-the-loop verification step and report corrected tags rather than claiming full automation.

## Caveats
- **Simulated-learner results are screening evidence, not proof of classroom impact** — the source papers say so explicitly; always pair with even a tiny human pre/post and cite Käser & Alexandron (2024) on validity. Because large simulated N will always yield "statistical significance," report effect sizes and confidence intervals, not just p-values.
- **LLM concept tagging is imperfect** (moderate inter-rater/inter-model agreement, ~0.5 kappa in reported studies); prerequisite-edge direction is the noisiest output. Spot-check and report an agreement number rather than claiming perfect extraction.
- **BKT needs data**; with a hackathon's tiny N it can be unstable — this is exactly why Elo is the safer default.
- **Scraping/extension approaches are brittle** and can raise terms-of-service/permission questions; the upload app avoids both.
- **Small-N human studies have low statistical power**; report normalized gain with honest confidence intervals and don't over-claim.
- **Some cited efficacy figures come from vendor sources** (Khanmigo mastery gains, Duolingo's 12% engagement and 45% error-reduction numbers are from Duolingo's own ACL paper and operational studies; ALEKS/Khan figures from their own materials) — present them as vendor-reported, not independent peer review. Where possible, anchor claims to the peer-reviewed learning-science meta-analyses (Hattie & Donoghue 2021; Pan & Rickard 2018) instead.

---
*Ghi chú cho bạn (VN): Chọn Elo làm lõi ước lượng mastery vì đơn giản, hội tụ nhanh (~10 câu/học viên), dễ giải thích trước giám khảo. Slice một câu: "Một sinh viên vừa làm sai quiz → nhận đúng 3 slide cần đọc lại (do Elo quyết định) → làm lại quiz thấy tiến bộ." Bằng chứng: A/B với học viên mô phỏng (adaptive vs random) + tỉ lệ lặp lỗi (wheel-spinning) đếm trực tiếp từ log. Xây bản standalone upload (PDF slide + CSV quiz) để chắc chắn demo chạy, kể cả khi chưa có quyền truy cập backend VLearn.*