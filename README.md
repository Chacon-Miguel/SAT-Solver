# SAT Solver
 Simple SAT Solver that's then used to solve Scheduling Problem

## Introduction
From recreational mathematics to standardized tests, one popular problem genre is logic puzzles, where some space of possible choices is described using a list of rules. A solution to the puzzle is a choice (often the one unique choice) that obeys the rules. This lab should give you the tools to make short work of any of those puzzles, assuming you have your trusty Python interpreter.

Here's an example of the kind of logic puzzle we have in mind.

The 6.009 staff were pleased to learn that grateful alumni had donated cupcakes for last week's staff meeting. Unfortunately, the cupcakes were gone when the staff showed up for the meeting! Who ate the cupcakes?

1. The suspects are Mike, Saman, Charles, Jonathan, and Tim the Beaver.
2. Whichever suspect ate any of the cupcakes must have eaten all of them.
3. The cupcakes included exactly two of the flavors chocolate, vanilla, and pickles.
4. Saman only eats pickles-flavored cupcakes.
5. Years ago, Charles and Jonathan made a pact that, whenever either of them eats cupcakes, they must share with the other one.
6. Mike feels strongly about flavor fairness and will only eat cupcakes if he can include at least 3 different flavors.

Let's translate the problem into Boolean logic, where we have a set of variables, each of which takes the value True or False. We write the rules as conditions over these variables. Here is each rule as a Python expression over Boolean variables. We include one variable for the guilt of each suspect, plus one variable for each potential flavor of cupcake.

In reading these rules, note that Python _not_ binds more tightly than _or_, so that _not p or q_ is the same as _(not p) or q_. It's also fine not to follow every last detail, as this rule set is just presented as one example of a general idea!

You may also find that some of our encoding choices don't match what you would come up with, such that our choices lead to longer or less-comprehensible rules. We are actually intentionally forcing ourselves to adhere to a restricted format that we will explain shortly and that will ultimately make the job of solving these kinds of problems more straightforward.

```
rule1 = (saman or mike or charles or jonathan or tim)
# At least one of them must have committed the crime!  Here, one of these
# variables being True represents that person having committed the crime.


rule2 = ((not saman or not mike)
     and (not saman or not charles)
     and (not saman or not jonathan)
     and (not saman or not tim)
     and (not mike or not charles)
     and (not mike or not jonathan)
     and (not mike or not tim)
     and (not charles or not jonathan)
     and (not charles or not tim)
     and (not jonathan or not tim))
# At most one of the suspects is guilty.  In other words, for any pair of
# suspects, at least one must be NOT guilty (so that we cannot possibly find
# two or more people guilty).

# Together, rule2 and rule1 guarantee that exactly one suspect is guilty.


rule3 = ((not chocolate or not vanilla or not pickles)
     and (chocolate or vanilla)
     and (chocolate or pickles)
     and (vanilla or pickles))
# Here is our rule that the cupcakes included exactly two of the flavors.  Put
# another way: we can't have all flavors present; and, additionally, among
# any pair of flavors, at least one was present.


rule4 = ((not saman or pickles)
     and (not saman or not chocolate)
     and (not saman or not vanilla))
# If Saman is guilty, this will evaluate to True only if only pickles-flavored
# cupcakes were present.  If Saman is not guilty, this will always evaluate to
# True.  This is our way of encoding the fact that, if Saman is guilty, only
# pickles-flavored cupcakes must have been present.


rule5 = (not charles or jonathan) and (not jonathan or charles)
# If Charles ate cupcakes without sharing with Jonathan, the first case will fail
# to hold.  Likewise for Jonathan eating without sharing.  Since Charles and Jonathan
# only eat cupcakes together, this rule excludes the possibility that only one
# of them ate cupcakes.


rule6 = ((not mike or chocolate)
     and (not mike or vanilla)
     and (not mike or pickles))
# If Mike is the culprit and we left out a flavor, the corresponding case here
# will fail to hold.  So this rule encodes the restriction that Mike can only
# be guilty if all three types of cupcakes are present.


satisfied = rule1 and rule2 and rule3 and rule4 and rule5 and rule6
```

