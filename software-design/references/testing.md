# Test Strategy

What to test, at which level, and what a green suite actually proves.

Tests are scope. They cost writing, running, and reading, and they are maintained for as long as the code lives. So the question is never "is this tested" but "which guarantees are pinned, and by what".

## Decide the strategy from the shape

- **Classify each dependency first.** In-process, local-substitutable, remote-but-owned, or true external. The category names what to substitute and what it costs (`modules.md`). The last two each add a port and two adapters, which is real work that belongs in the plan rather than the margin.
- **If the only way to test it is mocking everything, the shape is wrong.** This is a verdict on the design, not a test-writing problem, and it is cheapest to act on while the shape is still open.
- **Which level catches what.** Unit for logic and shape, integration for the wiring and the real collaborators, end-to-end for the path a user or consumer actually takes. Say where each lives and what surface it exercises.
- **The interface is the test surface.** Tests attach where callers attach and assert observable outcomes. A test that has to reach past the interface is evidence about the module, not a reason to widen it.

## One test per guarantee, not one per function

- Pin the load-bearing guarantees and the cases the design itself says are hard. Do not enumerate one test for every branch a reader can already see. A test suite carrying more than the change is worth gets quietly trimmed by whoever is tired, which is not a decision anyone made.
- **Name the guarantee, then name the test that would fail if it regressed.** For each invariant the design leans on ("the validator rejects stale keys before projection runs", "this fires on every failure path"), the test has to exercise the real collaborator rather than a mock of the thing under contract, and assert the invariant itself rather than an incidental proxy.
- **The bar is deletion.** If removing the guarantee from the implementation leaves the suite green, it was never pinned.
- **A bug fix opens with the test that reproduces it.** New behaviour gets its test written before the code that satisfies it. Deviate where the behaviour genuinely cannot be stated until something is built, and say that is what you are doing.

## Cases, not intentions

"Cover the validator" is an intention. A case is a name, the input that drives it, and the observable outcome asserted, which is enough that someone else could write it and get the test you meant. Stopping at the intention leaves the test to be invented alongside the code, which is how a test ends up shaped to whatever got built instead of to the behaviour that was agreed.

**Some guarantees are properties, not cases.** A parser, a smart constructor, a state machine, a serialization round trip, a normalization that must be idempotent: enumerating examples samples the space badly and a property covers it. Parse then render returns the input. Normalizing twice equals normalizing once. No legal sequence of transitions reaches an invalid state. Name the property the way you would name a case; the framework that runs it is a build-time detail.

When a fix exists specifically to handle a tricky input (multi-line content, an empty list, a boundary value), there has to be a test feeding *that* input. Otherwise the next person who simplifies the fix away passes CI.

## Why a passing test can be worthless

A test that passes proves nothing if it would *keep* passing after the guarantee it claims to protect is broken. Four recurring ways that happens:

- **It mocks the thing under contract.** If the load-bearing behaviour is "the validator rejects stale keys before projection runs", a test that patches out the validator exercises the mock. Mock the boundaries *around* the unit, not the unit's own contract.
- **It asserts an incidental proxy instead of the invariant.** Comparing a set when *order* is the property that matters, asserting a label that is coincidental to the behaviour, pinning a count without pinning what was counted. Assert the thing that would actually be wrong if the code were wrong.
- **It fakes an external contract with the code's own assumption of it.** A stub authored from the shape the code assumes means the test and the code share one guess, so they agree by construction. A wrong assumption about the real contract then passes every test while production silently gets nothing. Pin boundary shape against a captured real sample or a contract test.
- **It pins the function and not the wiring.** A test that passes the load-bearing value in as a parameter leaves the expression at the call site unpinned, and mutating that expression often leaves the whole suite green. This is common when mocks make the call-site value invisible. Find the single expression the behaviour rests on and drive the call site.

**Check the assertion's direction.** A containment or subset assertion ("every mirrored key exists upstream") stays true as the source of truth *grows*, so it cannot catch the drift that actually happens: someone adds a member upstream and stops. Invert it. Enumerate the source, keep an explicit allowlist of deliberate exclusions, and require every other member to be accounted for. Then a new member fails until someone classifies it.

**Prove it by mutation when reading leaves it open.** Reading a test tells you what it asserts, not what it would catch. Most of the time reading settles it. Mutate the ones it cannot: delete or invert the one line the guarantee rests on, run the narrowest selection that covers it, and require a failing test. A green run there is the finding. Grep for other tests touching the symbol before calling it unpinned, since a narrow selection can miss the one that pins it, and restore the file afterwards.

## Which tests a change retires

When a refactor deepens a module, the tests that pinned the old pieces one by one become waste as soon as tests exist at the new interface. They pin the implementation the change just decided to hide, so they break on the next internal edit and get "fixed" by rewriting them.

Replace, do not layer. Tests at the new interface retire the old per-piece ones, and their deletion is part of the change. The reverse case is a finding too: a new interface with no tests of its own, resting entirely on the old ones.

## A guardrail counts only once it runs

A test that exists but executes in no pipeline protects a laptop, not the mainline. When the safety story leans on a drift test, a contract test, or a lint rule, confirm that its package is in the CI project set and reachable from the configured test paths.

The suite also has to be green *reproducibly*: a check that depends on terminal width, colour, locale, wall-clock time, or an ambient environment variable gets disabled rather than fixed.

## Testing code that has none

Before changing untested code, pin the current behaviour first, bugs included. A characterization test records what the code does now so the refactor has something to be judged against; it is not an endorsement of that behaviour. Where the same change lands at several sites, every site needs cover, not just the first one found.
