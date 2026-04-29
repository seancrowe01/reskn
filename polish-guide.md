# Polish Guide

The 8 steps you do every time a deal closes.

This is the only document you need open when polishing a site. Follow it top to bottom.

If this is your first time, read `START-HERE.md` first.

---

## Step 0 - Wait for Sean's Slack

Sean will Slack you when a deal closes. His message looks like this:

> Hey G. Kevin Brogan deal closed.
> Slug: kevin-brogan-plumbing
> Domain: kevinbroganplumbing.co.uk
> [zip file attached]

The zip will contain:

- `index.html` — the robot draft of the site
- `assets/` — folder with real client photos (the team, the van, work shots)
- `details.txt` — Gas Safe number, real opening hours, real years in business, real reviews if any

If anything is missing, message Sean before starting. Do not guess.

---

## Step 1 - Pull the latest code (1 minute)

In your terminal:

```bash
cd reskn
git pull
```

This makes sure you have the newest version of the project. Always do this first.

---

## Step 2 - Drop Sean's zip into the right place (2 minutes)

Make a new folder for this client under `out/`:

```
out/kevin-brogan-plumbing/
```

Unzip Sean's file in there. You should now have:

```
out/kevin-brogan-plumbing/
├── index.html
├── details.txt
└── assets/
    ├── team-photo.jpg
    ├── van.jpg
    └── ... etc
```

The `out/` folder is hidden from git (it stays on your laptop only) so client photos never accidentally get pushed to the internet.

---

## Step 3 - Open the site to see what you are working with (1 minute)

Two windows side by side:

**Browser:** double click `index.html` to see the current state of the site
**Editor:** open the same `index.html` in your code editor (Cursor or Claude Code)

You will swap photos and text in your editor, then refresh the browser to check.

---

## Step 4 - Tell Claude to swap the photos in (5 minutes)

In Claude Code or Cursor, paste this kind of message:

> "Replace the hero stock photo with `assets/team-photo.jpg`. Replace the 'why us' background with `assets/van.jpg`. Add `assets/boiler-install-1.jpg` to the services section. Keep all the existing copy the same."

Claude does the file edit for you. Refresh the browser to check it looks right.

If a photo is at the wrong size or angle, ask Claude to adjust it (e.g. "make the hero photo cover the full width" or "crop the van photo wider").

---

## Step 5 - Add the real client details (10 minutes)

Open `details.txt` (Sean dropped it in the same folder). You will see things like:

```
Gas Safe number: 545454
Phone: 02890 123 456
Email: kevin@kevinbroganplumbing.co.uk
Opening hours: Mon-Fri 7am-7pm, Sat 9am-4pm, Sun emergency only
Years in business: 16 (since 2009)
Service area: Ballymena, Antrim, Carrickfergus, Larne, Comber, Dundonald, Ballygowan
Real reviews from client:
  Sarah M, Belfast, 5 stars: "Kevin came out same day, fixed our boiler in an hour. Brilliant service."
  James T, Ballymena, 5 stars: "Fair price and proper job. Will use again."
```

Tell Claude:

> "Update the site with these real details: [paste everything from details.txt]"

Claude will replace every placeholder. Refresh the browser.

---

## Step 6 - Eyeball check on your phone (5 minutes)

Open the file on your phone too. Easiest way:

- Send yourself the file via AirDrop (Mac) or email (Windows)
- Open it in Safari/Chrome on your phone

Check:

- Phone number works when you tap it (should open the dialler)
- All photos load, none are broken
- Hero looks sharp on a small screen
- No `<!-- TODO -->` comments left in the file
- No "your business name here" placeholders
- Reviews section has 5 star visuals and named reviewers
- Footer has correct opening hours and address

If anything looks off, ask Claude to fix it.

---

## Step 7 - Zip the finished folder (2 minutes)

When the site looks great, zip the whole folder up:

- Mac: right-click the folder, "Compress"
- Windows: right-click the folder, "Send to → Compressed (zipped) folder"

Name it `kevin-brogan-plumbing-FINAL.zip` (or whatever the slug is).

---

## Step 8 - Slack the zip back to Sean (2 minutes)

Slack message to Sean:

> Done with kevin-brogan-plumbing. [zip attached]
> Notes: [anything Sean should know — e.g. "had to crop the van photo wider, looked stretched", or "client did not send a Gas Safe number so left as 'number on request'"]

Sean takes it from there. He puts it live on the client's domain.

---

## After it goes live

Sean will message you when the site is live. That is when the job is done.

Mark the deal `Polished` in your tracker (Trello or however Sean asks).

Move on to the next one.

---

## How long this should take

About 30 to 45 minutes per site once you have done a few. First one might take an hour. That is normal.

If it takes you more than 90 minutes, ping Sean. Something is probably off with the source draft and we can fix it together.

---

## Common mistakes to avoid

- **Editing the wrong file.** Always work in `out/<slug>/index.html`. Never touch the prompts or scripts folders.
- **Inventing a Gas Safe number.** If the client did not send one, use `Gas Safe registered (number on request)`.
- **Forgetting to test the phone link.** Tap it on your actual phone before you send the zip back.
- **Pushing photos to git.** Photos go in `out/<slug>/assets/` which is gitignored. Do not commit them. The folder is hidden from git on purpose.
- **Changing the structure.** The 9 sections are locked. Do not add or remove sections without asking Sean.
- **Not pulling first.** Always `git pull` at the start. Sean might have updated the prompts or the brand voice rules.

---

## When you are stuck

1. Paste the problem into Claude. Claude has the full project context from `CLAUDE.md` and will help.
2. If Claude cannot fix it in 15 minutes, ping Sean.

Do not waste a whole afternoon stuck on one site. We will fix it together in 5 minutes.
