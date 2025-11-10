# main.py
from grammar import Grammar
from first_follow import compute_first, compute_follow
from ll1_parser import build_ll1_table, parse_ll1
from slr_parser import build_slr_table, parse_slr

def print_sets(grammar, first_sets, follow_sets):
    print("\n" + "="*40)
    print("FIRST sets")
    print("="*40)
    for nt in sorted(grammar.non_terminals):
        print(f"FIRST({nt}) = {{{', '.join(sorted(first_sets[nt]))}}}")
    
    print("\n" + "="*40)
    print("FOLLOW sets")
    print("="*40)
    for nt in sorted(grammar.non_terminals):
        print(f"FOLLOW({nt}) = {{{', '.join(sorted(follow_sets[nt]))}}}")

def tokenize_input(line):
    """Simple tokenizer - split by spaces"""
    return line.strip().split()

def run_parser_interface(grammar):
    # Compute FIRST and FOLLOW
    first_sets = compute_first(grammar)
    follow_sets = compute_follow(grammar, first_sets)
    
    print_sets(grammar, first_sets, follow_sets)
    
    # Check LL(1) and SLR(1)
    ll1_table, is_ll1 = build_ll1_table(grammar, first_sets, follow_sets)
    slr_action, slr_goto, is_slr = build_slr_table(grammar, first_sets, follow_sets)
    
    print(f"\nLL(1) check: {'YES' if is_ll1 else 'NO'}")
    print(f"SLR(1) check: {'YES' if is_slr else 'NO'}")
    
    # Determine case according to specification
    if is_ll1 and is_slr:
        # Case 1: Both LL(1) and SLR(1)
        print("\nGrammar is both SLR(1) and LL(1).")
        while True:
            choice = input("Select a parser (T: for LL(1), B: for SLR(1), Q: quit): ").strip().upper()
            if choice == 'Q':
                return
            elif choice in ('T', 'B'):
                break
            else:
                print("Invalid choice. Please enter T, B, or Q.")
        
        parser_type = 'LL' if choice == 'T' else 'SLR'
        print(f"Using {parser_type} parser. Enter strings to parse (empty line to stop):")
        
        while True:
            line = input().strip()
            if not line:
                break
            
            tokens = tokenize_input(line)
            if parser_type == 'LL':
                result = parse_ll1(grammar, ll1_table, tokens)
            else:
                result = parse_slr(grammar, slr_action, slr_goto, tokens)
            
            print("yes" if result else "no")
    
    elif is_ll1 and not is_slr:
        # Case 2: Only LL(1)
        print("\nGrammar is LL(1).")
        print("Enter strings to parse (empty line to stop):")
        
        while True:
            line = input().strip()
            if not line:
                break
            
            tokens = tokenize_input(line)
            result = parse_ll1(grammar, ll1_table, tokens)
            print("yes" if result else "no")
    
    elif is_slr and not is_ll1:
        # Case 3: Only SLR(1)
        print("\nGrammar is SLR(1).")
        print("Enter strings to parse (empty line to stop):")
        
        while True:
            line = input().strip()
            if not line:
                break
            
            tokens = tokenize_input(line)
            result = parse_slr(grammar, slr_action, slr_goto, tokens)
            print("yes" if result else "no")
    
    else:
        # Case 4: Neither
        print("\nGrammar is neither LL(1) nor SLR(1).")

def main():
    grammar = Grammar()
    
    print("Context-Free Grammar Parser")
    print("=" * 50)
    
    # Read number of non-terminals
    try:
        n = int(input("Enter number of nonterminals: ").strip())
        if n <= 0:
            print("Number of nonterminals must be positive.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    
    # Read productions
    print("Enter productions in format: A -> alpha | beta")
    print("Use 'e' for epsilon, spaces between symbols")
    
    for i in range(n):
        while True:
            line = input(f"Production {i+1}: ").strip()
            if '->' in line:
                lhs, rhs = line.split('->', 1)
                lhs = lhs.strip()
                alternatives = [alt.strip() for alt in rhs.split('|')]
                
                grammar.add_production(lhs, alternatives)
                break
            else:
                print("Invalid format. Use: A -> alpha | beta")
    
    print("\n" + "="*50)
    print("Grammar loaded successfully!")
    print(grammar)
    
    # Set start symbol (always S according to specification)
    grammar.start_symbol = 'S'
    
    # Run parser interface
    run_parser_interface(grammar)

if __name__ == "__main__":
    main()