# LarkAG - Attribute Grammar Extension for Lark

LarkAG is an extension to the Lark Compiler Generator that adds support for Attribute Grammars, allowing users to define attributes and semantic operations within their context-free grammars. This tool aims to simplify the development of language processors by enhancing the capabilities of Lark, improving productivity, and reducing errors in grammar engineering.

## Features
Attribute Grammar Support: Define synthesized and inherited attributes directly in grammar files.
Semantic Rule Execution: Use evaluation, context conditions, and translation rules for complex language processing.
Python Code Generation: Automatically generate Python code for interpreting AGs.

## Installation

### Prerequisites:
Python 3.7+ is required to install LarkAG.
Lark 1.1.9 

Install LarkAG using pip:
```bash
pip install lark-ag
```

## Lexing directives

Whitespace is ignored by default (`%import common.WS` / `%ignore WS` are added automatically).
If the grammar declares its own `%ignore`, that default is not added, so import and ignore whitespace explicitly if still desired.
Directives must currently appear after the grammar rules. `%ignore`, `%import`, `%declare` and `%override` are supported and passed to Lark unchanged.

## Known limitations

- Rule aliases (`-> name`) are not supported. LarkAG names each alternative `rule_<index>` (e.g. `start_0`) and relies on that naming to attach semantics.
- `%import` of a name list does not accept per-name aliases (`%import common (INT -> NUM)`); use the single-import form.
- Attribute evaluation visits each node exactly once. Attribute grammars that need the same subtree to be visited more than once
  (e.g. synthesize a value up, pass it back down as inherited, then synthesize a result up again) are rejected with an error,
  even though they are valid, non-circular AGs in standard AG theory. This is a limitation of the evaluator, not of AGs.
- Circular attribute dependencies are reported with an error naming the rule, alternative and attributes involved.
- A child is only visited if an equation of its parent reads one of its attributes. The context conditions and translation rules of a child that is never referenced are not run.
