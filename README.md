# Referral Scout

A Grok Bot assistant that helps you use LinkedIn to find the right people at your target companies, start real conversations, and earn referrals.

**Human in the loop, always.** Referral Scout researches and drafts. You review and approve every message before anything is sent. It never sends a message without your explicit OK.

---

## Who it's for

- Job seekers who want referrals instead of cold applications
- Anyone building a professional network in a new field, city, or industry
- People who want a steady, organized outreach habit without spending hours on research

---

## Setup

This is a template. Adapt each part to your own search.

### 1. Tell it your goal

Be specific. For example:

- **Target roles:** AI Product Manager
- **Company stages:** Series A to D startups, plus big-tech AI teams
- **Locations:** Seattle or US remote
- **Experience level:** roles asking for 3 years of experience or less

> **Tip:** Get the referral *before* you apply. Applying first can void the referral at many companies.

### 2. Set your outreach mix

- About **70% peer-level** people (folks doing the job you want)
- About **30% senior people and hiring managers**, approached with a "learning from you" framing rather than an ask

### 3. Set your message rules

- Lead with ownership and business scope (what you owned, what it moved)
- Connection notes stay **under 300 characters**
- Every note has a **personalized hook** and a **portfolio link**
- **No referral ask in the first message**

### 4. Sign in to LinkedIn

Sign in to LinkedIn in the bot's computer browser. LinkedIn Premium helps (more InMail and search filters) but is optional.

### 5. Set up routines

| Routine | When | What it does |
|---|---|---|
| **Daily scout** | Weekdays, e.g. 8:30 AM and 2:45 PM | Researches 3 to 5 new people, finds a hook for each, drafts notes, and hands them to you for approval. Read-only: it does not send anything. |
| **Acceptance check** | Weekdays, around 9 AM | Checks who accepted or replied and drafts follow-ups for your approval. |

### 6. Keep one outreach log

Keep a single outreach log (a spreadsheet or file the bot owns) so nobody gets contacted twice.

### 7. Optional: scheduling

Schedule calls yourself from your own calendar, or let the bot suggest times for you to confirm.

### Starter prompt

Copy, edit the parts in brackets, and send this to your own Grok Bot:

```text
I want you to be my "Referral Scout": a LinkedIn networking assistant that helps me
find the right people at target companies and earn referrals.

My goal:
- Target roles: [e.g. AI Product Manager]
- Company stages: [e.g. Series A-D startups plus big-tech AI teams]
- Locations: [e.g. Seattle or US remote]
- Experience level: [e.g. roles asking 3 years or less]
- My portfolio link: [your link]

Rules:
1. Human in the loop. You research and draft. Never send any message, connection
   request, or follow-up without my explicit approval of the exact text.
2. Outreach mix: about 70% peers, 30% senior people or hiring managers.
   Use a "learning from you" framing for senior people.
3. Messages lead with ownership and business scope. Connection notes stay under
   300 characters, include a genuine personalized hook and my portfolio link,
   and never ask for a referral in the first message.
4. Before sending an approved note: confirm the person still works there, check
   we haven't messaged before, send the approved text exactly once, and verify it
   went through. If a hook can't be verified, skip that person and tell me.
5. Keep one outreach log as the single source of truth so nobody is contacted twice.
6. Remind me to get a referral before I apply, not after.

Routines (weekdays):
- Daily scout at [8:30 AM] and [2:45 PM]: research 3-5 new people with sourced
  hooks and draft notes for my review. Read-only, no sending.
- Acceptance check at [9:00 AM]: see who accepted or replied and draft follow-ups
  asking for a 15-20 minute chat, for my approval.

I'm signed in to LinkedIn in your computer's browser. Start by confirming these
settings, creating the outreach log, and setting up the routines.
```

---

## Workflow

1. **Pick a target.** Name a company, or let the daily scout source candidates. For a market sweep, it builds a company map with stage, funding, open PM roles, and experience requirements, tiered A, B, or C.
2. **Research.** It covers company basics and open roles, then finds 5 to 6 people per company. It prefers peers, local people, and shared alumni or background, and caps the number of senior people. Each person gets a genuine, sourced hook: a recent post, a blog, a shared school, or a career path.
3. **Draft.** One personalized note per person, checked for length and style.
4. **Review.** You see each person, why they're worth talking to, and the exact draft. You pick which ones to send.
5. **Send and verify.** It re-confirms the person still works there, checks for earlier messages, sends the approved text exactly once, and verifies it went through. If a hook can't be verified, it skips that person rather than send something false.
6. **Log and follow up.** When someone accepts, it drafts a follow-up asking for a 15 to 20 minute chat. That follow-up is approved by you before it goes out.

---

## Real results

From the outreach log, **Sep 24 to Oct 2, 2026** (7 working days):

- About **120 distinct people** contacted across about **25 companies' teams** (for example Microsoft, Google, OpenAI, Anthropic, Databricks, Snowflake, Airbnb), plus Seattle startups
- **20+ connection acceptances**, each followed by a personalized follow-up
- **At least 5 direct replies**
- **2 coffee chats**, plus one being scheduled
- A **Seattle startup map**: 38 relevant Series A+ companies (13 tier A), with 4 open PM roles asking for 3 years or less

### Example run

Three target companies: a healthcare voice-AI startup, a large CX company with an AI product suite, and a well-funded agent company.

- **18** people researched and drafted, all 18 approved
- **14** connection requests sent and verified
- **4** skipped:
  - 2 had no Connect option
  - 1 had left the company
  - 1 had a hook that turned out to be wrong
- Within about 12 hours, **2 accepted** and received approved follow-ups

---

## Lessons learned

- **Verify the hook before sending.** A wrong detail hurts more than a generic note. When in doubt, skip.
- **Keep one source of truth.** A single outreach log is what prevents duplicate messages.
- **Build relationships before asking for referrals.** Start with curiosity and a short chat. The referral conversation goes better once there's a real connection.

---

## License

MIT. See [LICENSE](LICENSE).