The piece of code above is a Python program that will tell us whether a given assignment is consistent with the rules we have laid out. For example, if we had set the following variables (representing the hypothesis that Saman was guilty and that only Pickles-flavored cupcakes were present):
```
saman = True
mike = False
charles = False
jonathan = False
tim = False

pickles = True
vanilla = False
chocolate = False
```

and then run the code, the `satisfied` variable would be set to `False` (since `rule3` would be `False`), indicating that this assignment did not satisfy the rules we had set out.

### Solving the Puzzle
While code like the above could be useful in certain situations, it doesn't help us solve the problem (it only helps us check a possible solution). In this lab, we'll look at the problem of Boolean Satisfiability: our goal will be, given a description of Boolean variables and constraints on them (like that given above), to find a set of assignments that satisfies all of the given constraints.

### Conjunctive Normal Form
In encoding the puzzle, we followed a very regular structure in our Boolean formulas, one important enough to have a common name: conjunctive normal form (CNF).

In this form, we say that a _literal_ is a variable or the `not` of a variable. Then a _clause_ is a multi-way `or` of literals, and a CNF _formula_ is a multi-way `and` of clauses.

It's okay if this representation does not feel completely natural. Some people find this form to be "backwards" from the way they would otherwise think about these constraints. However, forcing our constraints to be in this form can simplify the problem of implementing our solver, compared to other representations we could choose. We'll try in this writeup to help you with the pieces of the lab involving converting expressions to CNF.

### Python Representation
When we commit to representing problems in CNF, we can represent:
* a _variable_ as a Python string
* a _literal_ as a pair (a tuple), containing a variable and a Boolean value (`False` if `not` appears in this literal, `True` otherwise)
* a _clause_ as a list of literals
* a _formula_ as a list of clauses

For example, our puzzle from above can be encoded as follows:
```
rule1 = [[('saman', True), ('mike', True), ('charles', True),
          ('jonathan', True), ('tim', True)]]

rule2 = [[('saman', False), ('mike', False)],
         [('saman', False), ('charles', False)],
         [('saman', False), ('jonathan', False)],
         [('saman', False), ('tim', False)],
         [('mike', False), ('charles', False)],
         [('mike', False), ('jonathan', False)],
         [('mike', False), ('tim', False)],
         [('charles', False), ('jonathan', False)],
         [('charles', False), ('tim', False)],
         [('jonathan', False), ('tim', False)]]


rule3 = [[('chocolate', False), ('vanilla', False), ('pickles', False)],
         [('chocolate', True), ('vanilla', True)],
         [('chocolate', True), ('pickles', True)],
         [('vanilla', True), ('pickles', True)]]

rule4 = [[('saman', False), ('pickles', True)],
         [('saman', False), ('chocolate', False)],
         [('saman', False), ('vanilla', False)]]

rule5 = [[('charles', False), ('jonathan', True)],
         [('jonathan', False), ('charles', True)]]

rule6 = [[('mike', False), ('chocolate', True)],
         [('mike', False), ('vanilla', True)],
         [('mike', False), ('pickles', True)]]

rules = rule1 + rule2 + rule3 + rule4 + rule5 + rule6
```
When we have formulated things in this way, the list rules contains a formula that encodes all of the constraints we need to satisfy.

Now, consider this Boolean formula (which is **not** in CNF).
```
(a and b) or (c and not d)
```
This expression looks innocuous, but translating it into CNF is actually a nontrivial exercise! It turns out, though, that this expression does have a representation in CNF as:
```
(a or c) and (a or not d) and (b or c) and (b or not d)
```
or, in our representation, as:
```
[[('a', True), ('c', True)], [('a', True), ('d', False)], [('b', True), ('c', True)], [('b', True), ('d', False)]]
```
Notice that the above expression will be true if a and b are both true, or if c is true and d is false.

## SAT Solver
A classic tool that works on Boolean formulas is a **satisfiability solver** or SAT solver. Given a formula, either the solver finds Boolean variable values that make the formula true, or the solver indicates that no solution exists. In this lab, a SAT solver was written that can solve puzzles like ours, as in:
```
>>> print(satisfying_assignment(rules))
{'jonathan': False, 'charles': False, 'chocolate': False, 'mike': False,
 'saman': False, 'pickles': True, 'tim': True, 'vanilla': True}
```

