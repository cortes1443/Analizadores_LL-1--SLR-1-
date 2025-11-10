# slr_parser.py
from collections import defaultdict

class LR0Item:
    def __init__(self, lhs, rhs, dot_position=0):
        self.lhs = lhs
        self.rhs = tuple(rhs)  # Make immutable for hashing
        self.dot_position = dot_position
    
    def __eq__(self, other):
        return (self.lhs == other.lhs and 
                self.rhs == other.rhs and 
                self.dot_position == other.dot_position)
    
    def __hash__(self):
        return hash((self.lhs, self.rhs, self.dot_position))
    
    def __str__(self):
        rhs_list = list(self.rhs)
        rhs_list.insert(self.dot_position, '•')
        return f"{self.lhs} -> {' '.join(rhs_list)}"
    
    def next_symbol(self):
        if self.dot_position < len(self.rhs):
            return self.rhs[self.dot_position]
        return None
    
    def is_reduce_item(self):
        return self.dot_position == len(self.rhs)
    
    def advance(self):
        if not self.is_reduce_item():
            return LR0Item(self.lhs, self.rhs, self.dot_position + 1)
        return None

def closure(items, grammar):
    closure_set = set(items)
    changed = True
    
    while changed:
        changed = False
        
        for item in list(closure_set):
            next_sym = item.next_symbol()
            if next_sym in grammar.non_terminals:
                for production in grammar.productions[next_sym]:
                    rhs = [] if production == grammar.epsilon else grammar._extract_symbols(production)
                    new_item = LR0Item(next_sym, rhs, 0)
                    if new_item not in closure_set:
                        closure_set.add(new_item)
                        changed = True
    
    return frozenset(closure_set)

def goto(items, symbol, grammar):
    new_items = set()
    
    for item in items:
        if item.next_symbol() == symbol:
            new_item = item.advance()
            if new_item:
                new_items.add(new_item)
    
    return closure(new_items, grammar) if new_items else frozenset()

def build_canonical_collection(grammar):
    # Create augmented grammar
    start_aug = grammar.start_symbol + "'"
    while start_aug in grammar.non_terminals:
        start_aug += "'"
    
    # Build initial state
    initial_item = LR0Item(start_aug, [grammar.start_symbol], 0)
    I0 = closure({initial_item}, grammar)
    
    C = [I0]
    state_map = {I0: 0}
    
    changed = True
    while changed:
        changed = False
        
        for i, state in enumerate(C):
            # Get all symbols that can be shifted in this state
            symbols = set()
            for item in state:
                next_sym = item.next_symbol()
                if next_sym:
                    symbols.add(next_sym)
            
            for symbol in symbols:
                new_state = goto(state, symbol, grammar)
                if new_state and new_state not in state_map:
                    state_map[new_state] = len(C)
                    C.append(new_state)
                    changed = True
    
    return C, state_map, start_aug

def build_slr_table(grammar, first_sets, follow_sets):
    C, state_map, start_aug = build_canonical_collection(grammar)
    
    action_table = defaultdict(dict)
    goto_table = defaultdict(dict)
    is_slr = True
    
    for state in C:
        state_id = state_map[state]
        
        for item in state:
            if item.is_reduce_item():
                # Reduce item
                if item.lhs == start_aug:
                    # Accept action
                    if '$' in action_table[state_id]:
                        is_slr = False
                    action_table[state_id]['$'] = 'accept'
                else:
                    # Reduce by item.lhs -> item.rhs
                    production_str = ' '.join(item.rhs) if item.rhs else grammar.epsilon
                    for terminal in follow_sets[item.lhs]:
                        if terminal in action_table[state_id]:
                            # Conflict: reduce-reduce or shift-reduce
                            is_slr = False
                        action_table[state_id][terminal] = ('reduce', item.lhs, production_str)
            else:
                # Shift item
                next_sym = item.next_symbol()
                next_state = state_map[goto(state, next_sym, grammar)]
                
                if next_sym in grammar.terminals:
                    if next_sym in action_table[state_id]:
                        # Conflict: shift-shift or shift-reduce
                        is_slr = False
                    action_table[state_id][next_sym] = ('shift', next_state)
                elif next_sym in grammar.non_terminals:
                    goto_table[state_id][next_sym] = next_state
    
    return dict(action_table), dict(goto_table), is_slr

def parse_slr(grammar, action_table, goto_table, input_tokens):
    state_stack = [0]
    input_tokens = input_tokens + ['$']
    input_index = 0
    
    while True:
        current_state = state_stack[-1]
        current_token = input_tokens[input_index]
        
        if current_token not in action_table.get(current_state, {}):
            return False
        
        action = action_table[current_state][current_token]
        
        if action == 'accept':
            return True
        elif action[0] == 'shift':
            state_stack.append(action[1])
            input_index += 1
        elif action[0] == 'reduce':
            lhs, rhs_str = action[1], action[2]
            rhs = [] if rhs_str == grammar.epsilon else rhs_str.split()
            
            # Pop states for each symbol in RHS
            for _ in range(len(rhs)):
                state_stack.pop()
            
            # Goto new state
            prev_state = state_stack[-1]
            if lhs not in goto_table.get(prev_state, {}):
                return False
            
            state_stack.append(goto_table[prev_state][lhs])
        else:
            return False