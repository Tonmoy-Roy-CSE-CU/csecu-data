# Python script to generate TBox (ontology schema) and ABox (data instances) files in Turtle (TTL) format
# based on the mental health dataset CSV.
# This script is inspired by the style in the professor's agricultural knowledge graph paper,
# using RDF, OWL, QB4OLAP for multidimensional semantics, and linking to external sources like Wikidata.
# It handles the updated Snowflake schema with normalized dimensions and Person_Dimension.
# Assumptions:
# - The CSV file 'mental_health_data_final_data.csv' is in the same directory.
# - We use rdflib library for RDF generation (install via pip if needed: pip install rdflib).
# - For large datasets (50k rows), this may take time and memory; optimize if necessary.
# - External links: Example for countries to Wikidata; extend as needed for other dimensions.
# - TBox defines classes, properties, hierarchies.
# - ABox creates instances, using maps for unique IDs in normalized dimensions (Snowflake style).
# - Outputs: tbox.ttl and abox.ttl.

import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, Namespace, XSD
from rdflib.namespace import RDFS, OWL, QB, SKOS

# Step 1: Load the dataset from CSV
# Comment: The dataset has columns like User_ID, Age, Gender, etc. We read it into a Pandas DataFrame.
df = pd.read_csv('mental_health_data_final_data.csv')

# Step 2: Define namespaces for the ontology
# Comment: MH is the base namespace for mental health ontology, WD for Wikidata links.
MH = Namespace('http://example.org/mental_health#')
WD = Namespace('http://www.wikidata.org/entity/')
ex = Namespace('http://example.org/ontology#')  # For additional properties if needed

# Step 3: Create TBox graph (Terminological Box - schema/ontology)
# Comment: TBox defines classes (e.g., Person, MentalHealth), properties (e.g., hasAge), and hierarchies.
# We integrate QB4OLAP elements for OLAP compatibility, as in the agri paper.
tbox = Graph()
tbox.bind('mh', MH)
tbox.bind('wd', WD)
tbox.bind('ex', ex)
tbox.bind('rdfs', RDFS)
tbox.bind('owl', OWL)
tbox.bind('qb', QB)
tbox.bind('skos', SKOS)

# Define classes
# Comment: Classes based on schema: Person_Dimension, Mental_Health_Dim, Lifestyle_Dim, and sub-dimensions.
tbox.add((MH.Person, RDF.type, OWL.Class))
tbox.add((MH.Person, RDFS.label, Literal('Person', lang='en')))
tbox.add((MH.Person, RDFS.comment, Literal('Represents an individual with demographic attributes.')))

tbox.add((MH.MentalHealth, RDF.type, OWL.Class))
tbox.add((MH.MentalHealth, RDFS.label, Literal('Mental Health', lang='en')))
tbox.add((MH.MentalHealth, RDFS.comment, Literal('Captures mental health condition details.')))

tbox.add((MH.Lifestyle, RDF.type, OWL.Class))
tbox.add((MH.Lifestyle, RDFS.label, Literal('Lifestyle', lang='en')))
tbox.add((MH.Lifestyle, RDFS.comment, Literal('Captures lifestyle factors like diet, smoking.')))

# Normalized sub-classes for Snowflake schema
tbox.add((MH.Gender, RDF.type, OWL.Class))
tbox.add((MH.Occupation, RDF.type, OWL.Class))
tbox.add((MH.Country, RDF.type, OWL.Class))
tbox.add((MH.Severity, RDF.type, OWL.Class))
tbox.add((MH.Consultation, RDF.type, OWL.Class))
tbox.add((MH.StressLevel, RDF.type, OWL.Class))
tbox.add((MH.Medication, RDF.type, OWL.Class))
tbox.add((MH.DietQuality, RDF.type, OWL.Class))
tbox.add((MH.SmokingHabit, RDF.type, OWL.Class))
tbox.add((MH.AlcoholConsumption, RDF.type, OWL.Class))

# QB4OLAP for measurements and hierarchies
tbox.add((MH.Measurement, RDF.type, QB.DataStructureDefinition))
tbox.add((MH.Measurement, RDFS.label, Literal('Measurement', lang='en')))
tbox.add((MH.Measurement, RDFS.comment, Literal('Multidimensional measurements for OLAP.')))

# Define hierarchies (e.g., for Country dimension, using SKOS for concept schemes as in agri paper)
tbox.add((MH.CountryHierarchy, RDF.type, SKOS.ConceptScheme))
tbox.add((MH.CountryHierarchy, RDFS.label, Literal('Country Hierarchy')))
tbox.add((MH.Country, SKOS.inScheme, MH.CountryHierarchy))

