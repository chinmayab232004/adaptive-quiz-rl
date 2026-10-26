# ADAPTIVE QUIZ SYSTEM USING REINFORCEMENT LEARNING

> **Master of Computer Applications (MCA) Final Year Academic Capstone Project**  
> An intelligent educational evaluation platform integrating **Python, Streamlit, SQLite, and Tabular Q-Learning** with a mandatory pedagogical difficulty state machine.

---

## 📑 Table of Contents
1. [Abstract](#1-abstract)
2. [Introduction](#2-introduction)
3. [Problem Statement](#3-problem-statement)
4. [Objectives](#4-objectives)
5. [Existing System vs. Proposed System](#5-existing-system-vs-proposed-system)
6. [Scope of the Project](#6-scope-of-the-project)
7. [System Architecture & Data Flow](#7-system-architecture--data-flow)
8. [Core Requirement: Mandatory Adaptive Difficulty Rules](#8-core-requirement-mandatory-adaptive-difficulty-rules)
9. [Reinforcement Learning Formulation (Q-Learning)](#9-reinforcement-learning-formulation-q-learning)
10. [Database Design & Schema](#10-database-design--schema)
11. [Question Bank Details (105 Questions Across 5 Domains)](#11-question-bank-details-105-questions-across-5-domains)
12. [User Interface & Page Navigation (12 Pages)](#12-user-interface--page-navigation-12-pages)
13. [Hardware & Software Requirements](#13-hardware--software-requirements)
14. [Installation & Setup Instructions](#14-installation--setup-instructions)
15. [Execution Guide for Visual Studio Code](#15-execution-guide-for-visual-studio-code)
16. [Automated Testing & Verification](#16-automated-testing--verification)
17. [Comparative Evaluation & Simulation Lab](#17-comparative-evaluation--simulation-lab)
18. [Viva Voce & Project Defense Guide (For MCA Students)](#18-viva-voce--project-defense-guide-for-mca-students)
19. [Limitations & Future Enhancements](#19-limitations--future-enhancements)
20. [Conclusion](#20-conclusion)

---

## 1. Abstract
Computerized assessments play an indispensable role in contemporary higher education. However, traditional online examination platforms utilize static question distributions that fail to accommodate varying student cognitive readiness. This paper presents the **Adaptive Quiz System Using Reinforcement Learning**, a full-stack academic application utilizing **Python, Streamlit, and SQLite**. The system incorporates an exact, deterministic difficulty transition rule operating in tandem with a tabular **Q-learning** reinforcement learning agent. The quiz initializes at **EASY** and shifts dynamically to **MEDIUM** and **HARD** based on instantaneous student performance while updating state-action values according to the **Bellman Optimality Equation**. Empirical evaluation demonstrates how this dual-layer adaptive model maintains learner engagement within the **Zone of Proximal Development (ZPD)**.

---

## 2. Introduction
In standard e-learning platforms, quizzes are typically delivered in one of two ways:
1. **Fixed difficulty:** Every candidate answers questions of identical difficulty.
2. **Random difficulty:** Questions are selected randomly without regard to student responses.

Both paradigms suffer from fundamental educational deficiencies: capable students experience disengagement and boredom when presented with trivial questions, whereas struggling students experience anxiety and demotivation when confronted with overly difficult problems.

The **Adaptive Quiz System Using Reinforcement Learning** models educational assessment as a **Markov Decision Process (MDP)**. The system dynamically evaluates answers in real-time, advances or scaffolds question difficulty, and continuously refines its Q-table policy in a persistent relational database.

---

## 3. Problem Statement
Existing computerized adaptive testing (CAT) frameworks such as Item Response Theory (IRT) require extensive offline psychometric calibration across massive test-taker cohorts and cannot be easily customized or audited in real time. Moreover, conventional algorithmic rule engines lack the ability to quantify reinforcement signals or learn optimal question-serving policies. 

There is an urgent academic need for an educational testing system that:
1. Guarantees deterministic, pedagogical difficulty transitions after every answer.
2. Formulates difficulty adaptation using transparent, tabular Q-learning.
3. Operates entirely locally without expensive third-party APIs or cloud subscriptions.
4. Provides full transparency into learned Q-values and student metrics.

---

## 4. Objectives
- **Develop a Deterministic Difficulty Engine:** Ensure questions dynamically transition immediately: correct answers step up (`EASY -> MEDIUM -> HARD -> HARD`), while incorrect answers step down (`HARD -> MEDIUM -> EASY -> EASY`).
- **Implement Tabular Q-Learning:** Formulate learner states, difficulty actions, and scalar rewards (`+1` for correct, `-1` for incorrect), continuously updating Q-values via the Bellman equation.
- **Engineer a 100+ Question Inventory:** Create 105 realistic multiple-choice questions across 5 core Computer Science domains with distinct difficulty tiers and educational explanations.
- **Enforce In-Session Question Uniqueness:** Prevent question repetition within a session until all questions of that difficulty level are exhausted.
- **Deliver a 12-Page Streamlit Interface:** Provide dedicated student portals, administrative management panels, and algorithm visualizers with interactive Plotly analytics.
- **Validate with Automated Tests:** Achieve 100% test pass rates across pytest and unittest suites.

---

## 5. Existing System vs. Proposed System

| Feature | Conventional Examination System | Proposed Adaptive RL Quiz System |
| :--- | :--- | :--- |
| **Difficulty Delivery** | Static, fixed, or arbitrary random | Dynamically adaptive based on real-time correctness |
| **Cognitive Alignment** | Misaligned; causes boredom or frustration | Aligned with Zone of Proximal Development (ZPD) |
| **Initial Question** | Arbitrary or uniform | Starts at **EASY** by default to establish baseline |
| **AI / Machine Learning** | None | Tabular Q-Learning with Bellman optimality updates |
| **Feedback Mechanism** | Delayed or post-exam summary | Immediate feedback, explanations, and transition alerts |
| **Data Transparency** | Black-box scoring | Full visibility into Q-values, TD errors, and policy convergence |
| **Administrative Control** | Manual question entry only | Full CRUD, JSON/CSV bulk import/export, and audit tables |

---

## 6. Scope of the Project
- **Target Audience:** Undergraduate and postgraduate students (MCA, M.Sc. CS, B.Tech CSE), teaching faculty, and institutional evaluators.
- **Academic Disciplines Covered:**
  1. Python Programming
  2. Data Structures and Algorithms
  3. Database Management Systems (DBMS)
  4. Computer Networks
  5. Cybersecurity
- **Deployment Target:** Standalone local deployment on standard Windows/Linux/macOS laptops using Visual Studio Code and Python virtual environments.

---

## 7. System Architecture & Data Flow

```
                                  +---------------------------------------+
                                  |         Streamlit User Interface      |
                                  |   [Student Dashboard] [Admin Portal]  |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |           Quiz Engine Core            |
                                  |  - Tracks Active Session              |
                                  |  - Prevents In-Session Duplicates     |
                                  |  - Enforces Mandatory Transitions     |
                                  +---------+-------------------+---------+
                                            |                   |
                     +----------------------+                   +-----------------------+
                     v                                                                  v
+--------------------+---------------------+                  +-------------------------+--------------------+
|    Mandatory Difficulty Transition       |                  |        Reinforcement Learning Engine         |
|  - Correct:   EASY->MED->HARD->HARD      |                  |  - Discrete State (DIFF|ACC|PERF|ANS)        |
|  - Incorrect: HARD->MED->EASY->EASY      |                  |  - Actions (EASY=0, MEDIUM=1, HARD=2)        |
+--------------------+---------------------+                  |  - Rewards (+1.0 Correct, -1.0 Incorrect)    |
                     |                                        |  - Bellman Optimality Update                 |
                     |                                        +-------------------------+--------------------+
                     |                                                                  |
                     +------------------------------+-----------------------------------+
                                                    |
                                                    v
                                  +---------------------------------------+
                                  |            SQLite Database            |
                                  |  - users            - questions       |
                                  |  - quiz_sessions    - responses       |
                                  |  - q_values         - progress        |
                                  +---------------------------------------+
```

---

## 8. Core Requirement: Mandatory Adaptive Difficulty Rules

THIS IS THE GOVERNING FEATURE OF THE QUIZ SYSTEM.

The quiz engine automatically adjusts the difficulty level immediately following every submitted answer:
* Exactly three difficulty levels: **EASY**, **MEDIUM**, **HARD**.
* The first question always starts at **EASY** by default.

### Mandatory State Machine Rules:
* **If the student answers CORRECTLY:**
  * `EASY   -> MEDIUM`
  * `MEDIUM -> HARD`
  * `HARD   -> HARD` (Upper boundary capped at HARD)
* **If the student answers INCORRECTLY:**
  * `HARD   -> MEDIUM`
  * `MEDIUM -> EASY`
  * `EASY   -> EASY` (Lower boundary capped at EASY)

### In-Session Question Uniqueness:
* The quiz engine tracks `used_question_ids`.
* Questions of the required difficulty are served without repetition.
* If all questions of the required difficulty have been used, the engine resets the used list for that specific difficulty and draws from the full bank at that difficulty.
* **The system never silently changes the required difficulty level.**

---

## 9. Reinforcement Learning Formulation (Q-Learning)

### A. Markov Decision Process (MDP)
1. **State Space ($S$):** Discretized into a 4-dimensional tuple:
   $$\text{State Key} = \text{DIFF} \mid \text{ACC} \mid \text{PERF} \mid \text{ANS}$$
   * **Current Difficulty ($\text{DIFF}$):** `EASY`, `MEDIUM`, `HARD`
   * **Recent Accuracy ($\text{ACC}$):** `LOW` ($<50\%$), `MID` ($50\%-75\%$), `HIGH` ($>75\%$)
   * **Performance Tier ($\text{PERF}$):** `BEG` ($<40\%$), `INT` ($40\%-75\%$), `ADV` ($>75\%$)
   * **Question Count ($\text{ANS}$):** `FEW` ($\le 3$), `SOME` ($4-7$), `MANY` ($\ge 8$)
2. **Action Space ($A$):**
   * $a = 0 \rightarrow \text{EASY}$
   * $a = 1 \rightarrow \text{MEDIUM}$
   * $a = 2 \rightarrow \text{HARD}$
3. **Reward Scheme ($R$):**
   * Correct Answer: $+1.0$ (configurable in `config.py`)
   * Incorrect Answer: $-1.0$ (configurable in `config.py`)
4. **Action Selection:** $\epsilon$-greedy policy ($\epsilon = 0.2$) with random tie-breaking.

### B. Bellman Optimality Equation
After each answered question, the Q-table updates via:
$$Q(s, a) \leftarrow Q(s, a) + \alpha \left[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right]$$

* **Learning Rate ($\alpha = 0.1$):** Controls the weighting of temporal difference error.
* **Discount Factor ($\gamma = 0.9$):** Evaluates expected future reward accumulation.
* **Exploration Rate ($\epsilon = 0.2$):** Balances exploration of actions vs exploiting known high Q-values.
* **Separation of Concerns:** The mandatory difficulty transition rule dictates the immediate next question, while the Q-learning agent evaluates and learns expected returns across states.

---

## 10. Database Design & Schema

Stored locally in `adaptive_quiz.db` using SQLite with foreign keys and index optimization:

```sql
-- Users (Students & Administrators)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Question Bank (105+ Items)
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL DEFAULT 'General',
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    explanation TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quiz Sessions
CREATE TABLE quiz_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    total_questions INTEGER NOT NULL DEFAULT 10,
    score INTEGER DEFAULT 0,
    status TEXT DEFAULT 'in_progress',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Student Responses
CREATE TABLE student_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    submitted_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL,
    current_difficulty TEXT NOT NULL,
    next_difficulty TEXT NOT NULL,
    reward REAL NOT NULL,
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES quiz_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Persistent Q-Values (Global user_id=0, Personalized user_id>0)
CREATE TABLE q_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    state_key TEXT NOT NULL,
    action INTEGER NOT NULL,
    q_value REAL NOT NULL DEFAULT 0.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, state_key, action)
);

-- Cumulative Student Progress
CREATE TABLE student_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    estimated_skill REAL DEFAULT 0.50,
    total_correct INTEGER DEFAULT 0,
    total_incorrect INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, subject),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 11. Question Bank Details (105 Questions Across 5 Domains)

The database includes 105 curated multiple-choice questions:
* **Python Programming (21 questions):** Data types, lambda functions, closures, decorators, GIL, memory management, generators.
* **Data Structures and Algorithms (21 questions):** Stacks, queues, heaps, AVL trees, Red-Black trees, DSU, B-Trees, graph theory.
* **Database Management Systems (21 questions):** ACID properties, 2NF/3NF/BCNF normalization, indexing, WAL/ARIES recovery, MVCC.
* **Computer Networks (21 questions):** OSI layers, TCP 3-way handshake, subnetting, OSPF, BGP loop prevention, QUIC / HTTP/3.
* **Cybersecurity (21 questions):** CIA triad, phishing, ransomware, symmetric vs asymmetric ciphers, CSP, Diffie-Hellman, Spectre/Meltdown.

Every question contains:
- `id`, `subject`, `topic`, `question`, `option_a`, `option_b`, `option_c`, `option_d`, `correct_answer`, `difficulty` (`EASY`, `MEDIUM`, `HARD`), and `explanation`.

---

## 12. User Interface & Page Navigation (12 Pages)

The platform provides a modern deep navy (`#0B132B`) and electric blue theme with 12 distinct pages:

1. **Welcome Page:** Hero banner, architectural overview, and domain cards.
2. **Student Registration:** Salted password hashing, input validation.
3. **Student Login:** Secure sign in with demo admin credentials access.
4. **Student Dashboard:** Metrics cards, total rewards, overall accuracy, and Plotly charts.
5. **Subject Selection:** Choose from 5 CS domains, customize quiz lengths (5, 10, 15, 20), view past subject accuracy.
6. **Quiz Interface:** Live countdown timer, question progress bar, difficulty chips, and instant transition display:
   ```
   CURRENT QUESTION: MEDIUM
   ANSWER: INCORRECT
   REWARD: -1
   NEXT DIFFICULTY: EASY
   ```
7. **Quiz Result Page:** Final scorecard, attempt comparisons, itemized review, and personalized study recommendations.
8. **Quiz History:** Filter past completed sessions and inspect every past response.
9. **Learning Analytics:** Cumulative reward accumulation line charts, difficulty timeline scatters, and skill progression.
10. **Admin Dashboard:** Total students, questions, attempts, subject/difficulty donut charts, and student performance tables.
11. **Question Bank Management:** Add, edit, delete, search, filter, and import/export questions via JSON/CSV.
12. **Reinforcement Learning Visualization:** Interactive single-step Bellman equation calculator, parameter controls, and persistent Q-table heatmap.

---

## 13. Hardware & Software Requirements

### Hardware Requirements
- **Processor:** Intel Core i3 / AMD Ryzen 3 or higher.
- **RAM:** Minimum 4 GB RAM (8 GB recommended).
- **Disk Storage:** At least 500 MB free hard disk space.

### Software Requirements
- **Operating System:** Windows 10/11, macOS, or Linux.
- **Runtime:** Python 3.10, 3.11, 3.12, 3.13, or 3.14.
- **IDE:** Visual Studio Code (VS Code).
- **Browser:** Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari.

---

## 14. Installation & Setup Instructions

### Step 1: Open the Project Directory
In Visual Studio Code, navigate to:
```
File -> Open Folder -> Select "adaptive quiz system"
```

### Step 2: Create a Virtual Environment (Recommended)
Open the integrated terminal (`Ctrl + ~`) and create a Python virtual environment:
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
Run:
```bash
pip install -r requirements.txt
```

---

## 15. Execution Guide for Visual Studio Code

### Starting the Web Application
Execute the following command in the VS Code terminal:
```bash
python -m streamlit run app.py
```

### Accessing the Web Application
Once started, open your web browser and navigate to:
```
http://localhost:8501
```

### Pre-Configured Administrator Account
- **Username / Email:** `admin` or `admin@quizsystem.edu`
- **Password:** `adminpassword123`

*Students can register immediately via the "Create New Student Account" tab.*

---

## 16. Automated Testing & Verification

The project includes an automated test suite verifying all layers:

### Running Tests with pytest:
```bash
python -m pytest
```
*Output:*
```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0
collected 20 items

tests\test_database.py ....                                              [ 20%]
tests\test_difficulty.py ......                                          [ 50%]
tests\test_e2e_integration.py .                                          [ 55%]
tests\test_q_learning.py .....                                           [ 80%]
tests\test_quiz_engine.py ....                                           [100%]

============================== 20 passed in 2.08s ==============================
```

### Specific Transitions Tested:
1. `EASY + Correct = MEDIUM`
2. `MEDIUM + Correct = HARD`
3. `HARD + Correct = HARD`
4. `HARD + Incorrect = MEDIUM`
5. `MEDIUM + Incorrect = EASY`
6. `EASY + Incorrect = EASY`
7. First question defaults to `EASY`.
8. Zero in-session question duplication.
9. Bellman update formula mathematical precision.
10. Salted password authentication & uniqueness constraints.

---

## 17. Comparative Evaluation & Simulation Lab

Accessible from the sidebar via **🔬 Evaluation & Simulation**, this laboratory compares three paradigms across simulated learner archetypes (Novice, Average, Advanced):

1. **Fixed-Difficulty Model (Static Medium):**
   - Lacks adaptation. Novices experience continuous failure; advanced learners experience boredom.
2. **Pure Rule-Based Adaptive Model:**
   - Applies deterministic transitions without reinforcement learning value updates.
3. **Q-Learning Adaptive Model with Mandatory Transitions:**
   - Combines deterministic transition boundaries with Q-learning value updates, mapping state-action pairs and converging toward optimal cumulative reward trajectories.

---

## 18. Viva Voce & Project Defense Guide (For MCA Students)

During your project viva, examiners typically ask the following core questions:

### Q1: What is the primary difference between a conventional quiz and your adaptive quiz?
> *"In a conventional quiz, questions are served randomly or at a fixed difficulty regardless of student performance. In our system, the quiz initializes at EASY, and after every response, the difficulty dynamically transitions (Easy &rarr; Medium &rarr; Hard for correct answers, and Hard &rarr; Medium &rarr; Easy for incorrect answers). Concurrently, a tabular Q-learning agent evaluates the state-action pair using the Bellman optimality equation."*

### Q2: Why did you choose Tabular Q-Learning instead of Deep Q-Networks (DQN)?
> *"With discrete difficulty actions (Easy, Medium, Hard) and a discretized state space (243 states), tabular Q-learning is mathematically exact, converges rapidly, does not require GPU training, avoids catastrophic forgetting, and provides complete transparency: every Q-value can be inspected directly in SQLite."*

### Q3: What is the Bellman Optimality Equation used in your project?
> *"$$Q(s, a) \leftarrow Q(s, a) + \alpha [ r + \gamma \max_{a'} Q(s', a') - Q(s, a) ]$$*
> *Where $\alpha = 0.1$ is the learning rate, $\gamma = 0.9$ is the discount factor, $r = +1.0$ for correct or $-1.0$ for incorrect, and $\max_{a'} Q(s', a')$ represents the maximum estimated future return."*

### Q4: How do you prevent question repetition in a quiz session?
> *"The `QuizSession` manager tracks `used_question_ids` in memory and executes parameterized SQL exclusion (`WHERE id NOT IN (...)`). If all questions at that difficulty level are exhausted, the engine resets the used list for that specific difficulty and samples again, never silently changing the required difficulty."*

---

## 19. Limitations & Future Enhancements

### Limitations
- The state space uses discrete categorical bins rather than continuous latent representations.
- Questions are currently multiple-choice text; dynamic programming code executions are not auto-graded.

### Future Enhancements
- **Deep Q-Networks (DQN):** Incorporating neural networks for continuous skill assessment.
- **Coding Sandboxes:** Direct in-browser code execution for programming exercises.
- **Spaced Repetition Integration:** Incorporating SuperMemo SM-2 algorithms for long-term retention.

---

## 20. Conclusion
The **Adaptive Quiz System Using Reinforcement Learning** successfully demonstrates the integration of machine learning and modern web technologies to solve real educational challenges. By coupling a deterministic pedagogical transition rule with tabular Q-learning, the platform guarantees bounded, structured difficulty adaptation while simultaneously quantifying reinforcement learning performance. The project satisfies all academic requirements for an MCA final-year capstone.
