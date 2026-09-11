import re

# Update main.py
main_path = '/Users/nityam/cv-snap-project/backend/main.py'
with open(main_path, 'r') as f:
    main_code = f.read()

main_job_old = """        # Step 3: Create required skills nodes and link to job
        if job_data.get('required_skills'):
            skill_names = self.neo4j_service.create_skill_nodes(job_data['required_skills'])
            self.neo4j_service.link_job_requirements(job_id, job_data['required_skills'])"""
main_job_new = """        # Step 3: Create required skills nodes and link to job
        if job_data.get('required_skills'):
            skill_names = self.neo4j_service.create_skill_nodes(job_data['required_skills'])
            self.neo4j_service.link_job_requirements(job_id, job_data['required_skills'])
            
        # Step 3b: Create preferred skills nodes and link to job
        if job_data.get('preferred_skills'):
            self.neo4j_service.create_skill_nodes(job_data['preferred_skills'])
            self.neo4j_service.link_job_preferred_skills(job_id, job_data['preferred_skills'])"""
main_code = main_code.replace(main_job_old, main_job_new)

main_cand_old = """        # Create experience nodes
        if candidate_data.get('experience'):
            self.neo4j_service.create_experience_nodes(candidate_id, candidate_data['experience'])"""
main_cand_new = """        # Create experience nodes
        if candidate_data.get('experience'):
            self.neo4j_service.create_experience_nodes(candidate_id, candidate_data['experience'])
            
        # Create education nodes
        if candidate_data.get('education'):
            self.neo4j_service.create_education_nodes(candidate_id, candidate_data['education'])"""
main_code = main_code.replace(main_cand_old, main_cand_new)

with open(main_path, 'w') as f:
    f.write(main_code)

# Update neo4j_service.py
neo_path = '/Users/nityam/cv-snap-project/backend/neo4j_service.py'
with open(neo_path, 'r') as f:
    neo_code = f.read()

link_reqs_end = """                except Exception as e:
                    logger.error(f"Error linking requirement {skill_name} to job {job_id}: {str(e)}")
            
            logger.info(f"Linked {linked_count} required skills to job {job_id}")"""

link_pref_methods = """                except Exception as e:
                    logger.error(f"Error linking requirement {skill_name} to job {job_id}: {str(e)}")
            
            logger.info(f"Linked {linked_count} required skills to job {job_id}")

    def link_job_preferred_skills(self, job_id: str, preferred_skills: List[Dict[str, Any]]):
        if not preferred_skills: return
        with self.driver.session() as session:
            linked = 0
            for skill in preferred_skills:
                sname = self.normalize_skill_name(skill.get('name', ''))
                if not sname: continue
                query = '''MATCH (j:Job {id: $job_id}) MATCH (s:Skill {name: $sname})
                           MERGE (j)-[r:PREFERS_SKILL]->(s)
                           ON CREATE SET r.importance = $imp, r.min_years = $my
                           ON MATCH SET r.importance = $imp, r.min_years = $my'''
                try:
                    session.run(query, job_id=job_id, sname=sname, imp=skill.get('importance', 4), my=skill.get('min_years', 0))
                    linked += 1
                except Exception as e: pass
            logger.info(f"Linked {linked} preferred skills")
"""
neo_code = neo_code.replace(link_reqs_end, link_pref_methods)


exp_end = """                except Exception as e:
                    logger.error(f"Error linking experience {exp_id} to candidate {candidate_id}: {str(e)}")
            
            logger.info(f"Linked {linked_count} experiences to {candidate_id}")"""

