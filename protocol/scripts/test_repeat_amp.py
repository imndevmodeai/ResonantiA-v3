import json
from Three_PointO_ArchE.abm_dsl_engine import create_model_from_schema

schema = json.load(open('contexts/pk_detection_context.json'))['schema']
beh = [b for b in schema['agents'][0]['behaviour'] if not b.startswith('ScheduleDose(AMP')]
for h in [-60,-48,-36,-24,-12,0]:
    beh.append(f"ScheduleDose(AMP, 15, at_hour={h})")
schema['agents'][0]['behaviour'] = beh
m = create_model_from_schema(schema)
for _ in range(72):
    m.step()
print('Final body attrs', m.last_body_attrs) 