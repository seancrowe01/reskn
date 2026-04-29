# Hi Giezel

Welcome to Reskn. Read this whole page once. After that you are ready to work.

If anything below is unclear, message Sean. Do not waste time guessing.

---

## What we do (in plain English)

We help small local businesses (mostly plumbers in Northern Ireland) get a proper website.

The robot builds the first draft. Your job is to take that draft and finish it like a real designer would. Add the real photos, the real details, make it look great.

When you are done, you Slack the finished file back to Sean. He puts it live.

---

## What you need on your computer

You need 3 things installed. Do this once and never again.

**1. Git** (so you can clone this repo)
- Mac: open Terminal and type `git --version`. If it asks you to install, say yes.
- Windows: download from https://git-scm.com and install with default options.

**2. A code editor with Claude built in**
- We use **Claude Code** (the terminal one) or **Cursor** (the desktop one with Claude inside). Either works.
- Claude Code: https://claude.com/product/claude-code
- Cursor: https://cursor.sh

**3. A web browser**
- You already have one. Chrome or Safari is fine.

**You do NOT need Python.** Sean handles all the robot stuff. You only ever edit HTML files.

---

## First time setup (10 minutes)

Open your terminal (Mac) or Git Bash (Windows). Then:

```bash
# 1. Clone the repo (one time only)
git clone https://github.com/seancrowe01/reskn.git

# 2. Go into the folder
cd reskn

# 3. Open it in your editor
# If you use Cursor: type "cursor ."
# If you use Claude Code: type "claude" then it opens here
```

That is it. You are set up.

---

## Take a look at a finished example

Before your first real job, look at what a finished-by-robot site looks like.

Open this file in your browser by double clicking it:

```
samples/ards-comber-boiler-services/index.html
```

Have a scroll. This is the kind of draft Sean will send you. Notice:

- 9 sections (nav, hero, trust strip, services, why us, reviews, area, CTA banner, footer)
- All Tailwind CSS for styling
- Phone numbers are clickable on mobile
- Stock photos (these will be swapped for real photos later)
- Placeholder reviews (these will be swapped if client sends real ones)

Open the HTML file in your editor too. Have a poke around so you know how it is built. Tailwind classes everywhere, all in one file.

---

## How a job comes to you

Sean Slacks you when a deal closes. His message looks like this:

> Hey G. Kevin Brogan deal closed.
> Slug: kevin-brogan-plumbing
> Domain they want: kevinbroganplumbing.co.uk
> [zip file with photos and details attached]

The zip will have:

- `index.html` — the robot draft
- `assets/` — folder with real client photos
- `details.txt` — Gas Safe number, real opening hours, real years in business, real reviews

---

## What you do with it (the 8 steps)

Open `polish-guide.md` and follow it top to bottom.

Short version:

1. Unzip Sean's file into a new folder under `out/`
2. Open the `index.html` in your editor and your browser side by side
3. Tell Claude what to swap in (photos, real details, opening hours)
4. Refresh browser, check it looks right
5. Test the phone number on your phone
6. Zip the finished folder back up
7. Slack it back to Sean
8. Mark the deal `Polished` in your Trello (or wherever Sean asks)

That is the whole job.

---

## How long should it take

About 30 to 45 minutes per site once you have done a few. The first one might take an hour. That is normal.

If it takes you more than 90 minutes, ping Sean. Something is probably off and we can fix it together.

---

## What you do NOT touch

- Anything in `prompts/` (that is the robot's brief)
- Anything in `scripts/` (that is Sean's tools)
- The `samples/` folder (those are reference examples)

If you think any of those need changing, ping Sean first.

---

## When you are stuck

1. Paste the problem into Claude. Claude has the full project context from `CLAUDE.md` and will help.
2. If Claude cannot fix it in 15 minutes, ping Sean.

---

## Pay and hours

Sean handles that side. Just message him with how many you finished each week.

---

## Quality over speed

We are building a name in NI. One bad site that goes live is worse than 5 sites that are perfect. Take your time.

The robot draft is meant to be 80 percent there. Your job is the last 20 percent. Real photos. Real details. Real domain. That last 20 percent is what makes the site feel like theirs, not ours.

Welcome aboard. Go open the sample site now and have a look.

— Sean
