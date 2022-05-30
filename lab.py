#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
import typing
import doctest
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

def parse_formula(formula):
    """
    Takes in a 3-D list that represents the CNF formula and creates
    a new representation of the formula as a 2-D dictionary. Every 
    clause is an internal dictionary where the keys are the variables of
    the clause and the values are the booleans of each variable. 
    
    Example of new formula: {
        {
            a: True,
            b: True,
            c: False
        }, {
            a: False
        }
    }

    The function then returns 4 other dictionaries:
    1. indices: when the function is iterating through the clauses, if it runs
        into a variable it hasn't seen yet, it adds it to this dictionary
        where the key is the variable and the value is the index of the variable.
        So if the variable A was seen first, then it has index = 0, and if B was next,
        then it has index = 1 and so forth.
        Example: indices = {C:2, D:3}
    2. assignments: keeps track of what each variable is assigned. The key is the index
        of the variable and the value is the boolean assigned. So if variable A has index 1,
        B has index 2, and C has index 3, and we assign True, False, True to these variables 
        respectively, then we have the following dictionary:
        {1:True, 2:False, 3:True}
    3. states: keeps track of what each variable has been assigned. The keys are the indices
        of each variable and the values can be either 0, 1, or 2. All variables initially start
        with no assignment so all values in states dict is 0. But say we assign variable A the 
        value True. Then we update its state to 1 since one value has been tried. Then say we
        find that we have to backtrack and we end up coming back to A. Then we assign False to A
        and update its state by 2 since True and False have been tried. 
        Example: {1: 1, 2: 2, 3: 1}
    4. variables: it is just the inverse of indices, so the keys are the variables and the values
        are the indices of the variables. 
    Returns the dictionaries in the order described and the new formula representation comes before
    all described dictionaries
    """
    # new formula
    n_formula = {}
    indices = {}
    n = 0

    # for every clause...
    for clause in formula:
        # for every literal...
        for literal in clause:
            # if variable has not been seen...
            if literal[0] not in indices:
                # add it to indices dictionary
                indices[literal[0]] = len(indices)
    # now that all variables have been given an index, initialize
    # assignments and state dictionary
    assignments = {i:None for i in range(len(indices))}    
    state = {i:0 for i in range(len(indices))}

    # for every clause...
    for clause in formula:
        # dictionary that holds new clause representation
        n_clause = {}
        for literal in clause:
            # for irrelevancies: if the current variables has not been seen...
            if literal[0] not in n_clause:
                # add it to the new clause representation
                n_clause[literal[0]] = literal[1]
            # if the literal has been seen and can be either True or False,
            # then its value does not affect clause so delete it
            elif literal[1] != n_clause[literal[0]]:
                del n_clause[literal[0]]
        # if the new clause is not empty, add it to the new formula representation
        if n_clause != {}:
            n_formula[n] = n_clause
        # keep track of how many clauses we've seen
        n += 1

    return n_formula, assignments, state, indices, {val:key for key, val in indices.items()}

def get_copy(formula):
    """
    Returns copy of given cnf formula that's represented by a 2-D dictionary
    """
    return {key:{k:v for k,v in value.items()} for key,value in formula.items()}

def simplify_formula(formula, var, assignment):
    """
    Given a variable and an assignment for it, it simplifies the given formula by
    iterating through all of its clauses and either removing it from the clause if
    it no longer affects the end result or deletes the clause if the literal satisfies
    the clause.
    Example:
        Say we had this formula: {
            {A: False, B: False, C:True},
            {A: True, D: True}
        }
        And we assign A the boolean True. Then it will no longer affect the first clause
        so we delete A from it, and we delete the second clause since it's been satisfied by
        the assignment. Thus, the formula is simplified to the following:
        {
            {B: False, C:True}
        }
    """
    # get copy of current formula
    n_formula = get_copy(formula)
    keys = list(n_formula.keys())
    
    # for every clause...
    for key in keys:
        clause = n_formula[key]
        # check if the variable given is in the clause
        if var in clause:
            # if assignment satisfies clause, delete the clause
            if clause[var] == assignment:
                del n_formula[key]
            # otherwise, delete the literal from the clause
            else:
                del clause[var]
        
        # Check if clause has length 0. That means contradiction has been reached,
        # so return None
        if len(clause) == 0:
            return None
    
    return n_formula

