import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { Search, Database, Brain, Download, Activity } from "lucide-react";
import QueryForm from "./components/QueryForm";
import ResultsView from "./components/ResultsView";
import ExportButton from "./components/ExportButton";
import ErrorBoundary from "./components/ErrorBoundary";
import { initializeMessagingErrorHandling } from "./utils/messagingErrorHandler";
import "./App.css";

const AppContainer = styled.div`
  min-height: 100vh;
  // background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background: #5c5470;
  padding: 20px;
`;

const Header = styled.header`
  text-align: center;
  margin-bottom: 40px;
  color: white;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 20px;
`;

const Features = styled.div`
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 40px;
  flex-wrap: wrap;
`;

const Feature = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.1);
  padding: 10px 20px;
  border-radius: 25px;
  backdrop-filter: blur(10px);
  color: white;
  font-weight: 500;
`;

const MainContent = styled.div`
  max-width: 100%;
  margin: 0 auto;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const ContentHeader = styled.div`
  // background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  // padding: 10px;
  color: white;
  margin: 0;
  margin-bottom: 20px;
  text-align: center;
`;

const ContentTitle = styled.h2`
  font-size: 1.6rem;
  // margin-bottom: 10px;
  font-weight: 600;
  margin: 0px;
`;

const ContentDescription = styled.p`
  font-size: 1rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
`;

const ContentBody = styled.div`
  padding: 20px;
  padding-left: 5px;
  display: flex;
  gap: 20px;
  min-height: 600px;
  max-height: calc(100vh - 120px);

  @media (max-width: 1024px) {
    flex-direction: column;
    gap: 20px;
    max-height: none;
  }
`;

const FormSection = styled.div`
  flex: 0 0 35%;
  min-width: 350px;
  position: sticky;
  top: 20px;
  height: fit-content;
  max-height: calc(100vh - 40px);
  overflow-y: auto;

  @media (max-width: 1024px) {
    flex: 1;
    min-width: auto;
    position: static;
    max-height: none;
  }
`;

const ResultsSection = styled.div`
  flex: 1;
  min-width: 0;
  max-height: calc(100vh - 40px);
  overflow-y: auto;

  @media (max-width: 1024px) {
    flex: 1;
    max-height: none;
  }
`;

const StatusBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  margin-left: 15px;
  padding: 10px;
  padding-left: 20px;
  background: #f8f9fa;
  border-radius: 10px;
  border-left: 4px solid
    ${(props) =>
      props.status === "loading"
        ? "#ffc107"
        : props.status === "success"
        ? "#28a745"
        : props.status === "error"
        ? "#dc3545"
        : "#6c757d"};
`;

const StatusText = styled.span`
  font-weight: 500;
  color: ${(props) =>
    props.status === "loading"
      ? "#856404"
      : props.status === "success"
      ? "#155724"
      : props.status === "error"
      ? "#721c24"
      : "#495057"};
