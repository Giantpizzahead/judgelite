Mary has been quite busy lately; her $N$ day schedule is packed with different business meetings. Mary has a pretty good sense of fashion, so she always wears business clothes to business meetings, and she wears casual clothes on other days.

Whenever Mary wears a piece of clothing, it becomes dirty, meaning that it cannot be worn again until Mary washes her clothes. Mary washes all of her used clothes at once, so it only takes one wash to clean all the dirty clothes that Mary currently has. At the end of each day (after wearing the clothing required for that day), she can choose whether or not to wash her clothes.

Budgeting is a huge issue for Mary, so she refuses to buy any new clothing apart from the $B$ business clothes and $C$ casual clothes she already has. Mary knows that this decision will probably result in her having to wash her clothes really often... but she'd like to know for sure.

Help Mary determine the **minimum # of times she has to wash her clothes** in order to wear the correct type of clothing for all of the $N$ days in her schedule (if she acts optimally).

#### INPUT FORMAT

The first line contains three integers $N$, $B$, and $C$, representing the number of days in Mary's schedule, the number of business clothes Mary has, and the number of casual clothes Mary has (respectively).
The next line contains $N$ space-separated integers, where the $i$th integer represents the style of clothing required for day $i$ (**0 for business clothes, 1 for casual clothes**).

#### OUTPUT FORMAT

A single integer: The minimum # of times Mary has to wash her clothes if she acts optimally.

#### CONSTRAINTS

$1 \leq N \leq 5{,}000$
$1 \leq B, C \leq N$

#### SAMPLE INPUT
```text
9 1 2
1 0 1 0 0 1 0 1 1
```

#### SAMPLE OUTPUT
```text
3
```

#### EXPLANATION

There are $9$ days in Mary's schedule. She has $1$ set of business clothes, and $2$ sets of casual clothes. The below sequence shows one way for Mary to wear the correct type of clothing every day, while only washing her clothes $3$ times (the minimal amount for the sample input).

Day 1 end: $1$ business, $1$ casual
Day 2 end: $0$ business, $1$ casual
Day 3 end: $0$ business, $0$ casual
--- Wash clothes before next day ---
Day 4 end: $0$ business, $2$ casual
--- Wash clothes before next day ---
Day 5 end: $0$ business, $2$ casual
Day 6 end: $0$ business, $1$ casual
--- Wash clothes before next day ---
Day 7 end: $0$ business, $2$ casual
Day 8 end: $0$ business, $1$ casual
Day 9 end: $0$ business, $0$ casual

Note that Mary does *not* need to wash her clothes at the end of day 9.