# Similar for other dimensions if hierarchies exist (e.g., Severity: None < Low < Medium < High)
tbox.add((MH.SeverityHierarchy, RDF.type, SKOS.ConceptScheme))
tbox.add((MH.Severity, SKOS.inScheme, MH.SeverityHierarchy))
# Add levels if needed, e.g., skos:broader for hierarchy

# Define properties
# Comment: Properties link classes, with domain/range. Datatype for scalars, Object for links.
# Person properties
tbox.add((MH.hasAge, RDF.type, OWL.DatatypeProperty))
tbox.add((MH.hasAge, RDFS.domain, MH.Person))
tbox.add((MH.hasAge, RDFS.range, XSD.integer))

tbox.add((MH.hasGender, RDF.type, OWL.ObjectProperty))
tbox.add((MH.hasGender, RDFS.domain, MH.Person))
tbox.add((MH.hasGender, RDFS.range, MH.Gender))

tbox.add((MH.hasOccupation, RDF.type, OWL.ObjectProperty))
tbox.add((MH.hasOccupation, RDFS.domain, MH.Person))
tbox.add((MH.hasOccupation, RDFS.range, MH.Occupation))

tbox.add((MH.hasCountry, RDF.type, OWL.ObjectProperty))
tbox.add((MH.hasCountry, RDFS.domain, MH.Person))
tbox.add((MH.hasCountry, RDFS.range, MH.Country))
tbox.add((MH.hasCountry, OWL.equivalentProperty, WD.P17))  # Link to Wikidata 'country' property

# Mental Health properties
tbox.add((MH.hasMentalHealth, RDF.type, OWL.ObjectProperty))
tbox.add((MH.hasMentalHealth, RDFS.domain, MH.Person))
tbox.add((MH.hasMentalHealth, RDFS.range, MH.MentalHealth))

tbox.add((MH.hasSeverity, RDF.type, OWL.ObjectProperty))
tbox.add((MH.hasSeverity, RDFS.domain, MH.MentalHealth))
tbox.add((MH.hasSeverity, RDFS.range, MH.Severity))

tbox.add((MH.hasConsultationHistory, RDF.type, OWL.ObjectProperty))
tbox.add((MH.hasConsultationHistory, RDFS.domain, MH.MentalHealth))
tbox.add((MH.hasConsultationHistory, RDFS.range, MH.Consultation))

tbox.add((MH.hasStressLevel, RDF.type, OWL.ObjectProperty))
tbox.add((MH.hasStressLevel, RDFS.domain, MH.MentalHealth))
tbox.add((MH.hasStressLevel, RDFS.range, MH.StressLevel))

tbox.add((MH.hasMedicationUsage, RDF.type, OWL.ObjectProperty))
tbox.add((MH.hasMedicationUsage, RDFS.domain, MH.MentalHealth))
tbox.add((MH.hasMedicationUsage, RDFS.range, MH.Medication))

# Lifestyle properties
tbox.add((MH.hasLifestyle, RDF.type, OWL.ObjectProperty))
tbox.add((MH.hasLifestyle, RDFS.domain, MH.Person))
tbox.add((MH.hasLifestyle, RDFS.range, MH.Lifestyle))

tbox.add((MH.hasDietQuality, RDF.type, OWL.ObjectProperty))
tbox.add((MH.hasDietQuality, RDFS.domain, MH.Lifestyle))
tbox.add((MH.hasDietQuality, RDFS.range, MH.DietQuality))

tbox.add((MH.hasSmokingHabit, RDF.type, OWL.ObjectProperty))
tbox.add((MH.hasSmokingHabit, RDFS.domain, MH.Lifestyle))
tbox.add((MH.hasSmokingHabit, RDFS.range, MH.SmokingHabit))

tbox.add((MH.hasAlcoholConsumption, RDF.type, OWL.ObjectProperty))
tbox.add((MH.hasAlcoholConsumption, RDFS.domain, MH.Lifestyle))
tbox.add((MH.hasAlcoholConsumption, RDFS.range, MH.AlcoholConsumption))

# Measurement properties (for facts)
tbox.add((MH.hasSleepHours, RDF.type, OWL.DatatypeProperty))
tbox.add((MH.hasSleepHours, RDFS.domain, MH.Measurement))
tbox.add((MH.hasSleepHours, RDFS.range, XSD.float))
tbox.add((MH.hasSleepHours, QB.measure, Literal('Sleep Hours')))  # QB4OLAP measure

tbox.add((MH.hasWorkHours, RDF.type, OWL.DatatypeProperty))
tbox.add((MH.hasWorkHours, RDFS.domain, MH.Measurement))
tbox.add((MH.hasWorkHours, RDFS.range, XSD.integer))
tbox.add((MH.hasWorkHours, QB.measure, Literal('Work Hours')))

