import requests
import os
import json

url = "http://localhost:8000/analyze"
job_desc = """Junior Python Developer

Experience: 1–3 Years
Employment Type: Full-time
Department: Engineering / Software Development
Location: Hybrid / On-site / Remote

About the Role
We are looking for a motivated Junior Python Developer with 1–3 years of experience to join our engineering team. The ideal candidate should have a strong foundation in Python programming, backend development, APIs, databases, and software development practices.

You will work closely with senior developers to develop, test, maintain, and improve scalable applications while gaining hands-on experience with modern backend technologies.

Key Responsibilities
* Develop, maintain, and enhance backend applications using Python.
* Build and integrate RESTful APIs and backend services.
* Work with frameworks such as Django, Flask, or FastAPI.
* Write clean, maintainable, and reusable Python code.
* Design and interact with relational databases such as PostgreSQL or MySQL.
* Write SQL queries and optimize database interactions where required.
* Debug applications, identify issues, and implement effective fixes.
* Write unit tests and participate in code reviews.
* Integrate third-party APIs and external services.
* Work with Git and follow version-control best practices.
* Assist in developing and maintaining CI/CD workflows.
* Collaborate with frontend developers, QA engineers, DevOps engineers, and other team members.
* Participate in Agile/Scrum ceremonies and contribute to sprint planning and technical discussions.
* Learn and adopt new technologies, tools, and development practices as required.

Required Qualifications
* 1–3 years of professional experience in Python development.
* Strong understanding of Python fundamentals, including OOP, data structures, exception handling, and modules.
* Experience with at least one Python web framework such as Django, Flask, or FastAPI.
* Understanding of REST APIs and HTTP concepts.
* Working knowledge of SQL and relational databases such as PostgreSQL or MySQL.
* Familiarity with Git/GitHub or GitLab.
* Understanding of software development lifecycle and debugging practices.
* Good problem-solving and analytical skills.
* Ability to work effectively in a collaborative development environment.

Good to Have
* Basic knowledge of Docker and containerized applications.
* Familiarity with AWS, Azure, or Google Cloud.
* Experience with Redis, Celery, or background job processing.
* Basic understanding of CI/CD tools such as Jenkins or GitHub Actions.
* Familiarity with Linux/Unix environments.
* Exposure to automated testing using PyTest or unittest.
* Basic understanding of microservices architecture.

Technical Skills
Language: Python
Frameworks: Django, Flask, FastAPI
APIs: REST, JSON, HTTP
Databases: PostgreSQL, MySQL
Version Control: Git, GitHub/GitLab
Testing: PyTest, unittest
DevOps: Docker, CI/CD
Cloud: AWS / Azure / GCP
Methodology: Agile / Scrum"""

files_dir = '/Users/nityam/cv-snap-project/sample_cv'
files = []
open_files = []

for filename in os.listdir(files_dir):
    if filename.endswith('.docx') or filename.endswith('.pdf'):
        f = open(os.path.join(files_dir, filename), 'rb')
        open_files.append(f)
        files.append(('resume_files', (filename, f, 'application/octet-stream')))

data = {'job_description': job_desc}

print("Sending request to backend...")
response = requests.post(url, data=data, files=files)

for f in open_files:
    f.close()

if response.status_code == 200:
    res = response.json()
    print(json.dumps(res, indent=2))
else:
    print(f"Error: {response.status_code}")
    print(response.text)
