import re
import unicodedata

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()

def delete_duplicates(jobs):
    result = []
    seen = set()
    for job in jobs:
        key = (_norm(job["title"]), _norm(job["company"]))
        if key not in seen:
            seen.add(key)
            result.append(job)
    return result

def filter_jobs(jobs: list, query: str) -> list:
    """Garde les offres dont le titre satisfait l'expression booléenne
    (AND / OR / NOT / parenthèses / "phrases entre guillemets")."""

    def tokenize(q):
        return re.findall(r'"[^"]*"|AND|OR|NOT|\(|\)|\S+', q)

    def parse(tokens, i=0):
        left, i = parse_and(tokens, i)
        while i < len(tokens) and tokens[i] == "OR":
            right, i = parse_and(tokens, i + 1)
            left = ("OR", left, right)
        return left, i

    def parse_and(tokens, i):
        left, i = parse_atom(tokens, i)
        while i < len(tokens) and tokens[i] == "AND":
            right, i = parse_atom(tokens, i + 1)
            left = ("AND", left, right)
        return left, i

    def parse_atom(tokens, i):
        if tokens[i] == "NOT":
            child, i = parse_atom(tokens, i + 1)
            return ("NOT", child), i
        if tokens[i] == "(":
            expr, i = parse(tokens, i + 1)
            return expr, i + 1 
        return ("WORD", tokens[i].strip('"').lower()), i + 1

    def match(node, text):
        if node[0] == "WORD": return node[1] in text
        if node[0] == "AND":  return match(node[1], text) and match(node[2], text)
        if node[0] == "OR":   return match(node[1], text) or match(node[2], text)
        if node[0] == "NOT":  return not match(node[1], text)

    tokens = tokenize(query)
    if not tokens:
        return jobs
    tree, _ = parse(tokens)
    return [job for job in jobs if match(tree, job["title"].lower())]