def switch_keys(assignment, state, variables, indices, assigned, index):
    """
    Given all dictionaries needed for the formula representation and two indices (i.e. assigned and index),
    the function switches the values for the two indices in every dictionary given. This is needed to keep 
    the assignment of the solver in order. 
    MUTATES THE DICTIONARIES. DOES NOT RETURN COPIES OF THEM!
    """
    # reassign values for assignment dictionary
    assignment[assigned], assignment[index] = assignment[index], assignment[assigned]
    # do the same for the rest of the dictionaries
    state[assigned], state[index] = state[index], state[assigned]

    indices[ variables[assigned] ], indices[ variables[index] ] = indices[ variables[index] ], indices[ variables[assigned] ]

    variables[assigned], variables[index] = variables[index], variables[assigned]

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    # get new formula representation and other dictionaries
    formula, assignment, state, indices, variables = parse_formula(formula)
    # dictionary that will keep track of all formulas generated, in case
    # we need to backtrack to a previous formula
    formulas = {0:formula}
    # c_formula => current formula, and initially, it's the original formula
    c_formula = formula
    # keeps track of the number of variables assigned
    assigned = 0
    
    # while all variables have not been assigned yet...
    while assigned != len(assignment):
        # find unit clauses and propogate their effects
        # unit_cs => unit clauses. Keeps track of how many we've found
        unit_cs = 0
        # n_formula => new formula. Make copy of the current formula
        n_formula = get_copy(c_formula)
        # keep track of whether we reached a contradiction when assigning
        # unit clauses and we need to backtrack
        deadend = False
        # while there are still unit clauses to assign...
        while True:
            # for every clause...
            for k in n_formula.keys():
                clause = n_formula[k]
                # if it's length is one...
                if len(clause) == 1:
                    # get the variable from dictionary
                    var = list(clause.keys())[0]
                    # get the variable's index
                    index = indices[var]
                    # switch the variables index with the assigned variable. Keeps how we assign
                    # the variables in order
                    switch_keys(assignment, state, variables, indices, assigned, index)
                    # since it's a unit clause, then we know that this variables value must be
                    # what the clause has because otherwise the clause isn't satisfied and
                    # the current assignment does not work
                    assignment[assigned] = clause[ variables[assigned] ]
                    # update the variables state
                    state[assigned] = 1
                    # now that we have assigned a value to the variable, simplify the current formula
                    n_formula = simplify_formula(n_formula, variables[assigned], clause[variables[assigned]])
                    # if a contradiction was not reached...
                    if n_formula != None:
                        # make the current formula the new one we just got by simplifying
                        c_formula = n_formula
                        # update the number of unit clauses we found
                        unit_cs += 1
                        # update the number of assigned variables we have
                        assigned += 1
                        # save the formula we just found
                        formulas[assigned] = n_formula
                    else:
                        # if a contradiction was reached, then the current assignment does not work,
                        # so make deadend True
                        deadend = True
                    # get out of the for loop
                    break
            # if no unit clauses are in the current formula, then get out of the while loop
            else:
                break
            # if we reached a deadend, then we need to backtrack
            if deadend:
                if assigned == 0:
                    # can't backtrack further. No solutions.
                    return None
                else:
                    # backtrack. Reset all values of the current variable we tried assignning
                    # something to
                    state[assigned] = 0
                    assignment[assigned] = None
                    # subtract the number of unit clauses we found
                    # from assigned to backtrack
                    assigned -= unit_cs 
                    # go back to the formula that does not end in a contradiction
                    c_formula = get_copy( formulas[assigned])
                    break
        # if all variables managed to be assigned by unit clauses, then stop assigning
        if assigned == len(assignment): 
            break
        # if not unit clauses dictates the current variables value, then
        # try assigning something to current variable
        for setting in (False, True):
            # if both True and False have not been tried, then either assign a value
            # that has not been tried.
            if state[assigned] != 2 and assignment[assigned] != setting:
                # get new formula
                n_formula = simplify_formula(c_formula, variables[assigned], setting)
                # if formula works...
                if n_formula != None:
                    # assign the current variable to the chosen setting
                    assignment[assigned] = setting
                    # update variables state
                    state[assigned] += 1
                    # update number of variables assigned
                    assigned += 1
                    # make the current formula the new one we found
                    c_formula = n_formula
                    # go to next variable
                    break
                # if the chosen setting led to a contradiction, then try
                # the other setting, but update the variables state
                else:
                    state[assigned] += 1
        # if nothing worked, then backtrack
        else:
            if assigned == 0:
                # can't backtrack further. No solutions.
                return None
            else:
                # backtrack
                state[assigned] = 0
                assignment[assigned] = None
                assigned -= 1
                c_formula = get_copy( formulas[assigned])
        # save previous formula
        formulas[assigned] = c_formula

    # return dictionary with assignments
    return {variables[k]:v for k,v in assignment.items()}

