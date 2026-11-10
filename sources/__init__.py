from .linkedin import LinkedIn
from .hellowork import HelloWork

# the sorting is important: if there is duplicates, the first one is kept
ALL_SOURCES = {cls.name: cls for cls in (HelloWork, LinkedIn)}

def get_sources(names=None) -> list:
    result = []
    for name, cls in ALL_SOURCES.items():
        if names and name not in names:
            continue
        if not cls.enabled():
            print(f"[{name}] ignored (missing config)")
            continue
        result.append(cls())
    return result