The return value of `satisfying_assignment` is a dictionary mapping variables to the Boolean values that have been inferred for them (or `None` if no valid mapping exists).

So, we can see that, in our example above, Tim the Beaver is guilty and has a taste for vanilla and pickles!

It turns out that there are other possible answers that have Tim enjoying other flavors, but it also turns out that Tim is the uniquely determined culprit. How do we know? The SAT solver fails to find an assignment when we add an additional rule proclaiming Tim's innocence.

```
>>> print(satisfying_assignment(rules + [[('tim', False)]]))
None
```

### Approach
We start by picking an arbitrary variable _x_ from our formula _F_. We then construct a related formula $F_{1}$, which does not involve _x_ but incorporates all the consequences of setting _x_ to be True. We then try to solve $F_{1}$. If it produces a successful result, we can combine that result with information about _x_ being `True` to produce our answer to the original problem.

If we could not solve $F_{1}$, we should try setting xx to be False instead. If no solution exists in either of the above cases, then the formula $F$ cannot be satisfied.

A key operation here is updating a formula to model the effect of a variable assignment. As an example, consider this starting formula.
```
(a or b or not c) and (c or d)
```
If we learn `c = True`, then the formula should be updated as follows.

```
(a or b)
```

We removed `not c` from the first clause, because we now know conclusively that that literal is `False`. Conversely, we can remove the second clause, because with `c` true, it is assured that the clause will be satisfied.

Note a key effect of this operation: _variable_ `d` _has disappeared from the formula, so we no longer need to consider values for_ `d`.

In general, this approach often saves us from an exponential enumeration of variable values, because we learn that, in some branches of the search space, some variables are actually irrelevant to the problem.

This pruning will show up in the assignments that your SAT solver returns: you are allowed (but not required) to omit variables that turn out to be irrelevant.

If we had instead learned that `c` was `False`, we would update the formula instead as follows:
```
d
```
How did we get there? Note that, with `c` being `False`, the first clause is already satisfied. The second clause, though, will only be `True` if `d` is `True`.

## Further Optimizations
* In the procedure described above, if setting the value of xx immediately leads to a contradiction, we can immediately discard that possibility (rather than waiting for a later step in the recursive process to notice the contradiction).

* At the start of any call to your procedure, check if the formula contains any length-one clauses ("unit" clauses). If such a clause `[(x, b)]` exists, then we may set `x` to Boolean value `b`, just as we do in the `True` and `False` cases of the outline above. However, we know that, if this setting leads to failure, there is no need to backtrack and also try `x = not b` (because the unit clause alone tells us exactly what the value of `x` must be)!

Thus, you can begin your function with a loop that repeatedly finds unit clauses, if any, and propagates their consequences through the formula. Propagating the effects of one unit clause may reveal further unit clauses, whose later propagations may themselves reveal more unit clauses, and so on.

## Scheduling by Reduction
Now that we have a fancy new SAT solver, let's look at applying it to a new problem!

In general, it's possible to write a new implementation of backtracking search for each new problem we encounter, but another strategy is to _reduce_ a new problem to one that we already know how to solve well. Boolean satisfiability is a popular target for reductions, because a lot of effort has gone into building fast SAT solvers. In this last part of the lab, you will implement a reduction to SAT from a scheduling problem.

In particular, we are interested in the real-life problem of assigning students in a class to different rooms for taking a quiz. For 6.009's quiz, we assigned rooms based on last names; but we could have tried a different streategy instead, asking for room preferences.

In this scenario, each student prefers only some of the rooms, but each room has limited capacity. We want to find a schedule (assignment of students to rooms) that respects all the constraints.

The function `boolify_scheduling_problem(student_preferences, room_capacities)` as described both below and in `lab.py` was implemented:
* The argument `student_preferences` is a dictionary mapping a student name (string) to a list of room names (strings) for which that student is available.
* Argument `room_capacities` is a dictionary mapping each room name to a positive integer for how many students can fit in that room.
* The function returns a CNF formula encoding the schedule problem, as we explain next.

