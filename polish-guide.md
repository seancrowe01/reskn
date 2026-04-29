# Polish Guide

The 8 steps you do every time a deal closes.

This is the only document you need open when polishing a site. Follow it top to bottom.

---

## Before you start

Sean has messaged you. You should have:

- The slug (like `kevin-brogan-plumbing`)
- A folder of stuff from the client (photos, Gas Safe number, opening hours, real reviews if any)
- The domain they want to use (like `kevinbroganplumbing.co.uk`)

If anything is missing, ping Sean before starting. Do not guess.

---

## Step 1 - Pull the latest code (1 minute)

Open your terminal, go to the reskn folder, and pull the latest version:

```bash
cd reskn
git pull
```

This makes sure you have all the newest scripts and prompts.

---

## Step 2 - Find the site (1 minute)

The robot has already generated a draft for every lead. Yours is at:

```
out/<slug>/index.html
```

Example: `out/kevin-brogan-plumbing/index.html`

If for some reason it does not exist, generate it:

```bash
python scripts/generate_site.py "Kevin Brogan"
```

Open the file in your browser to see the current state. Just double click it.

---

## Step 3 - Drop in the real photos (5 minutes)

Make a folder for client photos:

```
out/<slug>/assets/
```

Copy every photo the client sent into that folder. Rename them so they make sense:

- `team-photo.jpg` for the team shot
- `boiler-install-1.jpg`, `boiler-install-2.jpg` etc for work shots
- `van.jpg` for their branded van
- `logo.png` for their logo if they have one

Keep file names lowercase, no spaces, dashes between words.

---

## Step 4 - Tell Claude to swap the photos in (5 minutes)

Open the site folder in Claude Code. Then say something like:

> "Replace the hero stock photo with `assets/team-photo.jpg`. Replace the 'why us' section background with `assets/van.jpg`. Add `assets/boiler-install-1.jpg` to the services grid. Keep all the existing copy."

Claude will edit the HTML for you. Refresh the browser to check it looks right.

---

## Step 5 - Add the real client details (10 minutes)

Tell Claude to update the real details. Paste them directly into the message:

> "Update these details in the site:
> - Gas Safe registration number: 545454
> - Phone: 02890 123 456
> - Email: kevin@kevinbroganplumbing.co.uk
> - Opening hours: Mon-Fri 7am to 7pm, Sat 9am to 4pm, Sun emergency only
> - Years in business: 16 (since 2009)
> - Service area: add Comber, Dundonald, Ballygowan, Saintfield, Killyleagh"

Claude will replace every placeholder for you. Refresh the browser.

---

## Step 6 - Real reviews (only if client sent them) (5 minutes)

If the client sent screenshots of real Google reviews, transcribe the text and tell Claude:

> "Replace the placeholder reviews with these real ones:
> 1. Sarah M, Belfast, 5 stars: 'Kevin came out same day, fixed our boiler in an hour. Brilliant service.'
> 2. James T, Ballymena, 5 stars: '[etc]'
> 3. [etc]"

If the client did NOT send reviews, leave the placeholders alone. They already say "Real Google review" with a link to their Google Business Profile.

---

## Step 7 - Final eyeball check (5 minutes)

Walk through the whole site one last time on your phone. Things to check:

- Phone number works when you tap it (should open the dialler)
- All photos load (no broken images)
- No `<!-- TODO -->` comments left in the file
- No "your business name here" placeholders
- Hero looks sharp on a small screen
- Reviews section has 5 star visuals
- Footer has the right opening hours

If anything looks off, ask Claude to fix it.

---

## Step 8 - Deploy to their domain (10 minutes)

When you are happy with the site, run:

```bash
python scripts/deploy_vercel.py kevin-brogan-plumbing --domain kevinbroganplumbing.co.uk
```

This does three things automatically:

1. Pushes the site to Vercel
2. Connects the domain
3. Prints out a list of DNS records the client needs to add at their domain provider

Send the DNS records to Sean. Sean sends them to the client. Once the client adds them, the site goes live (usually within an hour).

---

## After it goes live

1. Send Sean the live URL.
2. Mark the deal `Delivered` in GHL.
3. Move on to the next one.

---

## How long this should take you

About 30 to 45 minutes per site, once you have done it a few times.

If it takes you more than an hour, ping Sean. Something might be off with the source draft and we can fix it together.

---

## Common mistakes to avoid

- **Editing the wrong file.** Always work in `out/<slug>/index.html`. Never touch the prompts or scripts.
- **Inventing a Gas Safe number.** If the client did not send one, use `Gas Safe registered (number on request)`.
- **Forgetting to test the phone link.** Tap it on your actual phone before you ship.
- **Pushing photos to git.** Photos go in `out/<slug>/assets/` which is gitignored. Do not commit them.
- **Changing the structure.** The 9 sections are locked. Do not add or remove sections without asking Sean.

---

## When you are stuck

Paste the problem into Claude. Claude has the full project context from `CLAUDE.md` and will help.

If Claude cannot fix it in 15 minutes, ping Sean. Do not waste a whole afternoon stuck on one site.
