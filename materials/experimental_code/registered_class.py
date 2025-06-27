workflow_registry = {}

class Workflow:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.steps = []
        workflow_registry[name] = self
    def add_step(self, func):
        self.steps.append(func)
    def run(self):
        print(f"Running workflow: {self.name}")
        for step in self.steps:
            step()
    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "steps": [f.__name__ for f in self.steps]
        }

# kroky
def parse_csv():
    print("Parsing CSV file...")
def validate_user():
    print("Validating user data...")
def save_to_db():
    print("Saving to DB...")
def load_orders():
    print("Loading orders...")
def push_to_api():
    print("Pushing data to API...")

# definice workflow
wf = Workflow("import_users", "Import uživatelů ze souboru")
wf.add_step(parse_csv)
wf.add_step(validate_user)
wf.add_step(save_to_db)

wf2 = Workflow("sync_orders")
wf2.add_step(load_orders)
wf2.add_step(push_to_api)

# serializace
import json
all_as_json = json.dumps(
    [w.to_json() for w in workflow_registry.values()],
    indent=2
)
print(all_as_json)

# spuštění jednoho workflow
wf.run()