Here's an example call: 
```
boolify_scheduling_problem({'Alice': ['basement', 'penthouse'],
                            'Bob': ['kitchen'],
                            'Charles': ['basement', 'kitchen'],
                            'Dana': ['kitchen', 'penthouse', 'basement']},
                           {'basement': 1,
                            'kitchen': 2,
                            'penthouse': 4})
```

In English, Alice is available for the sessions in the basement and penthouse, Bob is available only for the session in the kitchen, etc. The basement can fit 1 student, the kitchen 2 students, and the penthouse 4 students. In this case, one legal schedule would be Alice in the basement, Bob in the kitchen, Charles in the kitchen, and Dana in the penthouse.

Your job is to translate such inputs into CNF formulas, such that your SAT solver can then find a legal schedule (or confirm that none exists).

The CNF formula you output should mention only Boolean variables named like `student_room`, where student is the name of a student, and where `room` is the name of a room. The variable `student_room` should be `True` if and only if that student is assigned to that room (for example, the variable `Bob_kitchen` should be `True` if Bob is in the kitchen and `False` otherwise).

The CNF clauses you include should enforce exactly the following rules (which are discussed in more detail below):

1. Students are only assigned to rooms included in their preferences.
2. Each student is assigned to exactly one room.
3. No room has more assigned students than it can fit.

### Implementing the Rules
#### Students Only In Desired Sessions
For each student, we need to guarantee that they are given a room that they selected as one of their preferences. In the example above, for example, we know that Charles must be in the basement or the kitchen, and that Alice must be in the basement or in the penthouse.

Here's the CNF formula expressing this constraint (students are only assigned to rooms in their preferences) for the example data above (with Alice, Bob, Charles, and Dana). We used variable names of the form described above (e.g., 'Bob_kitchen' represents Bob being in the kitchen).
```
[[('Alice_basement', True), ('Alice_penthouse', True)], [('Bob_kitchen', True)], [('Charles_basement', True), ('Charles_kitchen', True)], [('Dana_kitchen', True), ('Dana_penthouse', True), ('Dana_basement', True)]]
```
#### Each Student In Exactly One Session
This rule is a little bit trickier, but it may help to separate it into two pieces:
* each student must be in at least one room, **and**
* each student must be in at most one room.

We can generate formulae for each of these conditions and combine them to construct the overall formula corresponding to this rule.

In fact, the first bullet (that each student be assigned to at least one room) is redundant with our first condition (that each student be assigned to a room in their preferences).

So let's turn our attention to making sure that each student is assigned to _at most one room_. This one is a bit trickier, particularly since we need to put things in CNF. One flip of perspective that can be helpful is that, if we need each student to be in at most one room, that means that for any pair of rooms, any given student can be in only one of them.

For example, one clause in this expression will say that Bob cannot be in both the kitchen and the basement. That is, we cannot have both `Bob_kitchen` and `Bob_basement` be `True` (or, to phrase it a different way, at least one of them must be `False`).

Note that there is a corresponding clause for every other pair of rooms; and each of these clauses has a corresponding clause for Alice (and the other students)

#### No Oversubscribed Sessions
This last rule is also fairly tricky, and it maybe requires a bit of a shift of perspective to express this constraint in CNF. However, it is similar to the previous rule in some ways.

We can think about this as: if a given room can contain _N_ students, then in every possible group of $N+1$ students, there must be at least one student who is _not_ in the given room.

For example, since the kitchen holds 2 people, we would need to consider all possible groups of 3 students and make sure that at least one of the students in each group is _not_ in that room. 

What about the penthouse? It has enough room for everyone, so there is no need even to include it in the constraints (it doesn't constrain our decision in any way)!

All the rules are then combined to make the formula that can be passed onto our SAT Solver!

## UI
We have provided a browser UI for this lab, so you can see the code solving scheduling problems in action! Run python3 server.py and navigate to http://localhost:6009/. Running a test case on the UI involves generating a CNF formula and searching for a satisfying assignment for it, done by calling your functions. Enjoy!