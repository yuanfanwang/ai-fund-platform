# Lessons

- When asuma asks for English, keep both test prompts and all assistant replies in English unless they explicitly switch languages again.
- When the user corrects skill naming, propagate the exact public names and prefixes through directories, frontmatter, and docs before implementation continues.
- When a demo skill must be reliable in Codex, bind each public command to a bundled script and return stdout verbatim instead of relying on SKILL.md prose alone.
