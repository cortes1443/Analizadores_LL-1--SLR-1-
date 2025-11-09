# main.py
class Grammar:
    def __init__(self):
        self.productions = {}  # {nonterminal: [list of productions]}
        self.non_terminals = set()
        self.terminals = set()
        self.start_symbol = 'S'  # Símbolo inicial
        self.epsilon = 'e'

    def add_production(self, nonterminal, alternatives):
        """Add productions for a nonterminal"""
        if nonterminal not in self.productions:
            self.productions[nonterminal] = []

        for alt in alternatives:
            # Reemplazar 'e' por epsilon si es necesario
            if alt.strip() == 'e':
                alt = self.epsilon
            self.productions[nonterminal].append(alt)

            # Extract terminals and non-terminals
            for symbol in alt.split():
                if symbol == self.epsilon:
                    continue
                if symbol.isupper():
                    self.non_terminals.add(symbol)
                else:
                    self.terminals.add(symbol)

        self.non_terminals.add(nonterminal)

    def get_all_symbols(self):
        """Get all grammar symbols (terminals and non-terminals)"""
        return self.terminals.union(self.non_terminals)


def compute_first(grammar):
    """
    Compute FIRST sets for all grammar symbols
    Returns: dict {symbol: set of terminals}
    """
    first = {}
    changed = True

    # Initialize FIRST sets
    for symbol in grammar.get_all_symbols():
        first[symbol] = set()
        if symbol in grammar.terminals and symbol != grammar.epsilon:
            first[symbol].add(symbol)

    # Add epsilon to FIRST of non-terminals that can derive epsilon
    for nt in grammar.non_terminals:
        first[nt] = set()
        if grammar.epsilon in grammar.productions.get(nt, []):
            first[nt].add(grammar.epsilon)

    # Iterate until no changes
    while changed:
        changed = False

        for nt in grammar.non_terminals:
            for production in grammar.productions.get(nt, []):
                symbols = production.split()

                # For each symbol in the production
                all_epsilon = True
                for symbol in symbols:
                    if symbol == grammar.epsilon:
                        continue

                    # Add FIRST(symbol) - {epsilon} to FIRST(nt)
                    for terminal in first.get(symbol, set()):
                        if terminal != grammar.epsilon and terminal not in first[nt]:
                            first[nt].add(terminal)
                            changed = True

                    # If epsilon not in FIRST(symbol), stop
                    if grammar.epsilon not in first.get(symbol, set()):
                        all_epsilon = False
                        break

                # If all symbols can derive epsilon, add epsilon to FIRST(nt)
                if all_epsilon and grammar.epsilon not in first[nt]:
                    first[nt].add(grammar.epsilon)
                    changed = True

    return first


def compute_first_for_sequence(sequence, first_sets, grammar):
    """
    Compute FIRST set for a sequence of symbols
    """
    result = set()
    symbols = sequence.split() if isinstance(sequence, str) else sequence

    # Si la secuencia está vacía o es epsilon
    if not symbols or symbols == [grammar.epsilon]:
        return {grammar.epsilon}

    all_epsilon = True
    for symbol in symbols:
        if symbol == grammar.epsilon:
            continue

        # Add FIRST(symbol) - {epsilon} to result
        for terminal in first_sets.get(symbol, set()):
            if terminal != grammar.epsilon:
                result.add(terminal)

        # If epsilon not in FIRST(symbol), stop
        if grammar.epsilon not in first_sets.get(symbol, set()):
            all_epsilon = False
            break

    # If all symbols can derive epsilon, add epsilon
    if all_epsilon:
        result.add(grammar.epsilon)

    return result


def compute_follow(grammar, first_sets):
    """
    Compute FOLLOW sets for non-terminals
    Returns: dict {nonterminal: set of terminals}
    """
    follow = {nt: set() for nt in grammar.non_terminals}

    # El símbolo inicial debe tener $ en FOLLOW
    follow[grammar.start_symbol].add('$')

    changed = True

    while changed:
        changed = False

        for nt in grammar.non_terminals:
            for production in grammar.productions.get(nt, []):
                symbols = production.split()

                for i, symbol in enumerate(symbols):
                    if symbol in grammar.non_terminals:
                        # For A -> αBβ
                        beta = symbols[i + 1:] if i + 1 < len(symbols) else []

                        if beta:
                            # Add FIRST(β) - {epsilon} to FOLLOW(B)
                            first_beta = compute_first_for_sequence(beta, first_sets, grammar)
                            for terminal in first_beta:
                                if terminal != grammar.epsilon and terminal not in follow[symbol]:
                                    follow[symbol].add(terminal)
                                    changed = True

                            # If epsilon in FIRST(β), add FOLLOW(A) to FOLLOW(B)
                            if grammar.epsilon in first_beta:
                                for terminal in follow[nt]:
                                    if terminal not in follow[symbol]:
                                        follow[symbol].add(terminal)
                                        changed = True
                        else:
                            # For A -> αB, add FOLLOW(A) to FOLLOW(B)
                            for terminal in follow[nt]:
                                if terminal not in follow[symbol]:
                                    follow[symbol].add(terminal)
                                    changed = True

    return follow


def read_grammar_from_input():
    """
    Read grammar from standard input
    """
    grammar = Grammar()

    print("Enter the number of nonterminals:")
    n = int(input().strip())

    print("Enter productions in format: A -> a B c | e")
    for i in range(n):
        line = input().strip()
        if '->' in line:
            lhs, rhs = line.split('->', 1)
            lhs = lhs.strip()
            alternatives = [alt.strip() for alt in rhs.split('|')]
            grammar.add_production(lhs, alternatives)

    return grammar


def print_sets(grammar, first_sets, follow_sets):
    """
    Print FIRST and FOLLOW sets in a readable format
    """
    print("\n" + "=" * 50)
    print("FIRST SETS:")
    print("=" * 50)
    for symbol in sorted(grammar.get_all_symbols()):
        if symbol in grammar.non_terminals:
            print(f"FIRST({symbol}) = {{{', '.join(sorted(first_sets[symbol]))}}}")

    print("\n" + "=" * 50)
    print("FOLLOW SETS:")
    print("=" * 50)
    for nt in sorted(grammar.non_terminals):
        print(f"FOLLOW({nt}) = {{{', '.join(sorted(follow_sets[nt]))}}}")


def main():
    """
    Main function to demonstrate FIRST and FOLLOW computation
    """
    print("FIRST AND FOLLOW SETS CALCULATOR")
    print("=" * 40)

    # Example grammar or read from input
    use_example = input("Use example grammar? (y/n): ").strip().lower()

    if use_example == 'y':
        # Example grammar con 6 no terminales
        grammar = Grammar()

        grammar.add_production('S', ["E"])
        grammar.add_production('E', ["T E'"])
        grammar.add_production("E'", ["+ T E'", "e"])
        grammar.add_production('T', ["F T'"])
        grammar.add_production("T'", ["* F T'", "e"])
        grammar.add_production('F', ["( E )", "id"])

        print("Using example grammar with 6 nonterminals: S, E, E', T, T', F")

    else:
        grammar = read_grammar_from_input()

    # Compute FIRST sets
    print("\nComputing FIRST sets...")
    first_sets = compute_first(grammar)

    # Compute FOLLOW sets
    print("Computing FOLLOW sets...")
    follow_sets = compute_follow(grammar, first_sets)

    # Print results
    print_sets(grammar, first_sets, follow_sets)


if __name__ == "__main__":
    main()