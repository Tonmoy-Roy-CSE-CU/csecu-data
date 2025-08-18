import time
import rdflib
from rdflib import Graph
import matplotlib.pyplot as plt
import numpy as np

# Load the TBox and ABox into a single graph (assuming tbox.ttl and abox.ttl are in the current directory)
g = Graph()
g.parse("tbox.ttl", format="turtle")
g.parse("abox.ttl", format="turtle")

# Define sample SPARQL queries from your paper (roll-up, drill-down, slice, dice)
queries = {
    "roll_up_sleep_by_country": """
    PREFIX mh: <http://example.org/mental_health#>
    PREFIX ex: <http://example.org/ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?country (AVG(?sleepHours) AS ?avgSleepHours)
    WHERE {
      ?user a mh:Person ;
            ex:hasMeasurement ?measurement ;
            mh:hasCountry ?countryUri .
      ?measurement mh:hasSleepHours ?sleepHours .
      ?countryUri skos:prefLabel ?country .
      FILTER (datatype(?sleepHours) = xsd:float)
    }
    GROUP BY ?country
    ORDER BY ?country
    """,
    
    "drill_down_work_by_country_gender": """
    PREFIX mh: <http://example.org/mental_health#>
    PREFIX ex: <http://example.org/ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?country ?gender (AVG(?workHours) AS ?avgWorkHours)
    WHERE {
      ?user a mh:Person ;
            ex:hasMeasurement ?measurement ;
            mh:hasCountry ?countryUri ;
            mh:hasGender ?genderUri .
      ?measurement mh:hasWorkHours ?workHours .
      ?countryUri skos:prefLabel ?country .
      ?genderUri skos:prefLabel ?gender .
      FILTER (datatype(?workHours) = xsd:integer)
    }
    GROUP BY ?country ?gender
    ORDER BY ?country ?gender
    """,
    
    "slice_high_stress": """
    PREFIX mh: <http://example.org/mental_health#>
    PREFIX ex: <http://example.org/ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?user ?country ?sleepHours
    WHERE {
      ?user a mh:Person ;
            mh:hasMentalHealth ?mh ;
            mh:hasCountry ?countryUri ;
            ex:hasMeasurement ?measurement .
      ?mh mh:hasStressLevel ?stressUri .
      ?stressUri skos:prefLabel "High" .
      ?measurement mh:hasSleepHours ?sleepHours .
      ?countryUri skos:prefLabel ?country .
      FILTER (datatype(?sleepHours) = xsd:float)
    }
    ORDER BY ?country ?user
    """,
    
    "dice_medium_severity_australia": """
    PREFIX mh: <http://example.org/mental_health#>
    PREFIX ex: <http://example.org/ontology#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?user ?age ?workHours
    WHERE {
      ?user a mh:Person ;
            mh:hasMentalHealth ?mh ;
            mh:hasCountry ?countryUri ;
            ex:hasMeasurement ?measurement ;
            mh:hasAge ?age .
      ?mh mh:hasSeverity ?severityUri .
      ?severityUri skos:prefLabel "Medium" .
      ?countryUri skos:prefLabel "Australia" .
      ?measurement mh:hasWorkHours ?workHours .
      FILTER (datatype(?age) = xsd:integer && datatype(?workHours) = xsd:integer)
    }
    ORDER BY ?age ?user
    """
}

# Function to measure query execution time
def measure_query_time(graph, query_name, query):
    start_time = time.time()
    result = graph.query(query)
    end_time = time.time()
    execution_time = end_time - start_time
    row_count = len(result)
    return {
        "query_name": query_name,
        "execution_time": execution_time,
        "row_count": row_count
    }

# Run benchmarks for all queries on the full dataset (50k records)
benchmarks_full = []
for name, q in queries.items():
    benchmarks_full.append(measure_query_time(g, name, q))

print("Benchmarks for Full Dataset (50,000 records):")
for b in benchmarks_full:
    print(f"{b['query_name']}: {b['execution_time']:.4f} seconds, {b['row_count']} rows")

# For scalability: Subsample the graph for different sizes
def create_subsampled_graph(graph, max_user_id):
    sub_g = Graph()
    for s, p, o in graph:
        if "user/" in str(s) and int(str(s).split('/')[-1]) <= max_user_id:
            sub_g.add((s, p, o))
        # Include dimension instances as they are shared across users
        elif "gender/" in str(s) or "occupation/" in str(s) or "country/" in str(s) or \
             "severity/" in str(s) or "consultation/" in str(s) or "stress/" in str(s) or \
             "medication/" in str(s) or "diet/" in str(s) or "smoking/" in str(s) or "alcohol/" in str(s):
            sub_g.add((s, p, o))
    return sub_g

# Test scalability with different sizes (e.g., 10k, 25k, 50k users)
sizes = [10000, 25000, 50000]
scalability_results = {}

for size in sizes:
    sub_g = create_subsampled_graph(g, size)
    benchmarks = []
    for name, q in queries.items():
        benchmarks.append(measure_query_time(sub_g, name, q))
    scalability_results[size] = benchmarks

print("\nScalability Benchmarks:")
for size, bens in scalability_results.items():
    print(f"Dataset Size: {size} records")
    for b in bens:
        print(f"  {b['query_name']}: {b['execution_time']:.4f} seconds, {b['row_count']} rows")

# Generate figure for benchmarks
# Prepare data for plotting
query_names = [b["query_name"] for b in benchmarks_full]
full_times = [b["execution_time"] * 1000 for b in benchmarks_full]  # Convert to milliseconds for readability
scalability_sizes = list(scalability_results.keys())
scalability_times = {size: [b["execution_time"] * 1000 for b in bens] for size, bens in scalability_results.items()}

# Create bar chart for full dataset benchmarks
plt.figure(figsize=(10, 6))
plt.bar(query_names, full_times, color='skyblue')
plt.xlabel('Query Type')
plt.ylabel('Execution Time (ms)')
plt.title('OLAP Query Efficiency (50,000 Records)')
plt.xticks(rotation=45)
for i, v in enumerate(full_times):
    plt.text(i, v + 5, f'{v:.1f}', ha='center')
plt.tight_layout()

# Create line chart for scalability
plt.figure(figsize=(10, 6))
for i, name in enumerate(query_names):
    times = [scalability_times[size][i] for size in scalability_sizes]
    plt.plot(scalability_sizes, times, marker='o', label=name)
plt.xlabel('Dataset Size (records)')
plt.ylabel('Execution Time (ms)')
plt.title('Scalability: Dataset Size vs. Query Performance')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save figures
plt.figure(1).savefig('query_efficiency.png')
plt.figure(2).savefig('scalability_performance.png')
print("\nFigures saved as 'query_efficiency.png' and 'scalability_performance.png'")

# Optional: Display plots (uncomment if running interactively)
# plt.show()