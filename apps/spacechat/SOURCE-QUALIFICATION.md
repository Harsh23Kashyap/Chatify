# Source qualification, 31 October 2026

Existing packaged reference snippets now retain their observed original Wikipedia URLs and fetch date (21 October 2026), rather than losing clickable attribution after retrieval.

Candidate expansion not activated:
- NASA Image and Video Library API was probed from its official documented endpoint. It returned real metadata, but common educational questions often matched logo/event captions, old plans or irrelevant descriptions. More records was not better evidence. No general science-answer quality claim.
- Live Wikipedia search added results for Artemis and Webb questions. Actual gpt-4o-mini Artemis output then mixed retrieved plans with a packaged snapshot that records Artemis II as completed. This date/status conflict is unresolved. The new live source was removed rather than claiming improved freshness or mission status.
- arXiv returned real astronomy abstracts, but Webb/early-galaxies retrieval included old Solar System plans unrelated to early galaxies. Not activated.

Actual model answers on the candidate expansion were checked. Webb answer had a support warning, and Artemis mission status conflicted across retrieved references. The source expansion is NOT qualified. Attribution repair is separate from answer-quality proof.

Sources:
- https://images.nasa.gov/docs/images.nasa.gov_api_docs.pdf
- https://en.wikipedia.org/wiki/Artemis_program
- https://en.wikipedia.org/wiki/James_Webb_Space_Telescope
