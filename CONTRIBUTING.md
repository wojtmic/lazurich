# Contribution guide

## When to contribute?
Since Lazurich supports extensions, sometimes you don't need to modify the core. Only open a PR when you want to fix a bug, improve the UX/UI, optimize something or add/improve a universal feature.

## Guidelines
While all contribution is respected, there are guidelines.
1. Keep the tech stack (from [README](https://linktoread.me)), don't add dependencies unless absolutely necessary
2. Ensure that launcher's core is kept fully unopinionated
3. Respect the user, their time and what they want
4. Each **core** feature must have unit tests, if these are possible to implement
5. Apply DRY in your code and reuse existing components if possible
6. Use type hints in function arguments - return types aren't required
7. Transfer data around via dataclasses
8. Only store data in `STORAGE_ROOT`'s subdirs
9. All core code that executes in runtime (not on startup/shutdown) must be async
10. Include comments on confusing parts
11. Keep code readable and maintainable by other people
12. Be nice to maintainers and other contributors - we're all unpaid volunteers, just like you
13. No monoliths are allowed - code should be modular and no file should exceed 100 lines (optimally 30-80)
14. For large changes (architectural, GUI changes or multifile rewrites) **open an issue first** - do not waste your time writing a massive PR that won't be accepted
15. Use custom exceptions that are handled by the GUI - all internal exceptions (like httpx errors) MUST be translated to a handled Lazurich exception first
16. High-impact, automated or non-"instant" actions must be logged

## AI?
AI assistance is allowed to a limited degree. As long as the code is **not entirely generated**, and you can understand it, it should be fine. If your code looks too AI, you might be questioned on how your code works before a merge.<br>
**Sloppy, spammy PRs will not be accepted!**
