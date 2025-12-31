# Visual Testing

Documents the Playwright screenshot-based test process for verifying each degree of freedom independently and confirming deterministic replay.

This document has no unique requirements. All testable behaviors verified by visual tests are already specified in other requirement documents:

- Demo form visibility, centering, styling, and stationarity: see `demo-form.md`
- Transform isolation (each axis produces only its expected motion): implied by `animated-background-component.md` ($REQ_ABC_012 transform mapping) and `element-attributes.md` ($REQ_ATTR_012 zero range means stationary)
- Position changes over time: implied by `animation-system.md` (velocity mechanics)
- Deterministic replay: see `deterministic-replay.md` ($REQ_REPLAY_008)
- Boost decay, effect, reversal, and combined velocity: implied by `boost-velocity.md`
- Mouse pan and rotation boost: implied by `mouse-interaction.md`
