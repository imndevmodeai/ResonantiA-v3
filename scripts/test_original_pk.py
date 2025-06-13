import json
from Three_PointO_ArchE.abm_dsl_engine import create_model_from_schema
schema=json.load(open('contexts/pk_detection_context.json'))['schema']
model=create_model_from_schema(schema)
for _ in range(72):
    model.step()
print(model.last_body_attrs) 