# Decisions to be implemented

## Runners

### On-the-fly input

Generate input on-the-fly

- both theory + o-card

### By-feature

**REJECTED**

Split runners by feature

- if an external it's not available raise a warning "Not able to run -> so
  skip" but not a blocking error, to keep going with
- mark benchmarks by external, such that a single or a subset can be selected

## Parallelization

- implement bindings for thread safe database
