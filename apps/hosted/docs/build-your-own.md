# Build your own chat app

The short version: open **Configuration**, choose **Build with AI**, and
describe your app in one sentence. That is the easiest path, and it is the
one we recommend.

## The easy path: Build with AI

1. Open the **Configuration** page (top of this site).
2. Choose **Build with AI**.
3. Describe the app you want in plain words. For example: "A reading
   assistant over my gardening notes" or "A diet app that cites PubMed
   papers."
4. Wait while it drafts the setup: the name, the look, the prompts and
   suggested sources. On this site the model is already configured, so
   there is nothing to connect first.
5. **Review the draft.** Read it, change anything, and validate it.
   Nothing is saved until you confirm.
6. **Download the result** as a YAML file or a config-only ZIP.
7. Run it on your own computer with one command (see the Run locally
   page): `uvx --from chatify-app chatify start`, then load your file in
   Configuration under Load and share.

## The manual path

Every setting Build with AI can draft is also editable by hand on the
Configuration page: provider and model, sources and APIs, prompts,
appearance, and limits. Manual settings are for advanced tweaks; most
people should start with Build with AI.

## Running locally: the details

1. Open a command window. Mac: Cmd+Space, type Terminal, press Return.
   Windows: open Start, type PowerShell. Linux: open Terminal.
2. Install uv once. Mac/Linux:
   `curl -LsSf https://astral.sh/uv/install.sh | sh`
   Windows PowerShell:
   `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   Close and reopen the command window afterwards.
3. Start Chatify: `uvx --from chatify-app chatify start`
   Your browser opens the app automatically.

## Questions people hit the first time

- **The welcome guide**: it appears on first launch, you can skip it at
  any time, and it never locks the app while it is open.
- **Where do I type my question?** In the box at the bottom of the Chat
  page. Press Enter to send.
- **Can I use a web page as a source?** Yes. In Add sources, choose
  "Add a web page" and paste a public address. Chatify stores that page's
  text and answers over it.
- **File size**: files can be up to 8 MB each. If a file is too large,
  remove it and add a smaller one. Large PDFs often fit once figures are
  removed.
- **Does my data leave my computer?** When you run locally, no:
  documents, keys and chats stay on your machine. On this hosted demo the
  model is shared and data is temporary, so do not upload anything
  private here.