tbox.add((MH.hasPhysicalActivityHours, RDF.type, OWL.DatatypeProperty))
tbox.add((MH.hasPhysicalActivityHours, RDFS.domain, MH.Measurement))
tbox.add((MH.hasPhysicalActivityHours, RDFS.range, XSD.integer))
tbox.add((MH.hasPhysicalActivityHours, QB.measure, Literal('Physical Activity Hours')))

tbox.add((MH.hasSocialMediaUsage, RDF.type, OWL.DatatypeProperty))
tbox.add((MH.hasSocialMediaUsage, RDFS.domain, MH.Measurement))
tbox.add((MH.hasSocialMediaUsage, RDFS.range, XSD.float))
tbox.add((MH.hasSocialMediaUsage, QB.measure, Literal('Social Media Usage')))

tbox.add((ex.hasMeasurement, RDF.type, OWL.ObjectProperty))
tbox.add((ex.hasMeasurement, RDFS.domain, MH.Person))
tbox.add((ex.hasMeasurement, RDFS.range, MH.Measurement))

# Step 4: Save TBox to file
# Comment: Serialize as Turtle format for readability, like in the agri paper.
tbox.serialize(destination='tbox.ttl', format='turtle')

# Step 5: Create ABox graph (Assertional Box - data instances)
# Comment: ABox populates instances from CSV. Use dictionaries to map unique values to IDs for normalization (Snowflake).
abox = Graph()
abox.bind('mh', MH)
abox.bind('wd', WD)

# Maps for unique dimension IDs (normalization)
gender_map = {}  # gender -> id
occupation_map = {}
country_map = {}
severity_map = {}
consultation_map = {}
stress_map = {}
medication_map = {}
diet_map = {}
smoking_map = {}
alcohol_map = {}

