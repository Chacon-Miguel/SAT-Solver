#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
import typing
import doctest
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS
file = open('dd.txt', 'w')


def simplify_formula(formula, var, assignment):
    # unit_clause = None
    new_formula = []
    for clause in formula:
        new_clause = []
        for variable, value in clause:
            # if clause has the variable that has just been assigned...
            if variable == var:
                if value == assignment:
                    new_clause = []
                    break
            else:
                new_clause.append((variable, value))
        if len(new_clause) == 0 and value != assignment:
            return None
        elif len(new_clause) > 0:
            # if len(new_clause) == 1:
            #     unit_clause = new_clause
            new_formula.append(new_clause)
    
    # if unit_clause != None:
    #     # print(unit_clause, variables)
    #     # print()
    #     variables.remove(unit_clause[0][0])
    #     assignments[ unit_clause[0][0] ] = unit_clause[0][1]
    #     new_formula = simplify_formula(new_formula, variables, assignments, unit_clause[0][0], unit_clause[0][1])
    #     file.write(str(new_formula))
    #     file.write(str(variables))
    #     # file.write(str(assignments))
    #     file.write('\n')
    #     if new_formula == None:
    #         variables.add( unit_clause[0][0] )
    #         del assignments[ unit_clause[0][0] ]
    return new_formula

def check_unit_clause(formula):
    for clause in formula:
        if len(clause) == 1:
            pass

    return formula

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
    variables = {literal[0] for clause in formula for literal in clause}
    vals = (True, False)
    assignments = {}

    def helper(formula):
        if len(variables) == 0:
            return assignments
        
        var = variables.pop()
        for val in vals:
            assignments[var] = val
            new_formula = simplify_formula(formula, var, val)

            if new_formula is None:
                continue

            new_assignments = helper(new_formula)
            if new_assignments is not None:
                assignments.update(new_assignments)
                return assignments
        variables.add(var)
        del assignments[var]
        return None
    return helper(formula)


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
    # import doctest
    # _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    # doctest.testmod(optionflags=_doctest_flags)
    # formula = [[('d', True), ('b', True)],
    #            [('a', True), ('b', True)],
    #            [('a', False), ('b', False), ('c', True)],
    #            [('b', True), ('c', True)],
    #            [('b', True), ('c', False)],
    #            [('a', False), ('b', False), ('c', False)]]
    cnf = [
        [('a', True), ('a', False)],
        [('b', True), ('a', True)],
        [('b', True)],
        [('b', False), ('b', False), ('a', False)],
        [('c', True), ('d', True)],
        [('c', True), ('d', True)]
    ]
    print(satisfying_assignment(cnf))
