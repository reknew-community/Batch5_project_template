"""Service for loading family tree data from CSV files."""

from pathlib import Path
from typing import List, Tuple
import pandas as pd

from src.config.family_settings import ft_settings as settings
from src.models import Person, Relationship


class DataLoader:
    """Loads and validates family tree data from CSV files."""
    
    def __init__(self, data_dir: Path = None):
        """
        Initialize the data loader.
        
        Args:
            data_dir: Directory containing CSV files (defaults to RAW_DATA_DIR from settings)
        """
        self.data_dir = data_dir or settings.RAW_DATA_DIR
        print(f"📂 DataLoader initialized with directory: {self.data_dir}")
    
    def load_people(self, filename: str = None) -> List[Person]:
        """
        Load people from CSV file.
        
        Args:
            filename: CSV filename (defaults to PEOPLE_CSV from settings)
            
        Returns:
            List of Person objects
        """
        filename = filename or settings.PEOPLE_CSV
        filepath = self.data_dir / filename
        
        print(f"📖 Loading people from: {filepath}")
        
        if not filepath.exists():
            raise FileNotFoundError(f"❌ People CSV not found: {filepath}")
        
        # Read CSV file
        df = pd.read_csv(filepath)
        print(f"✅ CSV loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Convert each row to a Person object
        people = []
        for idx, row in df.iterrows():
            try:
                person = Person(
                                person_id=str(row['person_id']),
                                first_name=str(row['first_name']),
                                middle_name=str(row['middle_name']) if pd.notna(row.get('middle_name')) else '',
                                last_name=str(row['last_name']),
                                full_name=str(row['full_name']),
                                maiden_name=str(row['maiden_name']) if pd.notna(row.get('maiden_name')) else '',
                                birth_year=int(row['birth_year']) if pd.notna(row.get('birth_year')) else None,
                                died=int(row['died']) if pd.notna(row.get('died')) else None,
                                is_alive=str(row.get('is_alive', 'Yes')).lower() == 'yes',
                                gender=str(row['gender']),
                                ethnicity_1=str(row['ethnicity_1']) if pd.notna(row.get('ethnicity_1')) else '',
                                ethnicity_2=str(row['ethnicity_2']) if pd.notna(row.get('ethnicity_2')) else '',
                                ethnicity_3=str(row['ethnicity_3']) if pd.notna(row.get('ethnicity_3')) else '',
                                ethnicity_4=str(row['ethnicity_4']) if pd.notna(row.get('ethnicity_4')) else '',
                                notes=str(row['notes']) if pd.notna(row.get('notes')) else ''
                            )
                people.append(person)
            except Exception as e:
                print(f"❌ Error parsing row {idx}: {e}")
                raise
        
        print(f"✅ Loaded {len(people)} people successfully")
        return people
    
    def load_relationships(self, filename: str = None) -> List[Relationship]:
        """
        Load relationships from CSV file.
        
        Args:
            filename: CSV filename (defaults to RELATIONSHIPS_CSV from settings)
            
        Returns:
            List of Relationship objects
        """
        filename = filename or settings.RELATIONSHIPS_CSV
        filepath = self.data_dir / filename
        
        print(f"📖 Loading relationships from: {filepath}")
        
        if not filepath.exists():
            raise FileNotFoundError(f"❌ Relationships CSV not found: {filepath}")
        
        # Read CSV file
        df = pd.read_csv(filepath)
        print(f"✅ CSV loaded: {len(df)} rows")
        
        # Convert each row to a Relationship object
        relationships = []
        for idx, row in df.iterrows():
            try:
                rel = Relationship(
                    from_person_id=row['from_person_id'],
                    relationship=row['relationship'],
                    to_person_id=row['to_person_id']
                )
                relationships.append(rel)
            except Exception as e:
                print(f"❌ Error parsing row {idx}: {e}")
                raise
        
        print(f"✅ Loaded {len(relationships)} relationships successfully")
        return relationships
    
    def load_all(self) -> Tuple[List[Person], List[Relationship]]:
        """
        Load both people and relationships.
        
        Returns:
            Tuple of (people, relationships)
        """
        print("\n" + "="*60)
        print("🚀 Loading all family tree data")
        print("="*60)
        
        people = self.load_people()
        relationships = self.load_relationships()
        
        # Validate that all person IDs in relationships exist
        person_ids = {p.person_id for p in people}
        invalid_rels = 0
        
        for rel in relationships:
            if rel.from_person_id not in person_ids:
                print(f"⚠️  Warning: Unknown person ID '{rel.from_person_id}' in relationship")
                invalid_rels += 1
            if rel.to_person_id not in person_ids:
                print(f"⚠️  Warning: Unknown person ID '{rel.to_person_id}' in relationship")
                invalid_rels += 1
        
        if invalid_rels == 0:
            print("✅ All relationships reference valid people")
        
        print(f"\n✅ Data loading complete!")
        print(f"   People: {len(people)}")
        print(f"   Relationships: {len(relationships)}")
        
        return people, relationships