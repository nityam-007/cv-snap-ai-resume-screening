# CV.Snap - AI-Powered Resume Screening System

An intelligent resume screening and ranking system that uses AI to analyze job descriptions and candidate resumes, providing explainable match scores and rankings.

## 🚀 Features

- **AI-Powered Analysis**: Uses Groq (Llama 3) and Google Gemini API for fast, semantic understanding of skills and experience
- **Graph Database**: Neo4j for modeling complex candidate-skill-job relationships  
- **Smart Ranking**: Combines semantic analysis with graph-based reasoning for accurate matching
- **Explainable Results**: Natural language explanations for why candidates rank high or low
- **Modern UI**: React-based interface with real-time processing feedback
- **Multi-format Support**: Supports PDF and DOCX resume parsing
- **Batch Processing**: Analyze multiple resumes simultaneously
- **No Keyword Dependence**: Goes beyond simple keyword matching to understand context

## 🛠️ Tech Stack

### Backend
- **Python 3.8+** with FastAPI framework
- **Groq & Google Gemini APIs** for AI-powered text analysis (switchable via config)
- **Neo4j Graph Database** for relationship modeling
- **PyPDF2 & python-docx** for document parsing
- **Pydantic** for data validation

### Frontend
- **React 19** with TypeScript
- **Vite** for lightning-fast build and development
- **Tailwind CSS v4** for modern utility-first styling
- **HeroUI v3** for accessible, headless interactive components
- **Phosphor Icons** for clean, minimal iconography
- **File upload** with drag-and-drop support
- **Light/Dark Mode** with system preference detection

### Database
- **Neo4j** for storing candidate-skill-job relationships
- **Graph queries** for intelligent matching algorithms

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Neo4j Desktop
- Groq API Key ([Get one here](https://console.groq.com/keys)) or Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/nityam-007/cv-snap-ai-resume-screening.git
cd cv-snap-ai-resume-screening
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv cv_snap_env

# Activate virtual environment
# On macOS/Linux:
source cv_snap_env/bin/activate
# On Windows:
# cv_snap_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your configuration/keys:
# AI_PROVIDER=groq
# GROQ_API_KEY=your_groq_api_key_here
# GOOGLE_API_KEY=your_gemini_api_key_here
# NEO4J_PASSWORD=your_neo4j_password
```

### 4. Neo4j Database Setup

1. Download and install [Neo4j Desktop](https://neo4j.com/download/)
2. Create a new project called "CV Snap"
3. Create a new database with password matching your .env file
4. Start the database (it should show "Active" status)

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 6. Start the Backend

```bash
cd ../backend
source cv_snap_env/bin/activate  # Activate virtual environment
python main.py
```

### 7. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 💡 How to Use

1. **Enter Job Description**: Paste or type the job requirements, including required skills, experience level, and responsibilities.

2. **Upload Resumes**: Select multiple PDF or DOCX files containing candidate resumes (max 10MB each).

3. **Analyze**: Click "Analyze & Rank Candidates" to start the AI processing.

4. **Review Results**: View ranked candidates with:
   - Match scores (0-100%)
   - Skill coverage percentages  
   - Detailed explanations for each ranking
   - Candidate contact information

5. **Try Sample Data**: Use the "Try Sample Data" button to test the system with demo data.

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check and welcome message |
| GET | `/health` | System status (API, Neo4j, Gemini) |
| POST | `/analyze` | Main resume analysis endpoint |
| POST | `/analyze-sample` | Load sample data for testing |
| DELETE | `/clear-database` | Clear all data (debug mode only) |

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  React Frontend │    │  FastAPI Backend │    │  Neo4j Database │
│                 │────│                  │────│                 │
│ • File Upload   │    │ • AI Processing  │    │ • Graph Storage │
│ • Results UI    │    │ • Gemini API     │    │ • Relationships │
│ • Explanations  │    │ • Scoring Logic  │    │ • Match Queries │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Groq/Gemini API │
                       │                 │
                       │ • Skill Extract │
                       │ • Semantic NLP  │ 
                       │ • Explanations  │
                       └─────────────────┘
```

## 🔍 How It Works

1. **Document Parsing**: Extracts text from PDF/DOCX files using specialized libraries
2. **AI Analysis**: Gemini API analyzes job descriptions and resumes to identify skills, experience, and qualifications
3. **Graph Modeling**: Creates relationships between candidates, skills, and job requirements in Neo4j
4. **Intelligent Scoring**: Combines semantic similarity with graph-based reasoning for accurate matching
5. **Explanation Generation**: AI generates human-readable explanations for each candidate's ranking

## 🎯 What Makes CV.Snap Different

- **Beyond Keywords**: Uses semantic understanding instead of simple keyword matching
- **Explainable AI**: Every ranking comes with clear reasons
- **Graph Intelligence**: Models complex relationships between skills and experience
- **Real-world Ready**: Built for actual recruiting workflows, not just research

## 🛠️ Development

### Project Structure

```
cv-snap-ai-resume-screening/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── file_parser.py         # PDF/DOCX parsing
│   ├── gemini_service.py      # AI integration
│   ├── neo4j_service.py       # Database operations
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Main React component
│   │   ├── App.css            # Styles
│   │   └── services/          # API services
│   ├── package.json           # Node dependencies
│   └── public/                # Static assets
└── README.md
```

### Running in Development Mode

```bash
# Terminal 1: Start Neo4j database (using Neo4j Desktop or Docker)

# Terminal 2: Backend
cd backend
source .venv/bin/activate  # Activate virtual environment (if named .venv)
python main.py             # Or run via uvicorn: uvicorn main:app --reload

# Terminal 3: Frontend
cd frontend  
npm run dev
```

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check that virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure Gemini API key is valid in `.env` file

**Neo4j connection failed:**
- Start Neo4j database in Neo4j Desktop
- Check database credentials in `.env` file
- Verify Neo4j is running on default port 7687

**Frontend build errors:**
- Clear npm cache: `npm cache clean --force`
- Reinstall dependencies: `rm -rf node_modules && npm install`

**File upload issues:**
- Check file size (max 10MB per file)
- Ensure files are PDF or DOCX format
- Verify backend is running and accessible

## 📊 Sample Data

The system includes sample data for testing:
- Sample job description for a Senior Python Developer role
- Mock candidate profiles with varying skill levels
- Demonstrates ranking and explanation capabilities

## 🔒 Security

- API keys stored in environment variables (never committed to git)
- File uploads validated for type and size
- Input sanitization for all user data
- CORS protection configured for frontend domain

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit with descriptive messages: `git commit -am 'Add new feature'`
5. Push to your branch: `git push origin feature-name`
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini API** for advanced AI text analysis capabilities
- **Neo4j** for powerful graph database functionality
- **FastAPI** for the robust and fast web framework
- **React** for the modern frontend framework

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the [Issues](https://github.com/nityam-007/cv-snap-ai-resume-screening/issues) page
3. Create a new issue with detailed description and error logs

---

**Built with ❤️ for making recruitment smarter and fairer**
