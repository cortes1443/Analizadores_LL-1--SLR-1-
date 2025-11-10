# grammar.py
import re
from collections import defaultdict

class Grammar:
    def __init__(self):
        self.productions = defaultdict(list)
        self.non_terminals = set()
        self.terminals = set()
        self.start_symbol = 'S'
        self.epsilon = 'e'
        self.end_marker = '$'
        
    def add_production(self, nonterminal, alternatives):
        nonterminal = nonterminal.strip()
        self.non_terminals.add(nonterminal)
        
        for alt in alternatives:
            alt = alt.strip()
            if alt == 'e':
                alt = self.epsilon
            self.productions[nonterminal].append(alt)
            
            # Extract symbols from production
            symbols = self._extract_symbols(alt)
            for symbol in symbols:
                if symbol == self.epsilon:
                    continue
                if symbol and symbol[0].isupper():
                    self.non_terminals.add(symbol)
                else:
                    self.terminals.add(symbol)
    
    def _extract_symbols(self, production):
        """Extract symbols from production string"""
        if production == self.epsilon:
            return []
        
        # Simple tokenization: split by spaces
        symbols = production.split()
        return symbols
    
    def get_all_symbols(self):
        return self.terminals.union(self.non_terminals)
    
    def __str__(self):
        result = "Grammar:\n"
        for nt in sorted(self.non_terminals):
            prods = " | ".join(self.productions[nt])
            result += f"  {nt} -> {prods}\n"
        return result