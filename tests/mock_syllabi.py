"""
CampusLens AI — Mock OSU Syllabus Test Suite (Day 2)
====================================================
5 realistic OSU course syllabi covering:
  1. CS 361  — Software Engineering (group project, hard)
  2. MATH 341 — Linear Algebra (proof-based, moderate-hard)
  3. WR 327  — Technical Writing (writing-heavy, easy-moderate)
  4. CH 331  — Organic Chemistry I (lab + lecture, very hard)
  5. ECON 201 — Micro Economics (lecture-heavy, moderate)

Also includes:
  - SPARSE: minimal 3-line "syllabus" (fallback test)
  - SCANNED: mostly gibberish (extraction failure test)
"""

MOCK_SYLLABI = {

# ─────────────────────────────────────────────────────────────
# 1. CS 361 — Software Engineering I  (HARD — group project)
# ─────────────────────────────────────────────────────────────
"cs361_software_engineering": """
OREGON STATE UNIVERSITY — CS 361
Software Engineering I — Winter 2026
Instructor: Dr. Rebecca Hartmann  |  hartmann@oregonstate.edu
Credits: 4  |  Term: Winter 2026

OFFICE HOURS: Tuesday 2–4pm, Wednesday 1–2pm (Kelley 3048)

COURSE DESCRIPTION
This course covers fundamental software engineering practices including
requirements elicitation, design, implementation, testing, and maintenance.
Students work in teams of 4-5 to build a full-stack web application across the term.

LEARNING OBJECTIVES
- Apply Agile/Scrum methodologies to a real team project
- Write clear user stories, acceptance criteria, and technical specifications
- Design software using UML diagrams and design patterns
- Implement and test a web application using modern tools
- Conduct code reviews and pair programming sessions

REQUIRED MATERIALS
- "Clean Code" by Robert Martin ($35, required)
- GitHub account (free)
- Access to OSU Engineering servers (provided)

GRADE BREAKDOWN
Assignments (individual):     25%
Sprint deliverables (team):   35%
Peer evaluation:              10%
Midterm exam:                 15%
Final exam:                   15%
TOTAL:                       100%

ASSIGNMENTS
Weekly individual assignments due every Sunday at 11:59pm.
NO LATE WORK ACCEPTED. Zero credit after deadline — no exceptions.
Lowest assignment score will be dropped.

TEAM PROJECT
You will be assigned to a team in Week 1. Teams cannot be changed after Week 2.
You will build a CRUD web application over 8 sprints (2 weeks each).
Sprint demos occur every other Friday. Missing a demo = 0 for that sprint.
Peer evaluations affect individual grades: poor peer scores can reduce your
sprint grade by up to 30%.

EXAMS
Midterm: Week 5, covers Weeks 1-4
Final: Finals week, CUMULATIVE
Both exams are closed-book, 80 minutes.
No makeup exams without documented medical emergency (reported within 24 hours).

ACADEMIC INTEGRITY
All individual work must be your own. Sharing code on individual assignments
results in automatic failure of the course. Team members are expected to
contribute roughly equally — the instructor monitors GitHub commit history.

COURSE SCHEDULE
Week 1:  Introduction to Software Engineering, Agile overview
Week 2:  Requirements & User Stories
Week 3:  UML Diagrams & System Design
Week 4:  Design Patterns (MVC, Observer, Factory)
Week 5:  MIDTERM. Testing strategies
Week 6:  Sprint 3-4, Code Reviews
Week 7:  Database design & ORM
Week 8:  Security basics, Input validation
Week 9:  Deployment, CI/CD pipelines
Week 10: Sprint 7-8, Project polish
Finals:  Final exam + final project submission
""",

# ─────────────────────────────────────────────────────────────
# 2. MATH 341 — Linear Algebra  (MODERATE-HARD, proof-based)
# ─────────────────────────────────────────────────────────────
"math341_linear_algebra": """
OREGON STATE UNIVERSITY
MATH 341 — Linear Algebra
Winter 2026 | 4 Credits
Instructor: Prof. Alan Torres | torres@math.oregonstate.edu
Office: Kidder 368 | Hours: MWF 11am-12pm

PREREQUISITES: MATH 254 (Calculus III) with a grade of C or better.
Students without the prerequisite will be dropped from the course.

TEXTBOOK (Required): "Linear Algebra and Its Applications" by David Lay, 6th edition.
Specific sections will be listed in weekly reading assignments.

COURSE CONTENT
Vectors and matrices, systems of linear equations, determinants, vector spaces,
linear transformations, eigenvalues and eigenvectors, orthogonality,
and applications in data science and engineering.

GRADING
Homework:        20%
Written Quizzes: 15%   (6 quizzes, drop lowest 1)
Midterm 1:       20%   (Week 4)
Midterm 2:       20%   (Week 8)
Final Exam:      25%   (Comprehensive, 2.5 hours)
Total:          100%

HOMEWORK POLICY
Homework is assigned weekly, due Fridays at 5:00pm.
Late homework: 20% penalty per day, max 3 days late. After 3 days: 0 credit.
Work must show all steps for full credit. Answers only = half credit.
Collaboration is allowed but write-ups must be your own — copying is academic dishonesty.

EXAMS
All exams are closed-book, closed-notes.
You may bring one 3x5 index card with formulas (both midterms and final).
No calculators on any exam — this is a proof-based course.
Makeup exams require instructor approval at least 48 hours in advance.

PROOF EXPECTATIONS
Starting Week 3, some homework problems require formal mathematical proofs.
Proofs are graded on correctness, clarity, and notation. Students who have
not written proofs before are strongly encouraged to visit office hours.

QUIZZES
Quizzes are in-class, 15 minutes, given on random Fridays (announced the prior Wednesday).
Topics cover the previous 2 weeks of material.

SCHEDULE
Week 1:  Vectors, linear combinations, span
Week 2:  Matrix equations, solution sets
Week 3:  Linear independence, transformations
Week 4:  Midterm 1. Matrix operations, inverses
Week 5:  Determinants
Week 6:  Vector spaces, subspaces, basis
Week 7:  Dimension, rank theorem
Week 8:  Midterm 2. Eigenvalues, eigenvectors
Week 9:  Diagonalization, Markov chains
Week 10: Orthogonality, least squares
Finals:  Comprehensive final exam
""",

# ─────────────────────────────────────────────────────────────
# 3. WR 327 — Technical Writing  (EASY-MODERATE)
# ─────────────────────────────────────────────────────────────
"wr327_technical_writing": """
Oregon State University
WR 327: Technical Writing
Winter 2026 | 3 Credits
Instructor: Sarah Mitchell, MFA
Email: mitchells@oregonstate.edu
Office Hours: Tuesdays 1-3pm, or by appointment (via Calendly link on Canvas)

Welcome to Technical Writing! This course prepares students to communicate
complex information clearly and effectively in professional contexts.
This is a writing-intensive course — expect to write every week.

What You'll Learn:
- Audience analysis and purpose-driven writing
- Technical document design (reports, proposals, instructions)
- Data visualization and document formatting
- Collaborative writing and peer review
- Editing for clarity, conciseness, and accessibility

Required Materials:
- All readings posted free on Canvas. No textbook purchase required.
- Microsoft Word or Google Docs
- A Google account for document sharing

Grading Breakdown:
Participation & Peer Reviews:  15%
Short Writing Exercises (8):   20%
Major Project 1 — Instructions: 20%  (due Week 5)
Major Project 2 — Proposal:    20%  (due Week 8)
Final Report:                  25%  (due Finals Week)
Total:                        100%

Late Work Policy:
Life happens! You have a 48-hour grace period on all assignments with no penalty.
After 48 hours: 10% per day deduction, up to 5 days. After 5 days: not accepted.
Please communicate with me — I'm happy to work with you on extensions.

Attendance:
Regular attendance is expected but not formally graded.
If you miss class, you are responsible for getting notes from a classmate.
Missing more than 3 classes may affect your participation grade.

Projects:
Each major project has multiple stages (draft, peer review, revision, final).
Turning in a rough draft for peer review is mandatory for full credit on final drafts.
You may revise any major project one time for a higher grade (within 2 weeks of return).

Course Vibe:
This class is collaborative and low-stress. There are no surprise quizzes or
high-stakes exams. Your growth as a communicator matters more than perfection.

Weekly Schedule:
Week 1:  Intro to technical writing, audience analysis
Week 2:  Document design principles
Week 3:  Instructions genre, usability testing
Week 4:  Peer review workshop (Project 1 drafts)
Week 5:  Project 1 due. Data visualization
Week 6:  Proposals and business writing
Week 7:  Collaborative writing strategies
Week 8:  Project 2 due. Report writing
Week 9:  Editing and revision strategies
Week 10: Final project workshop
Finals:  Final Report due (no in-person exam)
""",

# ─────────────────────────────────────────────────────────────
# 4. CH 331 — Organic Chemistry I  (VERY HARD)
# ─────────────────────────────────────────────────────────────
"ch331_organic_chemistry": """
OREGON STATE UNIVERSITY
CH 331 — Organic Chemistry I
Winter 2026  |  4 Credits (3 lecture + 1 lab)
Lecture Instructor: Dr. Patricia Vo, PhD  |  vo@chemistry.oregonstate.edu
Lab Instructor: Dr. Mark Elkins  |  elkins@chemistry.oregonstate.edu
Office Hours: Dr. Vo — Mon/Wed 3-4pm, Gilbert 153

PREREQUISITES: CH 232 with C or better. No exceptions.
This course is a prerequisite for Medical School, Dental School, and Pharmacy admissions.

REQUIRED MATERIALS
- "Organic Chemistry" by Clayden, Greeves & Warren (3rd ed.) — $180
- Lab manual: available at OSU bookstore — $45
- Molecular model kit — $30 (available at bookstore)
- Lab coat and safety goggles — required for ALL lab sessions
- Scantron forms (Qty 5, Form 882-E)

COURSE OVERVIEW
CH 331 is universally considered the most challenging course in the pre-health curriculum.
We cover: structure and bonding, stereochemistry, substitution/elimination reactions
(SN1/SN2/E1/E2), carbonyl chemistry, and spectroscopy (IR, NMR, MS).
You WILL need to memorize reaction mechanisms. There is no shortcut.

GRADING
Lab reports (8 reports):        15%
Pre-lab quizzes (8):             5%
In-class problem sets (10):     10%
Exam 1 (Week 3):                15%
Exam 2 (Week 6):                15%
Exam 3 (Week 9):                15%
Final Exam (comprehensive):     25%
TOTAL:                         100%

NO DROPS. Every grade counts.
Historical average grade: C+ (2.3 GPA). About 15% of students receive a D or F.

EXAMS
All 3 midterms + final are in-person, 75 minutes.
Closed book, closed notes. Periodic table provided.
Exams include: multiple choice, mechanism drawing, synthesis problems, spectral analysis.
Makeup exams: only with documented emergency filed with the Dean of Students office.
Exams cannot be rescheduled for travel, work, or minor illness.

LAB (Wednesdays, 2:00–4:50pm, Gilbert 120)
Attendance at ALL lab sessions is mandatory. Missing a lab = 0 for that lab report.
Two missed labs = automatic F in the course.
Pre-lab quiz given first 10 minutes of each lab. Pre-lab reading is required.
Lab reports due the following Monday by 11:59pm. No late lab reports accepted.
Safety violations result in immediate removal from lab and potential course failure.

STUDENT SUPPORT
Organic Chemistry tutoring: STEM Leaders Center, MWF 6–9pm
Dr. Vo holds office hours Monday and Wednesday — these are very helpful!
Study groups are strongly encouraged. Students who form study groups historically
perform 0.5–1 letter grade better than students who study alone.

TYPICAL WEEK (expect 15-20 hrs/week outside class):
- Read textbook chapter before lecture (1.5–2 hrs)
- Attend 3 lectures + 1 lab per week (5 hrs total)
- Complete end-of-chapter problems (3–5 hrs)
- Complete in-class problem sets (1–2 hrs)
- Write lab report (3–4 hrs)
- Review mechanisms daily (30 min/day)

SCHEDULE
Week 1:  Bonding, hybridization, molecular structure
Week 2:  Stereochemistry, chirality, R/S notation
Week 3:  EXAM 1. Nucleophiles and electrophiles
Week 4:  SN2 reactions — mechanism and stereochemistry
Week 5:  SN1 reactions — carbocation stability
Week 6:  EXAM 2. E1 and E2 elimination reactions
Week 7:  Alkenes: addition reactions (HX, H2O, halogens)
Week 8:  Alkynes, dienes, conjugation
Week 9:  EXAM 3. Carbonyl chemistry introduction
Week 10: Infrared spectroscopy and NMR basics
Finals:  Comprehensive Final Exam
""",

# ─────────────────────────────────────────────────────────────
# 5. ECON 201 — Microeconomics  (MODERATE)
# ─────────────────────────────────────────────────────────────
"econ201_microeconomics": """
Oregon State University
ECON 201 — Introduction to Microeconomics
Winter 2026  |  4 Credits
Instructor: James Okonkwo
Email: okonkwo@oregonstate.edu  |  Office: Ballard 303
Office Hours: Thursday 10am–12pm

COURSE DESCRIPTION
An introduction to microeconomic theory: scarcity and choice, supply and demand,
market structures (perfect competition, monopoly, oligopoly), factor markets,
externalities, and public goods. No prior economics background required.

TEXTBOOK
"Principles of Microeconomics" by Mankiw, 9th edition.
An older edition (7th or 8th) is acceptable and significantly cheaper.

GRADING
Reading Quizzes (12, drop 2):   15%
Homework Assignments (6):       20%
Midterm 1:                      20%
Midterm 2:                      20%
Final Exam:                     25%
Total:                         100%

READING QUIZZES
Short 5-question Canvas quizzes, open before each lecture.
Available for 24 hours, auto-graded. You may take them twice (higher score counts).
Purpose: to ensure you read before class so we can discuss, not lecture.

HOMEWORK
6 problem sets, released every other week, due Sundays at midnight.
Late work: 25% penalty within 24 hours. Not accepted after 24 hours.
Collaboration encouraged — but write your own solutions.

EXAMS
Midterm 1: Week 4 (in class, 50 minutes)
Midterm 2: Week 8 (in class, 50 minutes)
Final: Finals week (90 minutes, covers all material with emphasis on post-midterm 2)
All exams: closed book, non-graphing calculators allowed.
One page of notes (handwritten only) permitted on each exam.

COURSE POLICIES
Attendance is not taken. However, attendance correlates strongly with performance.
Class sessions will involve in-class activities and discussion — not just lecturing.
Electronics: laptops/tablets allowed for note-taking. Phone use discouraged.

SCHEDULE
Week 1:  Scarcity, opportunity cost, PPF
Week 2:  Supply and demand basics
Week 3:  Elasticity
Week 4:  Midterm 1. Consumer surplus & producer surplus
Week 5:  Externalities and public goods
Week 6:  Firm behavior and profit maximization
Week 7:  Perfect competition
Week 8:  Midterm 2. Monopoly
Week 9:  Oligopoly, game theory basics
Week 10: Labor markets, income inequality
Finals:  Final Exam
""",

# ─────────────────────────────────────────────────────────────
# 6. SPARSE — minimal fake syllabus (tests fallback)
# ─────────────────────────────────────────────────────────────
"sparse_minimal": """
CS 499 — Special Topics
Dr. Johnson
Grades: 50% project, 50% presentation
Contact me for more info.
""",

# ─────────────────────────────────────────────────────────────
# 7. SCANNED ARTIFACT — gibberish (tests extraction failure)
# ─────────────────────────────────────────────────────────────
"scanned_gibberish": """
Ü©ÆêŒ†§¶•ªº–≠ æœ∑´†¥¨ˆøπ"'«åß∂ƒ©˙∆˚¬… 
lllllIIIIIIIIll llIlIlIlIl ll lI I
1 1 1 1 1 1 1 111 l l l l
""",
}

# Expected difficulty scores (for test validation)
EXPECTED_SCORES = {
    "cs361_software_engineering":  (6, 8),   # range (min, max)
    "math341_linear_algebra":      (5, 7),
    "wr327_technical_writing":     (2, 4),
    "ch331_organic_chemistry":     (8, 10),
    "econ201_microeconomics":      (3, 6),
    "sparse_minimal":              (1, 7),   # wide range — low confidence
}