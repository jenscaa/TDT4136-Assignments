from typing import Any
from queue import Queue
from time import perf_counter


class CSP:
    def __init__(
            self,
            variables: list[str],
            domains: dict[str, set],
            edges: list[tuple[str, str]],
    ):
        """Constructs a CSP instance with the given variables, domains and edges.
        
        Parameters
        ----------
        variables : list[str]
            The variables for the CSP
        domains : dict[str, set]
            The domains of the variables
        edges : list[tuple[str, str]]
            Pairs of variables that must not be assigned the same value
        """
        self.variables = variables
        self.domains = domains

        # Binary constraints as a dictionary mapping variable pairs to a set of value pairs.
        #
        # To check if variable1=value1, variable2=value2 is in violation of a binary constraint:
        # if (
        #     (variable1, variable2) in self.binary_constraints and
        #     (value1, value2) not in self.binary_constraints[(variable1, variable2)]
        # ) or (
        #     (variable2, variable1) in self.binary_constraints and
        #     (value1, value2) not in self.binary_constraints[(variable2, variable1)]
        # ):
        #     Violates a binary constraint
        self.binary_constraints: dict[tuple[str, str], set] = {}
        for variable1, variable2 in edges:
            self.binary_constraints[(variable1, variable2)] = set()
            for value1 in self.domains[variable1]:
                for value2 in self.domains[variable2]:
                    if value1 != value2:
                        self.binary_constraints[(variable1, variable2)].add((value1, value2))
                        self.binary_constraints[(variable1, variable2)].add((value2, value1))

        # Instrumentation
        self.bt_calls = 0
        self.bt_failures = 0
        self.ac3_runtime = 0.0
        self.bt_runtime = 0.0
        self.domains_after_ac3 = None

    def _revise(self, xi, xj):
        """Remove values from Xi's domain that are inconsistent with Xj."""
        revised = False
        for x in set(self.domains[xi]):
            # Check for value in Xj domain that satisfies the constraint with x
            if not any((x, y) in self.binary_constraints.get((xi, xj), set()) for y in self.domains[xj]):
                # If no such value y exists, remove x from Xi domain
                self.domains[xi].remove(x)
                revised = True
        return revised

    def ac_3(self) -> bool:
        """Performs AC-3 on the CSP.
        Meant to be run prior to calling backtracking_search() to reduce the search for some problems.

        Returns
        -------
        bool
            False if a domain becomes empty, otherwise True
        """

        # Initialize ac_3 timer
        start_time = perf_counter()

        # Initialize queue with arcs
        queue = Queue()
        for xi in self.variables:
            for xj in self.variables:
                if (xi, xj) in self.binary_constraints:
                    queue.put((xi, xj))

        # Process until queue is empty.
        while not queue.empty():
            xi, xj = queue.get()
            if self._revise(xi, xj):
                if not self.domains[xi]:
                    return False
                # Add all neighbors of xi back into the queue, except xj
                for xk in self.variables:
                    if (xk, xi) in self.binary_constraints and xk != xj:
                        queue.put((xk, xi))

        self.domains_after_ac3 = {v: set(d) for v, d in self.domains.items()}

        end_time = perf_counter()
        self.ac3_runtime = end_time - start_time
        return True

    def _is_consistent(self, var, val, assignment: dict[str, Any]) -> bool:
        """Check if assigning val to var is consistent with current assignment"""
        for other_var, other_val in assignment.items():
            if (var, other_var) in self.binary_constraints:
                if (val, other_val) not in self.binary_constraints[(var, other_var)]:
                    return False
            if (other_var, var) in self.binary_constraints:
                if (other_val, val) not in self.binary_constraints[(other_var, var)]:
                    return False
        return True

    def _is_complete(self, assignment: dict[str, Any]):
        """Check if all variables are assigned"""
        return len(assignment) == len(self.variables)

    def _select_unassigned_variable(self, assignment: dict[str, Any]):
        """Select the next unassigned variable"""
        for var in self.variables:
            if var not in assignment:
                return var
        raise ValueError("No unassigned variable found")

    def backtracking_search(self):
        """Performs backtracking search on the CSP.

        Returns
        -------
        None | dict[str, Any]
            A solution if any exists, otherwise None
        """

        # Initialize backtracking timer
        start_time = perf_counter()

        def backtrack(assignment: dict[str, Any]):
            # Backtrack counter
            self.bt_calls += 1

            if self._is_complete(assignment):
                return assignment
            var = self._select_unassigned_variable(assignment)

            # Process each value in domain
            for val in self.domains[var]:
                if self._is_consistent(var, val, assignment):
                    assignment[var] = val
                    result = backtrack(assignment)
                    if result is not None:
                        return result
                    # delete assignment
                    del assignment[var]

            # Failure counter
            self.bt_failures += 1
            return None

        backtrack_result = backtrack({})

        end_time = perf_counter()
        self.bt_runtime = end_time - start_time
        return backtrack_result


def alldiff(variables: list[str]) -> list[tuple[str, str]]:
    """Returns a list of edges interconnecting all of the input variables
    
    Parameters
    ----------
    variables : list[str]
        The variables that all must be different

    Returns
    -------
    list[tuple[str, str]]
        List of edges in the form (a, b)
    """
    return [(variables[i], variables[j]) for i in range(len(variables) - 1) for j in range(i + 1, len(variables))]
