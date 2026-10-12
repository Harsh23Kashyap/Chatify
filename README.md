# CustomChat

A chat app over your documents, set up with one YAML file. Answers cite their sources. Starts in offline Demo mode: no key, account or paid calls.

## Start

No Python, Git or uv needed. Open Terminal (macOS/Linux) or PowerShell (Windows) and run:

```sh
curl -fsSL https://raw.githubusercontent.com/Harsh23Kashyap/customchat/main/start.sh | sh
```

```powershell
& { $f = Join-Path ([IO.Path]::GetTempPath()) ([IO.Path]::GetRandomFileName() + '.ps1'); try { Invoke-WebRequest https://raw.githubusercontent.com/Harsh23Kashyap/customchat/main/start.ps1 -OutFile $f; & powershell -NoProfile -ExecutionPolicy Bypass -File $f } finally { Remove-Item $f -ErrorAction SilentlyContinue } }
```

The app opens in your browser (or open the printed localhost URL). Ctrl+C stops it. Run the same command in the same folder to come back to your chats. Review [start.sh](start.sh) or [start.ps1](start.ps1) before running downloaded scripts.

**Have uv?** `uvx customchat-app start`

**Prefer pip?** In an empty folder:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install customchat-app
.venv/bin/python -m customchat start
```

On Windows use `py -3 -m venv .venv` and `.\.venv\Scripts\python.exe`. The package is `customchat-app`; `customchat` on PyPI is a different project. Both install paths use an isolated environment, so nothing touches your system Python.

## macOS with Homebrew Python

From this repository folder, one command installs the current published package in a private environment and opens the app:

```sh
python3 start_local.py
```

This handles Homebrew's `externally-managed-environment` error without sudo, global pip, activation, or `--break-system-packages`. Requires Python 3.10+ and internet for installation. It reuses `.customchat-venv`; it never deletes or resets your app, chats or keys. Ctrl+C stops the app. Run the same command from the same folder to resume.

To reopen a different existing workspace, pass its folder (the one containing `app.yaml`):

```sh
python3 start_local.py --directory /path/to/my-chat
```

Starts offline Demo for a new workspace. Existing workspaces keep their settings. Add `--no-browser` or `--port 8081` if needed. This installs the published package, not uncommitted source changes in your clone.

## Make it yours

```sh
uvx customchat-app start --directory my-chat
```

Edit `my-chat/app.yaml`, add documents, and open Configuration to pick a model, look and sources. Keep keys in environment variables or the private local store, never in YAML or Git. Add `--lock-config` for a chat-only app. See the [configuration reference](docs/DESIGN.md).

## Features

- Upload files or add web links. Reads PDF, text/code, DOCX, XLSX, PPTX, ODT and, with Tesseract, images.
- Quick, Standard and Deep answer modes.
- Saved chats with bounded history, a temporary chat mode and an optional profile.
- Themes, light/dark, logo, animated emojis and a live preview.
- Budget limits, document freshness checks and a portable app export.

Demo is the default. In Configuration, choose a provider card with its icon; Show more reveals the remaining providers. Pick a returned model or type its name, then test the connection. Selecting a card alone does not verify it. Type in Find a setting for free local matches as you type. Ask AI is a separate explicit model request. Guide replays the Configuration walkthrough, including the App Studio, background builds, retry, validation, save/restart and export.

## Prompts and code helpers

Open Configuration, then **Prompts** or **Code helpers** in the sidebar. Both are visible in Simple and Advanced. Prompts can be edited or generated for review. Code helpers generate Python, check compilation and safety, and only run when you press Try it. In offline Demo, generation returns a starter template, not model-written code.

## More

[Install options](docs/INSTALL.md) · [Hosting](docs/DEPLOY_OPTIONS.md) · [Architecture](docs/DESIGN.md) · Tests: `python -m unittest discover -s tests`

Counterpart of [Custom-Nerd](https://github.com/Harsh23Kashyap/Custom-Nerd). Harsh Kashyap, Shela Wu. Advisor: Dennis Shasha. MIT license.

### Load a shared Nerd

Open Configuration → Load and share Nerds. Drop a ZIP or app.yaml, read the readiness check, review any Python connector, then Load and run. A separate workspace opens; the current app stays intact. Keys, accounts and chat history never come with the bundle. Python runs with your local user permissions after your review. Import checks are offline, not a model/network test.

`customchat-app run app.yaml` opens the browser after the server is ready. Use `--no-browser` for servers or terminals without a desktop.

### Build with AI

In Configuration, select your provider and model and save its key, then open **Build with AI**. Describe who the app is for, what it should answer and which sources it should use. It uses the currently selected model for setup without changing the running chat.

The App Studio has three connected steps: **Describe**, **Review changes**, **Save**. The active step, completed milestones and transitions stay clear on phones and desktop. Animations have a static reduced-motion fallback. Typing never calls a model.

Complete builds make separate calls for settings, colors, fonts, layout, wording, all nine pipeline prompts, API recommendations and inert helper drafts. Up to three calls run together, with at most 36 calls including final review and an optional logo. Progress shows actual completed areas and queued, waiting, received or retry states, not estimated percentages. Close and reopen the dialog while it works. Retry failed parts only; cancel stops pending work. In-flight calls may finish and cost money. Jobs stay in server memory and are lost on restart.

Inspect the design preview and edit the grouped fields or Advanced YAML. **Validate and review** runs locally, invalidates after edits and makes no model request. Confirm Save separately, then restart to apply. Download the merged YAML or a config-only ZIP. Nothing saves automatically and generated helper code is never installed or executed.

Provider limits still apply. A dollar cap blocks non-Demo calls when verified billing is unavailable. Missing keys, source paths, assets and unknown API endpoints need your review; API recommendations and helpers are drafts, not verified integrations.

### Workspace tools

- **Setup:** local readiness checks and explicit model/source checks with a send/cost review.
- **Workspace:** open, stop or remove imported Nerds after review. Removal affects only that imported workspace.
- **Changes:** compare and restore the last 30 model/retrieval revisions after review. Concurrent changes invalidate review; appearance, prompts and keys are not included.
- **Backup:** private JSON chat export and additive restore. Credentials, profiles, uploads, feedback and model files are not backed up. Chat text and evidence may be private.
- **Test questions:** save up to 10 questions and compare current/previous answers after service/cost review. This is not an accuracy score.
- **Deploy:** search guidance, prepare a selected-model account/audience/cost/rollback plan or copy a prompt for another AI. No hosting resource is created and nothing deploys automatically.

### Portability and safety

YAML restores configuration, appearance, pipeline prompts, inert helper drafts and API recommendations. Documents and executable connector files require a ZIP. Keys stay excluded by default. Sensitive-key export requires an explicit selection and warning confirmation. Imported key entries move into private workspace storage and are removed from the imported app file. Accounts and conversations are never imported.

Bundle review checks paths, declared files, imports and detected code patterns without running bundle code or contacting its destinations. It is not a safety verdict. Review all Python before allowing it to run. Imported connectors default to a bounded subprocess with an environment allowlist, timeout and output caps; **this is not a security sandbox**. Code can access host files and the network. On Windows, cancellation does not guarantee that child processes stop.

Model inputs and evidence remain untrusted data. Prompt boundaries and parser/AST checks reduce tested failure paths, not all prompt injection or hallucination. Citation syntax does not prove semantic support. Optional support checks are model-dependent, and streaming may show text before final checks.

The About page has feature tabs, six shown first with Load more. Local examples and previews are not live-service tests. Real providers, external APIs, generated prompts and code need your review.

See [CHANGELOG.md](CHANGELOG.md) for release history.
