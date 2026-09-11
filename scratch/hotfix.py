import re

# 1. Fix neo4j_service.py
neo_path = '/Users/nityam/cv-snap-project/backend/neo4j_service.py'
with open(neo_path, 'r') as f:
    neo_code = f.read()

if "SequenceMatcher" not in neo_code[:500]:
    neo_code = neo_code.replace("import logging\n", "import logging\nfrom difflib import SequenceMatcher\n")

with open(neo_path, 'w') as f:
    f.write(neo_code)


# 2. Fix gemini_service.py
gem_path = '/Users/nityam/cv-snap-project/backend/gemini_service.py'
with open(gem_path, 'r') as f:
    gem_code = f.read()

gem_code = gem_code.replace('GEMINI_MODEL = "gemini-2.5-flash"', 'GEMINI_MODEL = "gemini-3.6-flash"')
gem_code = gem_code.replace('gemini-1.5-flash', 'gemini-3.6-flash') # just in case

fallback_old = "def _generate_fallback_explanation(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:"
fallback_new = "def _generate_fallback_explanation(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any], match_analysis: Dict[str, Any] = None) -> str:"
gem_code = gem_code.replace(fallback_old, fallback_new)

# Some previous fallbacks might take 2 args, some take 3. Let's just use *args, **kwargs
gem_code = re.sub(r'def _generate_fallback_explanation\(self, (.*?)\) -> str:', r'def _generate_fallback_explanation(self, *args, **kwargs) -> str:', gem_code)


with open(gem_path, 'w') as f:
    f.write(gem_code)

print("Hotfix applied!")
