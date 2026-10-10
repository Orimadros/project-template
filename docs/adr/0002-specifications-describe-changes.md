# Specifications describe changes

A specification is a contract for a change to the repository and can cover several
scripts. Once the change is accepted, archive its specification unchanged. Later
changes receive new specifications. This preserves the reasons for each change
without creating a second description of each script's current behavior that can
drift from its code.

Each script explains its current purpose, inputs, outputs, substantive choices,
and their rationale in its own documentation and comments. The agent updates
that explanation with the code. Specifications are historical change records;
they are not maintained as external manuals for individual scripts.
