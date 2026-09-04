# Publish the decision layer as a portable Skill

**Ready to advance.** The idea was right in direction but too tied to one host. The stronger product is a versioned, self-contained Skill whose repository is the development and distribution source—not a runtime dependency.

## What changed

| | Initial idea | Matured decision |
|---|---|---|
| Product | A dedicated custom AI assistant | A host-neutral Agent Skill |
| Knowledge | Read the repository during normal use | Carry the cognitive core inside the installed version |
| Integrations | Name specific tools in the architecture | Request abstract capabilities and map them per host |
| Output | A good answer | Human Decision Brief + structured Decision Pack |

The core reason is portability. If the system needs one vendor, one connector or the latest `main` branch simply to know how to reason, behavior can drift without an explicit upgrade and other hosts become second-class citizens.

## What still matters

Host adapters can differ materially. A feature documented for one host is not automatically available on another surface, so runtime capability claims still need observable evidence.

## Next move

Ship one self-contained skill package, keep host wrappers thin, and run fresh v1.4 conformance before creating the stable release tag.