edu_methods = """                except Exception as e:
                    logger.error(f"Error linking experience {exp_id} to candidate {candidate_id}: {str(e)}")
            
            logger.info(f"Linked {linked_count} experiences to {candidate_id}")

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
neo_code = neo_code.replace(exp_end, edu_methods)

# Replace scoring method signature and add queries in calculate_candidate_job_match
calc_old = """                # Calculate scores
                scores = self._calculate_detailed_scores(
                    skill_matches, all_required, candidate_total_years,
                    job_min_years=job_min_years,
                    job_experience_level=job_experience_level
                )"""
calc_new = """                # Get preferred matches
                pref_query = "MATCH (c:Candidate {id: $candidate_id})-[ch:HAS_SKILL]->(s:Skill)<-[jp:PREFERS_SKILL]-(j:Job {id: $job_id}) RETURN s.name as skill, coalesce(ch.proficiency, 1) as candidate_proficiency, coalesce(jp.importance, 4) as job_importance"
                pref_matches = session.run(pref_query, candidate_id=candidate_id, job_id=job_id).data()
                
                # Get education
                edu_query = "MATCH (c:Candidate {id: $candidate_id})-[:HAS_EDUCATION]->(ed:Education) RETURN ed.degree as degree, ed.field as field"
                cand_edu = session.run(edu_query, candidate_id=candidate_id).data()
                
                # Calculate scores
                scores = self._calculate_detailed_scores(
                    skill_matches, all_required, candidate_total_years,
                    job_min_years=job_min_years,
                    job_experience_level=job_experience_level,
                    preferred_matches=pref_matches,
                    candidate_education=cand_edu
                )"""
neo_code = neo_code.replace(calc_old, calc_new)

ret_old = """                    'matched_skill_names': [m['skill'] for m in skill_matches],
                    'missing_skill_names': scores['breakdown'].get('missing_critical_skills', []),
                    'score_breakdown': scores['breakdown']
                }"""
ret_new = """                    'matched_skill_names': [m['skill'] for m in skill_matches],
                    'missing_skill_names': scores['breakdown'].get('missing_critical_skills', []),
                    'preferred_skills_matched': [m['skill'] for m in (pref_matches or [])],
                    'score_breakdown': scores['breakdown']
                }"""
neo_code = neo_code.replace(ret_old, ret_new)

def_old = """    def _calculate_detailed_scores(self, skill_matches, all_required, candidate_total_years,
                                    job_min_years=0, job_experience_level='mid'):"""
def_new = """    def _calculate_detailed_scores(self, skill_matches, all_required, candidate_total_years,
                                    job_min_years=0, job_experience_level='mid',
                                    preferred_matches=None, candidate_education=None):"""
neo_code = neo_code.replace(def_old, def_new)

bonus_old = """        bonus_score = min(bonus_score, 10)
        
        final_score = coverage_score + quality_score + experience_score + critical_score + bonus_score"""
bonus_new = """        if preferred_matches:
            pref_count = len(preferred_matches)
            if pref_count >= 4: bonus_score += 3
            elif pref_count >= 2: bonus_score += 2
            elif pref_count >= 1: bonus_score += 1
            
        edu_bonus = 0
        if candidate_education:
            relevant_fields = {'computer science','computer engineering','software engineering','information technology','data science','electrical engineering','electronics','mathematics','statistics','it','cs','ece','eee','mca','bca'}
            degree_scores = {'phd':3, 'doctorate':3, 'master':2, 'mtech':2, 'm.tech':2, 'ms':2, 'mca':2, 'bachelor':1, 'btech':1, 'b.tech':1, 'bs':1, 'be':1, 'bca':1, 'bsc':1}
            for edu in candidate_education:
                f_low = str(edu.get('field', '')).lower()
                d_low = str(edu.get('degree', '')).lower()
                f_rel = any(rf in f_low for rf in relevant_fields)
                d_level = 0
                for k,v in degree_scores.items():
                    if k in d_low:
                        d_level = v; break
                if f_rel: edu_bonus = max(edu_bonus, d_level)
                elif d_level > 0: edu_bonus = max(edu_bonus, 1)
            bonus_score += min(edu_bonus, 3)
            
        bonus_score = min(bonus_score, 10)
        
        final_score = coverage_score + quality_score + experience_score + critical_score + bonus_score"""
neo_code = neo_code.replace(bonus_old, bonus_new)

bd_old = """                'bonus_score': round(bonus_score, 1),
                'matched_skills': matched_count,"""
bd_new = """                'bonus_score': round(bonus_score, 1),
                'preferred_skills_matched': len(preferred_matches) if preferred_matches else 0,
                'education_bonus': min(edu_bonus, 3) if candidate_education else 0,
                'matched_skills': matched_count,"""
neo_code = neo_code.replace(bd_old, bd_new)

with open(neo_path, 'w') as f:
    f.write(neo_code)
print("Phase 3 applied successfully!")
