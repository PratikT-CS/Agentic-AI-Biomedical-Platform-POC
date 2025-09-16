# 🧬 Agentic AI-Enabled Biomedical Research Platform

A Proof of Concept (POC) platform that demonstrates the feasibility of integrating multiple biomedical data sources with AI orchestration for intelligent research workflows.

## 🎯 Overview

This platform integrates three major biomedical resources:

- **PubMed** - Biomedical article database (API integration)
- **UniProt** - Protein sequence and functional information (API integration)
- **SwissADME** - Drug properties and ADME predictions (Web scraping)

The platform features an AI agent powered by LangChain and Google Gemini that orchestrates multi-source queries and synthesizes results to provide actionable research insights.

## ✨ Key Features

- **Multi-Source Integration**: Seamlessly query PubMed, UniProt, and SwissADME
- **AI Orchestration**: Intelligent workflow coordination using LangChain
- **No-Code Interface**: User-friendly React frontend for complex queries
- **Data Provenance**: Complete logging and traceability of all queries
- **Real-time Processing**: Fast, responsive search across multiple databases
- **Export Capabilities**: Download results in multiple formats (JSON, CSV, TXT)

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Google Gemini API key (for AI orchestration)
- Chrome browser (for SwissADME web scraping)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd agentic-ai-biomedical-platform
   ```

2. **Set up environment variables**

   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
   ```
   
   **Note**: See [README_GEMINI_SETUP.md](backend/README_GEMINI_SETUP.md) for detailed Gemini API setup instructions.

3. **Build and run with Docker Compose**

   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📖 Usage

### Basic Query Example

1. **Open the web interface** at http://localhost:3000
2. **Enter your research query** (e.g., "COVID-19 vaccine efficacy")
3. **Select data sources** (PubMed, UniProt, SwissADME)
4. **Click "Search Biomedical Databases"**
5. **View synthesized results** with AI analysis
6. **Export results** in your preferred format

### Example Queries

- **Disease Research**: "Alzheimer's disease biomarkers"
- **Drug Discovery**: "cancer immunotherapy targets"
- **Protein Analysis**: "insulin receptor protein"
- **Clinical Studies**: "COVID-19 vaccine efficacy"

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  React Frontend │    │ FastAPI Backend │    │ AI Orchestrator │
│                 │    │                 │    │                 │
│ • Query Form    │◄──►│ • REST API      │◄──►│ • LangChain     │
│ • Results View  │    │ • Workflow Svc  │    │ • Multi-Agent   │
│ • Export Tools  │    │ • Data Logging  │    │ • Synthesis     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │     Data Adapters       │
                    │                         │
                    │ • PubMed Adapter        │
                    │ • UniProt Adapter       │
                    │ • SwissADME Adapter     │
                    └─────────────────────────┘
```

## 🔧 Configuration

### Environment Variables

| Variable         | Description                         | Default                                   |
| ---------------- | ----------------------------------- | ----------------------------------------- |
| `GEMINI_API_KEY` | Google Gemini API key for AI orchestration | Required                                  |
| `DATABASE_URL`   | SQLite database path                | `sqlite:///./data/biomedical_platform.db` |

## 🚧 Limitations & Known Issues

### Current Limitations

- SwissADME requires SMILES notation (drug name conversion not implemented)
- Google Gemini API key required for full AI orchestration
- Web scraping may be affected by SwissADME website changes
- Limited to English language queries

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI
- [Architecture Guide](docs/architecture.md) - Detailed system design
- [Usage Guide](docs/usage.md) - Comprehensive user manual
- [Feasibility Report](docs/feasibility_report.md) - POC findings and recommendations

## 📄 License

This project is licensed under the MIT License.

---

**Note**: This is a Proof of Concept (POC) platform designed to demonstrate feasibility. For production use, additional security, scalability, and reliability measures would be required.