def combinations(iterable, r):
    """
    Given an iterable and r that's the size of the combinations wanted,
    creates a generator that gives all combinations. Gotten from the 
    Python documentation for the itertools combinations function.
    """
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = list(range(r))
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)

def students_in_desired_sessions(student_preferences):
    """
    First rule for scheduling problem: make sure that each student
    is assigned to their preferred rooms.

    That can simply be represented as a clause where each room is set to True.

    Returns cnf representation of rule
    """
    # list that will keep track of all conditions for room pref's.
    output = []
    # for every student and their preferences...
    for student, rooms in student_preferences.items():
        output.append( [(student + "_" + room, True) for room in rooms] )

    return output

def assign_to_one_room_only(student_preferences, room_capacities):
    """
    Second rule for scheduling problem: make sure that each student
    is assigned to one room only.

    This can be represented by saying that for every possible pair of rooms,
    a student can only be in one of them, (i.e. only one variable can be True).
    That's the same as setting both of them to False.

    Returns cnf representation of rule
    """
    pairs = [combo for combo in combinations(room_capacities.keys(), 2)]

    # list that will keep track of all conditions
    output = []
    for student in student_preferences.keys():
        for pair in pairs:
            output.append( [(student+"_"+pair[0], False), (student+"_"+pair[1], False)] )
    return output

def no_oversubscribed_session(student_preferences, room_capacities):
    """
    Third rule for scheduling problem: make sure that no room is overbooked.

    This can be represented by saying that if a room can hold N students, than 
    with a group of N+1 students, there is at least one student who is not in the room.
    That implies that all students being there cannot be true, which is the same as setting
    all of them to False by Demorgan's Law. 

    Returns cnf representation of rule.
    """
    output = []
    # get all students
    students = list(student_preferences.keys())
    # for every room and its capacity...
    for room, cap in room_capacities.items():
        # get all possible groups of students that include one more student
        # than the capacity of the room. So if room can N students, group size
        # is N+1 
        groups = [combo for combo in combinations(students, cap+1)]
        # for every possible group of the room...
        for group in groups:
            # add the clause to the output, where each variable is set to False
            output.append([(student+"_"+room, False) for student in group])

    return output            

def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz room scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a list
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    rule1 = students_in_desired_sessions(student_preferences)
    rule2 = assign_to_one_room_only(student_preferences, room_capacities)
    rule3 = no_oversubscribed_session(student_preferences, room_capacities)

    return rule1 + rule2 + rule3


if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
