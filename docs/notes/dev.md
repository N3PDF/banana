# Refactoring

## Plan

We'd like to have the following runners:

- sandbox: make trials, a playground
- benchmarks: compare with external programs, on meaningful observables
- regression: compare with ourselves
  - here we can test not only the meaningful observables
  - indeed we will test the atomic elements, to check that behavior it's
    consistent in later versions, and flag otherwise

The same workflow however it's underlying:

1. run current `yadism`/`eko` version
2. collect "the other" (tabulated numbers, external program, former versions)
3. compare

- raise/collect errors (pytest-like)
- dump the comparison

Other tools:

- dev-tools: pdf generation, toyLH (maybe more)
- navigator
- (visualization)

## Runners

**Q:** Collect by external or collect by feature?

### Using Databases for comparison

Comparing across features it's not so useful, instead it would be useful
to compare the same feature across different external, so maybe it's better to
split by feature.

## Databases

**Q:** Do we need input databases?

- _sandbox_ it's very comfortable, and it's generating on the fly
- generating _theory_ on the fly it's easy: the domain it's well-known
- but what about the output-db?
  - without an input-db we need to rely on hashing theory/observable
  - but an hash does not retain the full-info about the input
  - then we can not query the results on their input, nor lookup to which
    specific

Moreover: there is a complicate business of benchmark exceptions going on, that
would be removed by on-the-fly o-card generation.

### Parallelization

We would like to achieve thread safety, to run benchmarks in parallel.
The only clash it's at writing the results, and so the way databases is handling
the insertion.

Top-level parallelization it's enough in our case, not that fast but all our
benchmarks are essentially taking the same time, because limited by the APFEL
pre-computation.

## DB interface
