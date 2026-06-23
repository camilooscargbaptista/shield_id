# Datasheet — <dataset name> v<x>

## Composition
synthetic faces (<generators>) · cloned voices (<TTS>) · fabricated docs (<LLMs>) · legit control set.
**No real personal data (I2).** Fully synthetic.

## Generators & cross-generator split (I4/D8)
train: {A, B} · **held-out test: C** (never used in training).

## Demographic distribution (validated — rule 06)
| Segment | Count | % |

## Labeling
per sample: attack type · generation method · difficulty tier.

## Generation pipeline
reproducible script: `<path>` · seed: <n>.

## Intended use & limitations
benchmark for synthetic-identity detection · NOT for surveillance/political targeting (license).

## Licensing & ethics
permissive open-source · no real PII · documented construction.
