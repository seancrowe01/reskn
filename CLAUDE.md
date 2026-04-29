# Reskn

Hi Giezel. This is your project guide. Read it once and you will know what to do.

## What we do

We help small local businesses (mostly plumbers and heating engineers in Northern Ireland for now) get a proper website.

Most of them have no website. Some have an old one from 2012 that looks awful. We sell them a one-off £800 redesign and they own it forever.

The robot (Claude AI) builds the first draft of every site. Your job is to take that draft and finish it like a real designer would. Add the real photos, the real reviews, the real Gas Safe number, and put it live on their domain.

## How a sale happens

1. We scrape Google Maps and find local plumbers with no website (or a bad one).
2. The robot builds a draft website for each one.
3. Jake (our caller) rings them up and shows them the draft.
4. They say yes and pay £800.
5. You polish the site and put it live. Done.

You only ever come in at step 5.

## The folders

```
reskn/
  CLAUDE.md         <- you are reading this
  README.md         <- quick start (run this first time you clone)
  polish-guide.md   <- the 8 steps you do every time a deal closes
  prompts/          <- the brief we give the robot to build sites
  scripts/          <- the tools you run (don't change these unless you want to)
  data/             <- list of leads (mostly hidden, only Sean has access)
  out/              <- every generated site lives in its own folder here
```

## What you do every time a deal closes

Sean will message you with the client's slug (like `kevin-brogan-plumbing`) and a folder of real photos and info from the client.

Then you follow `polish-guide.md`. Every single time. It is 8 short steps.

Open it in your Claude Code window. Claude will do most of the work. You just guide it.

## How to tell Claude what to do

When you open this repo in Claude Code, Claude reads this file automatically. So Claude already knows:

- What Reskn is
- The brand voice rules (below)
- How the files are organised
- Don't suggest changes to the system unless asked

You can just say things like:

- "Polish the kevin-brogan-plumbing site with these photos and details: [paste]"
- "The hero photo looks too American. Swap it for a UK boiler engineer photo."
- "Add a Gas Safe number 545454 to the trust strip."
- "Deploy kevin-brogan-plumbing to kevinbroganplumbing.co.uk"

Claude will do it.

## Brand voice rules (very important)

When writing or editing any copy on a site, follow these:

1. **British English only.** It is "colour" not "color". "Centre" not "center". "Boiler" not "furnace".
2. **Plain trade voice.** Like a friendly local plumber would talk. Not corporate. Not American sales.
3. **No filler words.** Avoid "we strive for excellence", "your trusted partner", "best in class". Just say what they do.
4. **Short sentences.** A homeowner reading this on their phone in 5 seconds. Make every word count.
5. **No fake details.** Never make up a Gas Safe number. Never make up reviews. If we do not have it, leave a note in the HTML like `<!-- TODO: client to confirm Gas Safe number -->`.
6. **Phone first.** Every Call to Action button is a phone number. No contact forms. No email forms. Just `tel:+44...` links.

## What every generated site has

Every `out/<slug>/index.html` will already include all 9 sections in this order:

1. Sticky nav (logo + 4 links + phone CTA)
2. Hero (big headline, sub-line, two CTAs)
3. Trust strip (3-4 stats)
4. Services grid (6 cards)
5. Why us (4 reasons)
6. Reviews (3 cards)
7. Service area (towns they cover)
8. CTA banner (full width)
9. Footer

You should not add or remove sections. Just polish the content inside them.

## Common polish jobs

| What client asks for | What you say to Claude |
|----------------------|------------------------|
| Replace stock photo with their own | "Replace the hero image with `assets/team-photo.jpg`. I have dropped it in the assets folder." |
| Add their real Gas Safe number | "Add Gas Safe number 545454 to the trust strip and footer." |
| Change the phone number | "Update every phone number in the file to 02890 123 456." |
| Make the colour scheme match their van | "Change the brand primary colour to #C8102E (their van red). Keep the rest." |
| Add 5 more towns to service area | "Add Comber, Dundonald, Ballygowan, Saintfield, Killyleagh to the service area block." |
| They sent real Google review screenshots | "Replace the placeholder reviews with these real ones: [paste]." |
| Change opening hours | "Update opening hours to Mon-Fri 7am to 7pm, Sat 9am to 4pm, Sun emergency only." |

## You do NOT run any Python

Sean handles all robot work — scraping leads, generating drafts, deploying live sites. You only edit HTML files in `out/<slug>/`.

The flow is:

1. Sean Slacks you a zip with the draft + photos + details
2. You unzip into `out/<slug>/`
3. You polish the HTML
4. You zip the folder back up and Slack it to Sean
5. Sean deploys it

You never need Python installed. You only need git, an editor with Claude (Cursor or Claude Code), and a browser.

## Sean-only commands (for reference, do not run these)

```bash
# Generate a site for one client (if not already generated)
python scripts/generate_site.py "Kevin Brogan"

# Generate sites for all the leads in HOT-leads.csv
python scripts/batch_generate.py

# Put a finished site live on a domain
python scripts/deploy_vercel.py kevin-brogan-plumbing --domain kevinbroganplumbing.co.uk
```

That is it.

## When something goes wrong

If a script breaks, paste the error into Claude and say "fix this". Claude has full context from this file.

If you are stuck for more than 15 minutes, ping Sean. Do not waste your time guessing.

## What NOT to do

- Do not edit anything in the `prompts/` folder. That is the master brief for the robot. If you want to change how every site is generated, ping Sean first.
- Do not edit anything in `scripts/`. Same reason.
- Do not push real client data (phone numbers, addresses, photos) to the public internet. Real photos go in `out/<slug>/assets/` which is gitignored.
- Do not write any reviews that did not come from a real client. We use 5-star visuals with placeholder text and "see all reviews on Google" link until the client sends real ones.
- Do not invent a Gas Safe registration number. If we do not have it, write `Gas Safe registered (number on request)`.

## Tools you might want

- **Claude Code** (terminal) - what you are using now. Best for bulk edits and deploys.
- **Claude.ai Artifacts** - paste an HTML file in, see it render live, chat to edit it visually. Good for finicky design tweaks. Then copy the final HTML back into the file.

Both work because every site is one self-contained HTML file with Tailwind via CDN. No build step. Just open `out/<slug>/index.html` in any browser to preview.

## Quick reference

- **Default brand colour for plumbers/heating:** deep blue `#0B5394`
- **Default font:** system-ui (no custom Google Fonts)
- **Hero photo source:** Unsplash via CDN if no client photo
- **Reviews placeholder:** 5 star visuals with "Real Google review" label and link to their Google Business Profile
- **Default opening hours if unknown:** Mon-Fri 8-6, Sat 9-1, Sun emergency only

## Final note

The robot draft is meant to look 80 percent finished on the cold call. Your job is the last 20 percent. Real photos. Real Gas Safe number. Real reviews. Real domain.

That last 20 percent is what makes the site feel like theirs, not ours.

Take your time on each one. Quality over speed. We are building a name in NI.
