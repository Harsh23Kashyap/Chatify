# Chatify

A chat app for your documents. Ask a question, follow the citations, and keep the conversation going. Configure the model, sources and look in your browser.

It starts in offline Demo mode, with no API key or paid calls. Demo uses built-in answers, not a live AI model.

![Chatify answering a question with sources in offline Demo mode](https://raw.githubusercontent.com/Harsh23Kashyap/chatify/v0.1.27/docs/screenshots/chat.png)

## Install and start

With [uv](https://docs.astral.sh/uv/getting-started/installation/) installed, run:

```sh
uvx chatify-app start --directory my-chat
```

The app opens in your browser. Your settings, documents and chats stay in `my-chat`. Press Ctrl+C to stop; run the same command from the same folder to return.

Without uv, use the [one-command installer for macOS, Linux or Windows](https://github.com/Harsh23Kashyap/chatify/blob/v0.1.27/docs/INSTALL.md). It installs what it needs without changing your system Python. For pip, install `chatify-app` in a virtual environment with Python 3.10 or newer. The package named `chatify` on PyPI is a different project.

## Configure

1. Open **Configuration**. In **Answers**, choose a provider, model and any required key, then test the connection and save.
2. Add your documents or web links. Choose which sources the chat should use.
3. In **Appearance**, choose a look and adjust the title, colors and fonts.

For help, type in **Find a setting** or open **Guide**. **Ask AI** asks your selected model about settings and may cost money.

**Build with AI** drafts a setup from your description. Choose a provider and model first, describe the app, then review, validate and save the draft. Restart to apply it. Generated code does not run automatically. Model requests may cost money.

![Build with AI describe step with an example prompt](https://raw.githubusercontent.com/Harsh23Kashyap/chatify/v0.1.27/docs/screenshots/build-with-ai.png)

Keep keys out of YAML and Git. Check sources for important answers; citations are not a guarantee of correctness.

[Install options](https://github.com/Harsh23Kashyap/chatify/blob/v0.1.27/docs/INSTALL.md) · [Configuration reference](https://github.com/Harsh23Kashyap/chatify/blob/v0.1.27/docs/DESIGN.md) · [Hosting](https://github.com/Harsh23Kashyap/chatify/blob/v0.1.27/docs/DEPLOY_OPTIONS.md)

MIT license. Harsh Kashyap and Shela Wu. Advisor: Dennis Shasha. Related project: [Custom-Nerd](https://github.com/Harsh23Kashyap/Custom-Nerd).

Fetch and start the latest release (uv installed):

```sh
uvx --refresh chatify-app start --directory my-chat
```

For pip: `python -m pip install --upgrade --no-cache-dir chatify-app`, then `python -m chatify start --directory my-chat`.
