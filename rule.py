from dataclasses import dataclass
import json

RULES_FILE = "./rules.json"


@dataclass
class Rule:
    regex: str
    tags: str
    notes: str

    def to_dict(self):
        return {'regex': self.regex, 'tags': self.tags, 'notes': self.notes}

def _parse_rules_json(rules_json: str) -> list[Rule]:
    rules = json.loads(rules_json)
    return [Rule(regex=r['regex'], tags=r['tags'], notes=r['notes'])
            for r in rules]


def load_rules() -> list[Rule]:
    try:
        with open(RULES_FILE, 'r', encoding='utf8') as f:
            return _parse_rules_json(f.read())

    except FileNotFoundError:
        # file doesn't exist, we create it
        with open(RULES_FILE, 'a', encoding='utf8') as f:
            json.dump([], f)
        return []


def save_rules(rules: list[Rule]) -> None:
    json_rules = [r.to_dict() for r in rules]
    with open(RULES_FILE, 'w', encoding='utf8') as f:
        json.dump(json_rules, f)
