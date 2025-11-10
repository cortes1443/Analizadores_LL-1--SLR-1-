# first_follow.py
from collections import defaultdict

def compute_first(grammar):
    first = defaultdict(set)
    
    # Initialize FIRST for terminals
    for terminal in grammar.terminals:
        if terminal != grammar.epsilon:
            first[terminal].add(terminal)
    
    # Initialize FIRST for non-terminals
    for nt in grammar.non_terminals:
        # Check if non-terminal can derive epsilon directly
        for production in grammar.productions[nt]:
            if production == grammar.epsilon:
                first[nt].add(grammar.epsilon)
    
    changed = True
    while changed:
        changed = False
        
        for nt in grammar.non_terminals:
            for production in grammar.productions[nt]:
                symbols = grammar._extract_symbols(production)
                
                if not symbols:  # epsilon production
                    if grammar.epsilon not in first[nt]:
                        first[nt].add(grammar.epsilon)
                        changed = True
                    continue
                
                # For each symbol in the production
                all_epsilon = True
                for symbol in symbols:
                    # Add all non-epsilon symbols from FIRST(symbol)
                    for terminal in first[symbol]:
                        if terminal != grammar.epsilon and terminal not in first[nt]:
                            first[nt].add(terminal)
                            changed = True
                    
                    # If current symbol cannot derive epsilon, stop
                    if grammar.epsilon not in first[symbol]:
                        all_epsilon = False
                        break
                
                # If all symbols can derive epsilon, add epsilon to FIRST(nt)
                if all_epsilon and grammar.epsilon not in first[nt]:
                    first[nt].add(grammar.epsilon)
                    changed = True
    
    return dict(first)

def compute_first_for_sequence(sequence, first_sets, grammar):
    """Compute FIRST set for a sequence of symbols"""
    if not sequence:
        return {grammar.epsilon}
    
    result = set()
    all_epsilon = True
    
    for symbol in sequence:
        # Add all non-epsilon terminals from FIRST(symbol)
        for terminal in first_sets.get(symbol, set()):
            if terminal != grammar.epsilon:
                result.add(terminal)
        
        # If current symbol cannot derive epsilon, stop
        if grammar.epsilon not in first_sets.get(symbol, set()):
            all_epsilon = False
            break
    
    # If all symbols can derive epsilon, add epsilon
    if all_epsilon:
        result.add(grammar.epsilon)
    
    return result

def compute_follow(grammar, first_sets):
    follow = {nt: set() for nt in grammar.non_terminals}
    follow[grammar.start_symbol].add(grammar.end_marker)
    
    changed = True
    while changed:
        changed = False
        
        for nt in grammar.non_terminals:
            for production in grammar.productions[nt]:
                symbols = grammar._extract_symbols(production)
                
                for i, symbol in enumerate(symbols):
                    if symbol not in grammar.non_terminals:
                        continue
                    
                    # For A -> αBβ, add FIRST(β)-{ε} to FOLLOW(B)
                    beta = symbols[i+1:]
                    if beta:
                        first_beta = compute_first_for_sequence(beta, first_sets, grammar)
                        
                        for terminal in first_beta:
                            if terminal != grammar.epsilon and terminal not in follow[symbol]:
                                follow[symbol].add(terminal)
                                changed = True
                        
                        # If β can derive epsilon, add FOLLOW(A) to FOLLOW(B)
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