mental_health_counter = 1
lifestyle_counter = 1

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    # Person instance
    user_uri = MH[f'user/{row["User_ID"]}']
    abox.add((user_uri, RDF.type, MH.Person))
    abox.add((user_uri, MH.hasAge, Literal(row['Age'], datatype=XSD.integer)))

    # Gender (normalized)
    gender_value = row['Gender']
    if gender_value not in gender_map:
        gender_id = len(gender_map) + 1
        gender_map[gender_value] = gender_id
        gender_uri = MH[f'gender/{gender_id}']
        abox.add((gender_uri, RDF.type, MH.Gender))
        abox.add((gender_uri, SKOS.prefLabel, Literal(gender_value)))
    abox.add((user_uri, MH.hasGender, MH[f'gender/{gender_map[gender_value]}']))

    # Occupation (normalized)
    occupation_value = row['Occupation']
    if occupation_value not in occupation_map:
        occ_id = len(occupation_map) + 1
        occupation_map[occupation_value] = occ_id
        occ_uri = MH[f'occupation/{occ_id}']
        abox.add((occ_uri, RDF.type, MH.Occupation))
        abox.add((occ_uri, SKOS.prefLabel, Literal(occupation_value)))
    abox.add((user_uri, MH.hasOccupation, MH[f'occupation/{occupation_map[occupation_value]}']))

    # Country (normalized, with Wikidata link example)
    country_value = row['Country']
    if country_value not in country_map:
        country_id = len(country_map) + 1
        country_map[country_value] = country_id
        country_uri = MH[f'country/{country_id}']
        abox.add((country_uri, RDF.type, MH.Country))
        abox.add((country_uri, SKOS.prefLabel, Literal(country_value)))
        # Example Wikidata sameAs links (extend with a dict for all countries)
        country_wd_map = {'Australia': WD.Q408, 'USA': WD.Q30, 'India': WD.Q668, 'UK': WD.Q145, 'Canada': WD.Q16, 'Germany': WD.Q183, 'Other': None}
        if country_value in country_wd_map and country_wd_map[country_value]:
            abox.add((country_uri, OWL.sameAs, country_wd_map[country_value]))
    abox.add((user_uri, MH.hasCountry, MH[f'country/{country_map[country_value]}']))

    # Mental Health instance (normalized)
    mh_uri = MH[f'mental_health/{mental_health_counter}']
    abox.add((mh_uri, RDF.type, MH.MentalHealth))
    abox.add((mh_uri, RDFS.label, Literal(row['Mental_Health_Condition'])))
    abox.add((user_uri, MH.hasMentalHealth, mh_uri))

    # Severity
    severity_value = row['Severity']
    if severity_value not in severity_map:
        sev_id = len(severity_map) + 1
        severity_map[severity_value] = sev_id
        sev_uri = MH[f'severity/{sev_id}']
        abox.add((sev_uri, RDF.type, MH.Severity))
        abox.add((sev_uri, SKOS.prefLabel, Literal(severity_value)))
    abox.add((mh_uri, MH.hasSeverity, MH[f'severity/{severity_map[severity_value]}']))

    # Consultation
    consultation_value = row['Consultation_History']
    if consultation_value not in consultation_map:
        cons_id = len(consultation_map) + 1
        consultation_map[consultation_value] = cons_id
        cons_uri = MH[f'consultation/{cons_id}']
        abox.add((cons_uri, RDF.type, MH.Consultation))
        abox.add((cons_uri, SKOS.prefLabel, Literal(consultation_value)))
    abox.add((mh_uri, MH.hasConsultationHistory, MH[f'consultation/{consultation_map[consultation_value]}']))

    # Stress Level
    stress_value = row['Stress_Level']
    if stress_value not in stress_map:
        stress_id = len(stress_map) + 1
        stress_map[stress_value] = stress_id
        stress_uri = MH[f'stress/{stress_id}']
        abox.add((stress_uri, RDF.type, MH.StressLevel))
        abox.add((stress_uri, SKOS.prefLabel, Literal(stress_value)))
    abox.add((mh_uri, MH.hasStressLevel, MH[f'stress/{stress_map[stress_value]}']))

    # Medication
    medication_value = row['Medication_Usage']
    if medication_value not in medication_map:
        med_id = len(medication_map) + 1
        medication_map[medication_value] = med_id
        med_uri = MH[f'medication/{med_id}']
        abox.add((med_uri, RDF.type, MH.Medication))
        abox.add((med_uri, SKOS.prefLabel, Literal(medication_value)))
    abox.add((mh_uri, MH.hasMedicationUsage, MH[f'medication/{medication_map[medication_value]}']))

    mental_health_counter += 1

    # Lifestyle instance
    ls_uri = MH[f'lifestyle/{lifestyle_counter}']
    abox.add((ls_uri, RDF.type, MH.Lifestyle))
    abox.add((user_uri, MH.hasLifestyle, ls_uri))

    # Diet Quality
    diet_value = row['Diet_Quality']
    if diet_value not in diet_map:
        diet_id = len(diet_map) + 1
        diet_map[diet_value] = diet_id
        diet_uri = MH[f'diet/{diet_id}']
        abox.add((diet_uri, RDF.type, MH.DietQuality))
        abox.add((diet_uri, SKOS.prefLabel, Literal(diet_value)))
    abox.add((ls_uri, MH.hasDietQuality, MH[f'diet/{diet_map[diet_value]}']))

    # Smoking Habit
    smoking_value = row['Smoking_Habit']
    if smoking_value not in smoking_map:
        smoke_id = len(smoking_map) + 1
        smoking_map[smoking_value] = smoke_id
        smoke_uri = MH[f'smoking/{smoke_id}']
        abox.add((smoke_uri, RDF.type, MH.SmokingHabit))
        abox.add((smoke_uri, SKOS.prefLabel, Literal(smoking_value)))
    abox.add((ls_uri, MH.hasSmokingHabit, MH[f'smoking/{smoking_map[smoking_value]}']))

    # Alcohol Consumption
    alcohol_value = row['Alcohol_Consumption']
    if alcohol_value not in alcohol_map:
        alc_id = len(alcohol_map) + 1
        alcohol_map[alcohol_value] = alc_id
        alc_uri = MH[f'alcohol/{alc_id}']
        abox.add((alc_uri, RDF.type, MH.AlcoholConsumption))
        abox.add((alc_uri, SKOS.prefLabel, Literal(alcohol_value)))
    abox.add((ls_uri, MH.hasAlcoholConsumption, MH[f'alcohol/{alcohol_map[alcohol_value]}']))

    lifestyle_counter += 1

    # Measurement instance (facts)
    meas_uri = MH[f'measurement/{row["User_ID"]}']
    abox.add((meas_uri, RDF.type, MH.Measurement))
    abox.add((meas_uri, MH.hasSleepHours, Literal(row['Sleep_Hours'], datatype=XSD.float)))
    abox.add((meas_uri, MH.hasWorkHours, Literal(row['Work_Hours'], datatype=XSD.integer)))
    abox.add((meas_uri, MH.hasPhysicalActivityHours, Literal(row['Physical_Activity_Hours'], datatype=XSD.integer)))
    abox.add((meas_uri, MH.hasSocialMediaUsage, Literal(row['Social_Media_Usage'], datatype=XSD.float)))
    abox.add((user_uri, ex.hasMeasurement, meas_uri))  # Link measurements to person

# Step 6: Save ABox to file
# Comment: Serialize as Turtle. For very large ABox, consider splitting files or using a triple store like Virtuoso.
abox.serialize(destination='abox.ttl', format='turtle')

print("TBox and ABox TTL files generated successfully.")