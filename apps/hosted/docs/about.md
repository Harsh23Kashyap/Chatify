# About this site

This is a live demo of Chatify, an open-source app that turns your own
documents, web pages and APIs into a chat that answers with citations.

## What you can do here

- **Chat right away.** A model is already configured on this site, so you
  can ask a question in the box at the bottom of the Chat page and get a
  cited answer. No setup, no key, no install.
- **Build your own app with AI.** Open Configuration and choose
  **Build with AI**. It is the easiest path: describe the app you want in
  plain words, and AI drafts the full setup for you to review, edit and
  download. Nothing is saved until you confirm it.
- **Run it on your own computer.** The Run locally page has the single
  command: `uvx --from chatify-app chatify start`.

## What Chatify is

Chatify answers questions only from the sources the builder chose:
uploaded documents, saved web pages, or live APIs such as PubMed. Every
answer cites the exact passages it used, so you can check each claim.
The builder owns the result: one YAML file holds the whole configuration,
and the audience gets a finished app with its own name, colors and sources.

## About this demo

This demo is hosted on a free plan, so it sleeps when nobody is using it.
If the site has been quiet, the first page load can take up to a minute
while it wakes up. Data on this demo is temporary and resets when the
host restarts. For anything you want to keep, run Chatify locally.
