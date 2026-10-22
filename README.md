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

## Repeated children

For a symbol that can occur several times in an alternative (e.g. `cart: item*`):
- `$item` is the number of occurrences (an `int`, `0` if there are none);
- `@item` is the list of occurrences, usable in any Python expression, e.g. `sum([i.price for i in @item])`. All of them are evaluated first.
- `item[n].attr` refers to the n-th occurrence (counting from 1). A bare `item` or `item.attr` is the first one.

## Errors

- `lark_ag.ContextConditionError`: an input violates a `CC` (the message is the one given after `->`).
- `lark_ag.AGDefinitionError`: the attribute grammar itself is invalid (duplicate or unknown attributes, wrong direction, ...), raised when the AG is loaded. `lark_ag.CircularDependencyError` is a subclass of it.

Both derive from `Exception`. Any other exception comes from your own equation code or from the input not matching the grammar. Doctests that expect a CC failure must name the class: `lark_ag.errors.ContextConditionError: message`.

## Known limitations

- Rule aliases (`-> name`) are not supported. LarkAG names each alternative `rule_<index>` (e.g. `start_0`) and relies on that naming to attach semantics.
- Rule and token name prefixes (`_`, `?`, `!`) are not supported. Every alternative gets a `rule_<index>` alias, which Lark rejects on `_rule`, and which makes `?rule` collapsing ineffective; attributes also need each rule to keep its own tree node.
- `%import` of a name list does not accept per-name aliases (`%import common (INT -> NUM)`); use the single-import form.
- Attribute evaluation visits each node exactly once. Attribute grammars that need the same subtree to be visited more than once
  (e.g. synthesize a value up, pass it back down as inherited, then synthesize a result up again) are rejected with an error,
  even though they are valid, non-circular AGs in standard AG theory. This is a limitation of the evaluator, not of AGs.
- Circular attribute dependencies are reported with an error naming the rule, alternative and attributes involved.
- A child is only visited if an equation of its parent reads one of its attributes. The context conditions and translation rules of a child that is never referenced are not run. An AG that relies only on CCs (no synthesized result) must therefore still read some attribute of each child, as in `panel_nesting_cc.ag` and `config_settings_cc.ag`.
- A rule without any `ER`, `CC` or `TR` block cannot be followed by another rule or token definition (the parser reads the next name as part of the rule body). Give it a semantics block, or place it last.
- `$symbol` / `@symbol` include the node itself when the symbol is the rule's own symbol (e.g. `l: "x" l*`).
- Inherited attributes of repeated children (`item*`) can only be defined for a fixed occurrence (`item[1].pos = ...`); there is no way to define them for every occurrence. Use a recursive list rule to pass context along a list.
- Indexing a repeated child beyond the occurrences present (`item[2]` with one item, or `item[1]` with none) raises an `IndexError` naming the symbol and the missing occurrence. Use `$item` to check the count first.