`;

const LoadingSpinner = styled.div`
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
`;

function App() {
  const [queryData, setQueryData] = useState({
    query: "",
    sources: ["pubmed", "uniprot", "swissadme"],
    maxResults: 10,
  });

  const [results, setResults] = useState(null);
  const [status, setStatus] = useState("idle"); // idle, loading, success, error
  const [error, setError] = useState(null);
  const [availableSources, setAvailableSources] = useState([]);

  useEffect(() => {
    // Fetch available sources on component mount
    fetchAvailableSources();

    // Initialize messaging error handling
    const cleanupMessagingErrorHandling = initializeMessagingErrorHandling();

    // Cleanup
    return () => {
      cleanupMessagingErrorHandling();
    };
  }, []);

  const fetchAvailableSources = async () => {
    try {
      const response = await fetch("/api/sources");
      const data = await response.json();
      setAvailableSources(data.sources || []);
    } catch (err) {
      console.error("Error fetching sources:", err);
    }
  };

  const handleQuerySubmit = async (formData) => {
    setStatus("loading");
    setError(null);
    setResults(null);

    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
      setStatus("success");
    } catch (err) {
      console.error("Error processing query:", err);
      setError(err.message);
      setStatus("error");
    }
  };

  const handleExport = (format) => {
    if (!results) return;

    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `biomedical-research-results.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <AppContainer>
      <ContentHeader>
        <ContentTitle>🧬 Agentic AI Biomedical Research Platform</ContentTitle>
      </ContentHeader>
      {/* <Header>
        <Title>🧬 Agentic AI Biomedical Research Platform</Title>
      </Header> */}
      {/* <Header>
        <Title>🧬 Agentic AI Biomedical Research Platform</Title>
        <Subtitle>
          Intelligent integration of biomedical data sources with AI
          orchestration
        </Subtitle>

        <Features>
          <Feature>
            <Search size={20} />
            Multi-Source Search
          </Feature>
          <Feature>
            <Database size={20} />
            Data Integration
          </Feature>
          <Feature>
            <Brain size={20} />
            AI Orchestration
          </Feature>
          <Feature>
            <Activity size={20} />
            Real-time Analysis
          </Feature>
        </Features>
      </Header> */}

      <MainContent>
        {/* <ContentHeader>
          <ContentTitle>Biomedical Research Query Interface</ContentTitle>
          <ContentDescription>
            Enter your research query below and select the data sources you want
            to search. Our AI agent will orchestrate the search across multiple
            biomedical databases and provide synthesized results.
          </ContentDescription>
        </ContentHeader> */}

        <ContentBody>
          <FormSection className="slide-in-left">
            <StatusBar status={status}>
              <StatusText status={status}>
                {status === "idle" &&
                  "Ready to process your biomedical research query"}
                {status === "loading" &&
                  (queryData.processingMode === "ai"
                    ? "Processing your query with AI orchestration..."
                    : "Processing your query with direct data retrieval...")}
                {status === "success" && "Query completed successfully!"}
                {status === "error" && `Error: ${error}`}
              </StatusText>
              {status === "loading" && <LoadingSpinner />}
              {status === "success" && results && (
                <ExportButton onExport={handleExport} />
              )}
            </StatusBar>

            <QueryForm
              onSubmit={handleQuerySubmit}
              availableSources={availableSources}
              loading={status === "loading"}
            />
          </FormSection>

          <ResultsSection className="slide-in-right">
            {results && <ResultsView results={results} status={status} />}
            {!results && status === "idle" && (
              <div
                className="fade-in"
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  height: "100%",
                  background:
                    "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
                  borderRadius: "20px",
                  border: "2px dashed #dee2e6",
                  color: "#6c757d",
                  fontSize: "1.1rem",
                  textAlign: "center",
                  padding: "40px",
                  position: "relative",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background:
                      "linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%)",
                    transform: "translateX(-100%)",
                    animation: "shimmer 3s infinite",
                  }}
                ></div>
                <div style={{ position: "relative", zIndex: 1 }}>
                  <div
                    style={{
                      fontSize: "3rem",
                      marginBottom: "20px",
                      animation: "pulse 3s infinite",
                    }}
                  >
                    🔬
                  </div>
                  <div style={{ fontWeight: "500", marginBottom: "10px" }}>
                    Ready for Research
                  </div>
                  <div style={{ fontSize: "0.9rem", opacity: 0.8 }}>
                    Enter your query and select data sources to begin your
                    biomedical research journey
                  </div>
                </div>
              </div>
            )}
            {status === "loading" && (
              <div
                className="fade-in"
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  height: "100%",
                  background:
                    "linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%)",
                  borderRadius: "20px",
                  color: "#856404",
                  fontSize: "1.1rem",
                  textAlign: "center",
                  padding: "40px",
                  position: "relative",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background:
                      "linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.2) 50%, transparent 70%)",
                    transform: "translateX(-100%)",
                    animation: "shimmer 2s infinite",
                  }}
                ></div>
                <div style={{ position: "relative", zIndex: 1 }}>
                  <LoadingSpinner
                    style={{
                      width: "40px",
                      height: "40px",
                      margin: "0 auto 20px auto",
                      borderTopColor: "#856404",
                      animation: "spin 1s linear infinite, pulse 2s infinite",
                    }}
                  />
                  <div style={{ fontWeight: "500", marginBottom: "10px" }}>
                    {queryData.processingMode === "ai"
                      ? "AI Agent Working"
                      : "Direct Processing"}
                  </div>
                  <div style={{ fontSize: "0.9rem", opacity: 0.8 }}>
                    {queryData.processingMode === "ai"
                      ? "Orchestrating searches across biomedical databases..."
                      : "Retrieving data from selected sources..."}
                  </div>
                </div>
              </div>
            )}
          </ResultsSection>
        </ContentBody>
      </MainContent>
    </AppContainer>
  );
}

export default App;
