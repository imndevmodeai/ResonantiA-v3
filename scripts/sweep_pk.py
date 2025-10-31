#!/usr/bin/env python
import json, itertools, os
from Three_PointO_ArchE.abm_dsl_engine import create_model_from_schema

schema_base = json.load(open('contexts/pk_detection_context.json'))['schema']

vitc_opts = [-0.1, -0.2, -0.3, -0.4]  # pH delta from Vit C (approx dosage)
bicarb_opts = [0.2, 0.4, 0.6, 0.8]     # pH delta from NaHCO3 (alkaline)

results = []
for vit_delta, bic_delta in itertools.product(vitc_opts, bicarb_opts):
    schema = json.loads(json.dumps(schema_base))
    # update behaviour entries for Body
    beh = schema['agents'][0]['behaviour']
    beh_new = []
    for line in beh:
        if line.startswith('pHShift(-') and 'window=[-72,-18]' in line:
            beh_new.append(f"pHShift({vit_delta}, window=[-72,-18])")
        elif line.startswith('pHShift(+') and 'window=[-24,0]' in line:
            beh_new.append(f"pHShift({bic_delta}, window=[-24,0])")
        elif line.startswith('ScheduleDose(AMP'):
            # strip existing dosing; we'll re-add below
            continue
        else:
            beh_new.append(line)
    # add regular AMP dosing every 12h from -60 to 0
    for h in range(-60, 1, 12):
        beh_new.append(f"ScheduleDose(AMP, 15, at_hour={h})")
    schema['agents'][0]['behaviour'] = beh_new
    model = create_model_from_schema(schema)
    for _ in range(72):
        model.step()
    attrs = getattr(model, 'last_body_attrs', {})
    mamp = attrs.get('MAMP', 0)
    amp = attrs.get('AMP', 0)
    results.append({
        'vitC_delta': vit_delta, 'bicarb_delta': bic_delta,
        'MAMP': mamp, 'AMP': amp,
        'MAMP_pos': mamp > 50, 'AMP_pos': amp > 20
    })

print("vitC_delta,bicarb_delta,MAMP,AMP,MAMP_pos,AMP_pos")
for r in results:
    print(f"{r['vitC_delta']},{r['bicarb_delta']},{r['MAMP']:.1f},{r['AMP']:.1f},{r['MAMP_pos']},{r['AMP_pos']}") 