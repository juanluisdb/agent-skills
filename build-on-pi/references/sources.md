# Sources And Caveats

Use this reference when you need to decide how much to trust a Pi claim.

## Source Hierarchy

- First-party product/docs
  `pi.dev`, official docs, API reference, official examples.
- First-party implementation
  `pi-mono` source code and packages.
- First-party integrations
  OpenClaw Pi integration docs are strong evidence for serious embedding patterns.
- Community and ecosystem material
  Blog posts, gists, examples, and shared extensions.
- Interpretive secondary sources
  `pi-book` and other architecture writeups.

## Practical Trust Rules

- For current API shape, prefer official docs and source over essays.
- For architecture and design intent, `pi-book` is useful but should be treated as interpretation tied to `pi-mono v0.66.0`.
- For philosophy and usage patterns, community material can be highly valuable, but it is not a compatibility promise.
- When an ecosystem example conflicts with first-party docs or code, follow the more primary source.

## Resources Gathered For This Skill

- `https://pi.dev/`
- official Pi SDK and extension API docs
- OpenClaw Pi integration docs
- community tutorial gist by Nader Dabit
- Armin Ronacher's Pi write-up
- `/Users/user/Downloads/pi_deep_brief.md`
- `/Users/user/code/pi-book/`

## Caveats Worth Preserving

- Pi's anti-MCP, anti-subagent, anti-plan-mode stance is philosophy, not a claim that those workflows cannot exist.
- Some extension and UI surfaces are still evolving.
- The best implementation details often require reading source after using the docs as a map.
