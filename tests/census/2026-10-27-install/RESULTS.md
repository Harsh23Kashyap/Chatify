# Installed artifact checks, October27

Fresh isolated environments outside the checkout passed on Linux x86_64 Python3.10.12,3.11.17,3.12.15,3.13.17,3.14.9. Each installed the actual wheel plus resolved PyYAML dependency; ran CLI version, scaffold, validate, mock ask; started the installed HTTP server and fetched health, chat, settings, build, font and font-license routes. See JSON logs for exact commands and responses.

The earlier12967401-byte wheel omitted every font asset and license. Fixed package-data to include web/fonts/* and added metadata regression. Fresh wheel15031610bytes, SHA25654d4b3536ade9e0146dffd7e42facfcb9cbebe230a33c4d44de5ea18db44ff73. Actual ZIP inventory confirms all source font-directory files are included. The previous wheel/build remains historical evidence, not current artifact.

Scope limits: Linux only, base dependency only, no Windows/macOS, document/semantic extras, real provider, PyPI upload, or full runtime qualification claim. Prior1102-ID unit count predates this metadata-only fix; one additional targeted packaging unit passes separately. Runtime quiet-event coverage remains blocked.
