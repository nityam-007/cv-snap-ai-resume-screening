import re

neo_path = '/Users/nityam/cv-snap-project/backend/neo4j_service.py'
with open(neo_path, 'r') as f:
    neo_code = f.read()

edu_func = """
    def create_education_nodes(self, candidate_id: str, education: List[Dict[str, Any]]) -> List[str]:
        if not education: return []
        with self.driver.session() as session:
            created = []
            for i, edu in enumerate(education):
                edu_id = f"{candidate_id}_edu_{i}"
                query = '''MATCH (c:Candidate {id: $candidate_id})
                           CREATE (ed:Education {id: $edu_id, degree: $degree, field: $field, institution: $inst, year: $year})
                           CREATE (c)-[:HAS_EDUCATION]->(ed)
                           RETURN ed.id as edu_id'''
                try:
                    res = session.run(query, candidate_id=candidate_id, edu_id=edu_id,
                                      degree=edu.get('degree', 'Unknown'), field=edu.get('field', 'Unknown'),
                                      inst=edu.get('institution', 'Unknown'), year=edu.get('year', 'Unknown'))
                    created.append(res.single()['edu_id'])
                except Exception as e: pass
            return created
"""

# Append to the class if not present
if "def create_education_nodes" not in neo_code:
    # Just put it before def get_all_candidates_for_job
    neo_code = neo_code.replace("    def get_all_candidates_for_job", edu_func + "\n    def get_all_candidates_for_job")

with open(neo_path, 'w') as f:
    f.write(neo_code)

print("Hotfix 2 applied!")
