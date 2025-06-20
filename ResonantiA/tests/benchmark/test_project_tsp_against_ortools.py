import os, json, pytest, math, logging
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE.utils.tsplib_loader import tsplib_to_abm_data
from Three_PointO_ArchE.benchmarks.ortools_baseline import solve as ortools_solve

# Configure logging for the test
logging.basicConfig(level=logging.INFO)
logging.getLogger("workflow_engine").setLevel(logging.INFO)
logging.getLogger("agent_based_modeling_tool").setLevel(logging.INFO)

DATA = [
    ('eil51', 426.0),
    # Add more instances if downloaded
]

datasets_dir = 'data/tsplib'

@pytest.mark.parametrize("instance, opt_dist", DATA)
def test_abm_vs_ortools(instance, opt_dist):
    tsp_path = os.path.join(datasets_dir, f"{instance}.tsp")
    if not os.path.exists(tsp_path):
        pytest.skip(f"TSPLIB file {instance} missing")

    tsp_data = tsplib_to_abm_data(tsp_path)

    print(f"DEBUG TEST: tsp_data before execute_workflow: cities present: {True if tsp_data and tsp_data.get('cities') else False}, num_cities: {len(tsp_data.get('cities', [])) if tsp_data else -1}", flush=True)
    # Run ABM workflow
    wf = json.load(open('../../../../todo/traveling_salesman_optimization.json'))
    engine = IARCompliantWorkflowEngine()
    res = engine.execute_workflow(wf, input_data={'tsp_data': tsp_data})
    abm_res = res['step_results']['tsp_simulation']['result']
    abm_dist = abm_res['total_distance']

    # OR-Tools baseline
    _, ort_dist = ortools_solve(tsp_data['cities'])

    ratio = abm_dist / ort_dist if ort_dist else math.inf
    print(f"\nInstance: {instance}")
    print(f"  ABM Best Distance: {abm_dist:.2f}")
    print(f"  OR-Tools Best Distance: {ort_dist:.2f}")
    print(f"  Ratio (ABM/ORTools): {ratio:.3f}")

    # Print Temporal Analysis and Flux
    sim_results = res['step_results']['tsp_simulation']['result']
    print(f"  Temporal Analysis Preview: {sim_results.get('temporal_analysis_preview')}")
    
    flux_history = sim_results.get('system_flux_history', [])
    # Filter out None values from flux history for cleaner printing if any exist from first gen or errors
    printable_flux_history = [f"{f:.4f}" for f in flux_history if f is not None]
    if printable_flux_history:
        print(f"  System Flux History (Euclidean distance between system states per gen):")
        # Print first few and last few flux values for brevity if history is long
        if len(printable_flux_history) > 10:
            print(f"    {printable_flux_history[:5]} ... {printable_flux_history[-5:]}")
        else:
            print(f"    {printable_flux_history}")
    else:
        print("  System Flux History: Not available or not computed.")

    # Print the full detailed temporal analysis
    detailed_analysis = sim_results.get('detailed_temporal_analysis')
    if detailed_analysis:
        print("  Detailed Temporal Analysis:")
        for key, value in detailed_analysis.items():
            if key == 'reflection': # Pretty print reflection separately
                continue
            if isinstance(value, float):
                print(f"    {key}: {value:.4f}")
            else:
                print(f"    {key}: {value}")
        if 'reflection' in detailed_analysis:
            print("    Reflection:")
            for r_key, r_value in detailed_analysis['reflection'].items():
                print(f"      {r_key}: {r_value}")
    else:
        print("  Detailed Temporal Analysis: Not available.")

    assert ratio <= 1.3, "ABM distance more than 30% worse than OR-Tools" 