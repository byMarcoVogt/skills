# Ghost deck

Before any slides are built, create ghost decks for this presentation. A ghost deck is the sketch of a deck before the actual deck: the key message it lands on and the storyline that gets there. Each slide, or group of slides, tells one story that serves that message; a story can be cut onto one slide or several, such as a sequence or a contrast pair. Make the ghost decks real alternatives: they may argue a different key message, use different stories, order them differently or cut them differently. Show options wherever a decision is open, so the reader can choose.

Write `data.js` in exactly this format:

```js
window.GHOST = {
  title, audience, purpose,
  decks: [{ id: "A", message, why, logic, recommended: true|false,   // message = the key takeaway this deck lands on, one sentence
    sequence: [{ story: "S1", cut: "S1a" }] }],
  stories: [{ id: "S1", claim,                        // the one point this story makes
    from: ["S3", "S4"],                               // optional: the stories this one merges
    cuts: [{ id: "S1a", kind,                          // free text for a group of slides, e.g. "sequence", "contrast pair"; omit for one slide
      slides: [{ id: "S1a-1", title,                  // action title
        keyInfo: [{ text, status: "available"|"partial"|"missing", sources: ["R1"],
          calc }],                                    // optional: how a figure was derived, if it is your own calculation
        substance: "thin"|"fits"|"too much",          // thin = not enough for a slide yet; too much = split it or move part to the appendix
        exhibit }] }] }],                             // rough exhibit idea
  decisions: [{ id: "D1", question, options: [{ id: "D1a", label }], recommended: "D1a" or null, why }],
                                                      // only questions that choosing a deck does not already settle
  sources: [{ id: "R1", label, url }]                 // for material in the folder: label = file plus page or statement, url = file name
};
```

Build the page with `python -I <this skill's folder>/storyline/build_artifact.py data.js ghost-decks.html "<short title>"` and publish it with the Artifact tool.
