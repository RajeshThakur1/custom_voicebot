# For existing DB tables
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rbacapp.database import Base, engine
import models 

print("Verifying existing database tables...")

for table_name in Base.metadata.tables.keys():
    print(f"Mapped model for table: {table_name}")
print("Done.")