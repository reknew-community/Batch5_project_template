"""Quick test of the data loader."""

from src.services.data_loader import DataLoader

# Create loader and load data
loader = DataLoader()
people, relationships = loader.load_all()

# Print some examples
print("\n" + "="*60)
print("📊 Sample Data:")
print("="*60)
print(f"\nFirst person: {people[0].full_name}")
print(f"  ID: {people[0].person_id}")
print(f"  Gender: {people[0].gender}")
print(f"  Age: {people[0].age}")
print(f"  Ethnicities: {people[0].ethnicities}")

print(f"\nFirst relationship:")
print(f"  {relationships[0].from_person_id} --{relationships[0].relationship}--> {relationships[0].to_person_id}")