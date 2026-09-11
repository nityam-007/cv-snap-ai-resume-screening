import pytest
from neo4j_service import Neo4jService

class TestSkillNormalization:
    @pytest.fixture
    def service(self):
        return object.__new__(Neo4jService)
        
    def test_react_variants(self, service):
        variants = ["React", "ReactJS", "react.js", "react js", "react"]
        for v in variants:
            assert service.normalize_skill_name(v) == "react.js"
            
    def test_node_variants(self, service):
        variants = ["Node", "NodeJS", "node.js", "node js"]
        for v in variants:
            assert service.normalize_skill_name(v) == "node.js"
            
    def test_python_variants(self, service):
        variants = ["Python", "Python3", "py"]
        for v in variants:
            assert service.normalize_skill_name(v) == "python"
            
    def test_database_variants(self, service):
        assert service.normalize_skill_name("PostgreSQL") == "postgresql"
        assert service.normalize_skill_name("Postgres") == "postgresql"
        assert service.normalize_skill_name("MongoDB") == "mongodb"
        assert service.normalize_skill_name("Mongo") == "mongodb"
        
    def test_cloud_variants(self, service):
        assert service.normalize_skill_name("Amazon Web Services") == "aws"
        assert service.normalize_skill_name("AWS") == "aws"
        assert service.normalize_skill_name("Google Cloud Platform") == "gcp"
        assert service.normalize_skill_name("K8s") == "kubernetes"
        
    def test_unknown_skill(self, service):
        assert service.normalize_skill_name("SomeNewFramework") == "somenewframework"
        
    def test_empty(self, service):
        assert service.normalize_skill_name("") == ""
        assert service.normalize_skill_name(None) == ""

class TestScoringDifferentiation:
    @pytest.fixture
    def service(self):
        return object.__new__(Neo4jService)
        
    def _make_skill_match(self, skill, prof, years, imp, req_years):
        return {
            'skill': skill, 'candidate_proficiency': prof, 'candidate_years': years,
            'job_importance': imp, 'required_years': req_years
        }
        
    def _make_required(self, skill, imp, req=True):
        return {'skill': skill, 'importance': imp, 'is_required': req, 'required_years': 2}
        
    def test_perfect_candidate(self, service):
        reqs = [self._make_required(f"s{i}", 10) for i in range(6)]
        matches = [self._make_skill_match(f"s{i}", 8, 5, 10, 5) for i in range(6)]
        score = service._calculate_detailed_scores(matches, reqs, 5, 5, 'mid')
        assert score['final_score'] >= 80
        
    def test_no_skills(self, service):
        reqs = [self._make_required(f"s{i}", 10) for i in range(4)]
        score = service._calculate_detailed_scores([], reqs, 2, 5, 'mid')
        assert score['final_score'] <= 15
        
    def test_half_skills(self, service):
        reqs = [self._make_required(f"s{i}", 10) for i in range(6)]
        matches = [self._make_skill_match(f"s{i}", 5, 3, 10, 3) for i in range(3)]
        score = service._calculate_detailed_scores(matches, reqs, 3, 3, 'mid')
        assert 30 <= score['final_score'] <= 65
        
    def test_different_scores(self, service):
        reqs = [self._make_required(f"s{i}", 8) for i in range(6)]
        m_a = [self._make_skill_match(f"s{i}", 8, 8, 8, 5) for i in range(5)]
        s_a = service._calculate_detailed_scores(m_a, reqs, 8, 5, 'mid')
        
        m_b = [self._make_skill_match(f"s{i}", 4, 2, 8, 5) for i in range(2)]
        s_b = service._calculate_detailed_scores(m_b, reqs, 2, 5, 'mid')
        
        assert s_a['final_score'] - s_b['final_score'] >= 20
        
    def test_adaptive_experience(self, service):
        reqs = [self._make_required("python", 10)]
        m = [self._make_skill_match("python", 7, 3, 10, 2)]
        
        # Junior job
        s_jun = service._calculate_detailed_scores(m, reqs, 3, 2, 'junior')
        # Senior job
        m_sen = [self._make_skill_match("python", 7, 3, 10, 8)]
        s_sen = service._calculate_detailed_scores(m_sen, reqs, 3, 8, 'senior')
        
        assert s_jun['final_score'] > s_sen['final_score']

class TestFuzzyMatching:
    @pytest.fixture
    def service(self):
        return object.__new__(Neo4jService)
        
    def test_close(self, service):
        assert service._find_fuzzy_skill_match("react", ["react.js", "node.js", "python"]) == "react.js"
        
    def test_no_match(self, service):
        assert service._find_fuzzy_skill_match("python", ["react.js", "node.js", "docker"]) is None
        
    def test_word_overlap(self, service):
        assert service._find_fuzzy_skill_match("machine learning", ["machine-learning", "deep-learning", "python"]) == "machine-learning"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
