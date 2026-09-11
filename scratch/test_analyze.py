import requests
import os
import json

url = "http://localhost:8000/analyze"
job_desc = """Senior Backend Engineer / Backend Lead
Experience: 8–12 years
Employment Type: Full-time
Department: Engineering
Location: Hybrid / Remote

About the Role
We are looking for an experienced Senior Backend Engineer / Backend Lead to design, build, and lead the development of highly scalable and reliable backend systems. The ideal candidate will have strong expertise in Java, Spring Boot, microservices, cloud-native architecture, and distributed systems, along with experience leading backend engineering teams.

You will be responsible for architecting backend services, improving system reliability and performance, driving cloud migration initiatives, and mentoring engineers while maintaining high engineering standards.

Key Responsibilities
* Design, develop, and maintain scalable backend services and APIs using Java and Spring Boot.
* Architect and implement microservices-based distributed systems.
* Design highly available and reliable database solutions using PostgreSQL.
* Lead backend architecture and technical decisions for large-scale applications.
* Develop and optimize RESTful APIs and backend services.
* Design systems for high availability, scalability, fault tolerance, and performance.
* Lead and contribute to AWS cloud-native deployments, including ECS, RDS, and Lambda.
* Drive migration of legacy/on-premise systems to cloud infrastructure.
* Build and maintain containerized applications using Docker and Kubernetes.
* Establish and improve CI/CD pipelines and automated deployment processes.
* Identify performance bottlenecks and implement solutions to improve system efficiency and reliability.
* Conduct code reviews and ensure adherence to engineering best practices.
* Collaborate with product managers, frontend engineers, DevOps engineers, and other stakeholders.
* Mentor and guide backend engineers and contribute to team development.
* Work effectively in an Agile/Scrum development environment.

Required Qualifications
* 8+ years of professional software engineering experience.
* Strong proficiency in Java and Spring Boot.
* Hands-on experience building and operating microservices.
* Strong understanding of distributed systems and scalable backend architecture.
* Experience designing and developing production-grade APIs.
* Strong experience with PostgreSQL and relational database systems.
* Practical experience with AWS, particularly ECS, RDS, and Lambda.
* Experience with Docker and Kubernetes.
* Experience designing and maintaining CI/CD pipelines, preferably with Jenkins.
* Strong understanding of software development lifecycle and Agile methodologies.
* Proven experience leading technical initiatives or backend engineering teams.

Preferred Qualifications
* Experience with Node.js and JavaScript-based backend services.
* Experience migrating large-scale applications from on-premise infrastructure to AWS.
* Knowledge of cloud-native architecture and infrastructure best practices.
* Experience with high-availability database architectures.
* Strong problem-solving and system-design skills.
* Excellent communication, collaboration, and technical leadership abilities.

What You’ll Work On
* Backend Architecture: Build reliable, scalable microservices and APIs.
* Cloud Engineering: Design and operate cloud-native workloads on AWS.
* Distributed Systems: Solve complex scalability, reliability, and performance challenges.
* Database Engineering: Build highly available PostgreSQL-based systems.
* DevOps: Improve containerization, CI/CD, and deployment automation.
* Technical Leadership: Mentor engineers and drive engineering best practices.

Core Technology Stack
Languages: Java, Node.js
Frameworks: Spring Boot
Architecture: Microservices, Distributed Systems
Databases: PostgreSQL
Cloud: AWS — ECS, RDS, Lambda
Containers: Docker, Kubernetes
CI/CD: Jenkins
Methodology: Agile"""

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
