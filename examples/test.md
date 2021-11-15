
# A title slide

Hello there! This is a demo of my slide processor.

---

## Markdown should work

* This is a markdown sample
  * Still a bit sampling
* Very markdown

1. Mark
2. Down
3. ???
4. Profif

---

## Another slide

```python number highlight=3,5
def fact(x):
    if x == 0:
        return 1
    else:
        return fact(x - 1) * x
```

::: footer
    Note the numbering of the line files. Also note this note.

---

## Some math

An example paragraph $1$ with some $\sqrt{2}$ math.

Brought to you by the $\int^1_0 \frac{\sin x}{x} \,dx$ gang.

::: latex
    \int \sin(x^2) \,dx

::: latex
    \subparLatexSkills(x)

---

## A graph

::: dot
    digraph G {
        rankdir=LR;
        A -> {B C};
        {B C} -> D;
        C -> E;
    }

Some more text under the graph.

And even more text.

Just to demonstrate auto-fitting of the graph above. yes it is magical. no I have never heared of `object-fit` before and tried to implement it manualy. yes I like to hurt myself.