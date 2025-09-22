from csp import CSP, alldiff

width = 9
box_width = 3


def build_csp_from_file(filename: str) -> CSP:
    grid = open(filename).read().split()

    domains = {}
    for row in range(width):
        for col in range(width):
            if grid[row][col] == '0':
                domains[f'X{row + 1}{col + 1}'] = set(range(1, 10))
            else:
                domains[f'X{row + 1}{col + 1}'] = {int(grid[row][col])}

    edges = []
    for row in range(width):
        edges += alldiff([f'X{row + 1}{col + 1}' for col in range(width)])
    for col in range(width):
        edges += alldiff([f'X{row + 1}{col + 1}' for row in range(width)])
    for box_row in range(box_width):
        for box_col in range(box_width):
            edges += alldiff([
                f'X{row + 1}{col + 1}'
                for row in range(box_row * box_width, (box_row + 1) * box_width)
                for col in range(box_col * box_width, (box_col + 1) * box_width)
            ])

    variables = [f'X{row + 1}{col + 1}' for row in range(width) for col in range(width)]
    return CSP(variables, domains, edges)


def print_solution(solution: dict[str, int]):
    for row in range(width):
        for col in range(width):
            print(solution[f'X{row + 1}{col + 1}'], end=" ")
            if col == 2 or col == 5:
                print('|', end=" ")
        print("")
        if row == 2 or row == 5:
            print('------+-------+------')


def format_domains(domains: dict[str, set]) -> str:
    out = []
    for row in range(width):
        row_cells = []
        for col in range(width):
            var = f'X{row + 1}{col + 1}'
            d = domains[var]
            row_cells.append(f"{var}:{d}")
        out.append(" ".join(row_cells))
    return "\n".join(out)


def report(filename: str, label: str):
    print(f"\n{label}:\n")
    csp = build_csp_from_file(filename)

    # Run AC-3
    ac3_ok = csp.ac_3()

    if not ac3_ok:
        print("Inconsistent puzzle!")
        return

    # Backtracking
    solution = csp.backtracking_search()

    # (a) Solution
    print("Solution:")
    if solution:
        print_solution(solution)
    else:
        print("No solution found.")

    # (b) Domains
    print("\nDomains after AC-3:")
    print(format_domains(csp.domains_after_ac3))

    # (c) Backtracking stats
    print("\nBacktracking stats:")
    print(f"\tCalls: {csp.bt_calls}")
    print(f"\tFailures: {csp.bt_failures}")

    # (d) Runtime of backtracking
    print("\nBacktracking runtime:")
    print(f"\t{csp.bt_runtime:.6f} seconds")

    # (e) Total runtime
    total_runtime = csp.ac3_runtime + csp.bt_runtime
    print("\nTotal runtime:")
    print(f"\t{total_runtime:.6f} seconds")


if __name__ == "__main__":
    files = [
        ("sudoku_easy.txt", "Sudoku Easy"),
        ("sudoku_medium.txt", "Sudoku Medium"),
        ("sudoku_hard.txt", "Sudoku Hard"),
        ("sudoku_very_hard.txt", "Sudoku Very Hard"),
    ]
    for filename, label in files:
        report(filename, label)
