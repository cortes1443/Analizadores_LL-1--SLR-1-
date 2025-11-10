# ll1_parser.py
from collections import deque
from first_follow import compute_first_for_sequence

def build_ll1_table(grammar, first_sets, follow_sets):
    table = {nt: {} for nt in grammar.non_terminals}
    is_ll1 = True
    
    for A in grammar.non_terminals:
        for production in grammar.productions[A]:
            symbols = grammar._extract_symbols(production)
            first_alpha = compute_first_for_sequence(symbols, first_sets, grammar)
            
            # Rule 1: For each terminal in FIRST(α), add A -> α to table[A][a]
            for terminal in first_alpha:
                if terminal == grammar.epsilon:
                    continue
                
                if terminal in table[A]:
                    # Conflict detected - multiple productions for same terminal
                    is_ll1 = False
                table[A][terminal] = production
            
            # Rule 2: If ε in FIRST(α), add A -> α to table[A][b] for each b in FOLLOW(A)
            if grammar.epsilon in first_alpha:
                for terminal in follow_sets[A]:
                    if terminal in table[A]:
                        # Conflict detected
                        is_ll1 = False
                    table[A][terminal] = production
    
    return table, is_ll1

def parse_ll1(grammar, table, input_tokens):
    stack = deque([grammar.end_marker, grammar.start_symbol])
    input_tokens = input_tokens + [grammar.end_marker]
    input_index = 0
    
    while stack:
        top = stack.pop()
        current_token = input_tokens[input_index]
        
        if top == grammar.end_marker and current_token == grammar.end_marker:
            return True
        
        if top in grammar.terminals:
            if top == current_token:
                input_index += 1
            else:
                return False
        elif top in grammar.non_terminals:
            if current_token not in table[top]:
                return False
            
            production = table[top][current_token]
            if production == grammar.epsilon:
                continue
                
            # Push symbols in reverse order
            symbols = grammar._extract_symbols(production)
            for symbol in reversed(symbols):
                stack.append(symbol)
        else:
            return False
    
    return False