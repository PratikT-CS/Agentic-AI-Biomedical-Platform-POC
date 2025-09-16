import React, { useState } from "react";
import styled from "styled-components";
import {
  Database,
  FileText,
  Dna,
  Pill,
  Brain,
  ExternalLink,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import JsonView from "@uiw/react-json-view";

const ResultsContainer = styled.div`
  background: white;
  border-radius: 20px;
  border: 1px solid #e9ecef;
  overflow: hidden;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const ResultsHeader = styled.div`
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
`;

const ResultsTitle = styled.h3`
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
`;

const ResultsBody = styled.div`
  padding: 20px;
  flex: 1;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
  }
`;

const SummarySection = styled.div`
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 15px;
  padding: 15px;
  margin-bottom: 15px;
  border: 1px solid #dee2e6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
`;

const SummaryGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
`;

const SummaryCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e9ecef;
  transition: transform 0.3s ease, box-shadow 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
  }
`;

const SummaryNumber = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: #4facfe;
  margin-bottom: 5px;
`;

const SummaryLabel = styled.div`
  font-size: 0.9rem;
  color: #6c757d;
  font-weight: 500;
`;

const SourcesSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const SourceCard = styled.div`
  border: 1px solid #e9ecef;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  }
`;

const SourceHeader = styled.div`
  background: ${(props) => {
    switch (props.source) {
      case "pubmed":
        return "linear-gradient(135deg, #007bff 0%, #0056b3 100%)";
      case "uniprot":
        return "linear-gradient(135deg, #28a745 0%, #1e7e34 100%)";
      case "swissadme":
        return "linear-gradient(135deg, #fd7e14 0%, #e55100 100%)";
      default:
        return "linear-gradient(135deg, #6c757d 0%, #495057 100%)";
    }
  }};
  color: white;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
`;

const SourceInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const SourceIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
`;

const SourceDetails = styled.div`
  display: flex;
  flex-direction: column;
`;

const SourceName = styled.h4`
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
`;

const SourceCount = styled.span`
  font-size: 0.9rem;
  opacity: 0.9;
`;

const ExpandButton = styled.button`
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: background-color 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`;

const SourceContent = styled.div`
  padding: 20px;
  background: white;
  max-height: ${(props) => (props.expanded ? "none" : "0")};
  overflow: hidden;
  transition: max-height 0.3s ease;
`;

const ResultsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const ResultItem = styled.div`
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 18px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }
`;

const ResultTitle = styled.h5`
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
`;

const ResultMeta = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
`;

const MetaTag = styled.span`
  background: #e9ecef;
  color: #495057;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
`;

const ResultDescription = styled.p`
  margin: 0 0 10px 0;
  color: #6c757d;
  font-size: 0.9rem;
  line-height: 1.4;
`;

const ResultLink = styled.a`
  color: #4facfe;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 5px;

  &:hover {
    text-decoration: underline;
  }
`;

const AIAnalysisSection = styled.div`
  background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%);
  color: white;
  border-radius: 10px;
  padding: 20px;
  margin-top: 20px;
`;

const AIAnalysisTitle = styled.h4`
  margin: 0 0 15px 0;
  font-size: 1.2rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const AIAnalysisContent = styled.div`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 15px;
  font-size: 0.95rem;
  line-height: 1.5;
`;

const ErrorMessage = styled.div`
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  padding: 15px;
  margin: 10px 0;
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 40px;
  color: #6c757d;
  font-style: italic;
`;

// SwissADME specific styled components
const SwissADMEContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const SwissADMESection = styled.div`
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #dee2e6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
`;

const SwissADMESectionTitle = styled.h4`
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SwissADMEGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
`;

const SwissADMEPropertyCard = styled.div`
  background: white;
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #e9ecef;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
`;

const SwissADMEPropertyName = styled.div`
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 500;
  margin-bottom: 5px;
  line-height: 1.3;
`;

const SwissADMEPropertyValue = styled.div`
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 600;
  word-break: break-word;
`;

const SwissADMESmilesCard = styled.div`
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);
`;

const SwissADMESmilesTitle = styled.h5`
  margin: 0 0 10px 0;
  font-size: 1rem;
  font-weight: 600;
`;

const SwissADMESmilesValue = styled.div`
  font-family: "Courier New", monospace;
  font-size: 1.1rem;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.1);
  padding: 10px;
  border-radius: 6px;
  word-break: break-all;
`;

function ResultsView({ results, status }) {
  const [expandedSources, setExpandedSources] = useState({});

  const toggleSource = (source) => {
    setExpandedSources((prev) => ({
      ...prev,
      [source]: !prev[source],
    }));
  };

  const getSourceIcon = (source) => {
    switch (source) {
      case "pubmed":
        return <FileText size={20} />;
      case "uniprot":
        return <Dna size={20} />;
      case "swissadme":
        return <Pill size={20} />;
      default:
        return <Database size={20} />;
    }
  };

  const getSourceDisplayName = (source) => {
    switch (source) {
      case "pubmed":
        return "PubMed Articles";
      case "uniprot":
        return "UniProt Proteins";
      case "swissadme":
        return "SwissADME Drug Properties";
      default:
        return source.toUpperCase();
    }
  };

  const formatPropertyValue = (value) => {
    if (typeof value === "number") {
      return value.toFixed(3);
    }
    if (typeof value === "boolean") {
      return value ? "Yes" : "No";
    }
    return String(value);
  };

  const renderSwissADMEResults = (item) => {
    return (
      <SwissADMEContainer>
        {/* SMILES Display */}
        {item.smiles && (
          <SwissADMESmilesCard>
            <SwissADMESmilesTitle>SMILES Structure</SwissADMESmilesTitle>
            <SwissADMESmilesValue>{item.smiles}</SwissADMESmilesValue>
          </SwissADMESmilesCard>
        )}

        {/* Physicochemical Properties */}
        {item.physicochemical_properties && (
          <SwissADMESection>
            <SwissADMESectionTitle>
              <Pill size={16} />
              Physicochemical Properties
            </SwissADMESectionTitle>
            <SwissADMEGrid>
              {Object.entries(item.physicochemical_properties).map(
                ([key, value]) => (
                  <SwissADMEPropertyCard key={key}>
                    <SwissADMEPropertyName>
                      {key.replace(/_/g, " ").toUpperCase()}
                    </SwissADMEPropertyName>
                    <SwissADMEPropertyValue>
                      {formatPropertyValue(value)}
                    </SwissADMEPropertyValue>
                  </SwissADMEPropertyCard>
                )
              )}
            </SwissADMEGrid>
          </SwissADMESection>
        )}

        {/* Lipophilicity */}
        {item.lipophilicity && (
          <SwissADMESection>
            <SwissADMESectionTitle>
              <Pill size={16} />
              Lipophilicity
            </SwissADMESectionTitle>
            <SwissADMEGrid>
              {Object.entries(item.lipophilicity).map(([key, value]) => (
                <SwissADMEPropertyCard key={key}>
                  <SwissADMEPropertyName>{key}</SwissADMEPropertyName>
                  <SwissADMEPropertyValue>
                    {formatPropertyValue(value)}
                  </SwissADMEPropertyValue>
                </SwissADMEPropertyCard>
              ))}
            </SwissADMEGrid>
          </SwissADMESection>
        )}

        {/* Water Solubility */}
        {item.water_solubility && (
          <SwissADMESection>
            <SwissADMESectionTitle>
              <Pill size={16} />
              Water Solubility
            </SwissADMESectionTitle>
            <SwissADMEGrid>
              {Object.entries(item.water_solubility).map(([key, value]) => (
                <SwissADMEPropertyCard key={key}>
                  <SwissADMEPropertyName>{key}</SwissADMEPropertyName>
                  <SwissADMEPropertyValue>
                    {formatPropertyValue(value)}
                  </SwissADMEPropertyValue>
                </SwissADMEPropertyCard>
              ))}
            </SwissADMEGrid>
          </SwissADMESection>
        )}

        {/* Pharmacokinetics */}
        {item.pharmacokinetics && (
          <SwissADMESection>
            <SwissADMESectionTitle>
              <Brain size={16} />
              Pharmacokinetics
            </SwissADMESectionTitle>
            <SwissADMEGrid>
              {Object.entries(item.pharmacokinetics).map(([key, value]) => (
                <SwissADMEPropertyCard key={key}>
                  <SwissADMEPropertyName>{key}</SwissADMEPropertyName>
                  <SwissADMEPropertyValue>
                    {formatPropertyValue(value)}
                  </SwissADMEPropertyValue>
                </SwissADMEPropertyCard>
              ))}
            </SwissADMEGrid>
          </SwissADMESection>
        )}

        {/* Drug Likeness */}
        {item.druglikeness && (
          <SwissADMESection>
            <SwissADMESectionTitle>
              <Pill size={16} />
              Drug Likeness
            </SwissADMESectionTitle>
            <SwissADMEGrid>
              {Object.entries(item.druglikeness).map(([key, value]) => (
                <SwissADMEPropertyCard key={key}>
                  <SwissADMEPropertyName>{key}</SwissADMEPropertyName>
                  <SwissADMEPropertyValue>
                    {formatPropertyValue(value)}
                  </SwissADMEPropertyValue>
                </SwissADMEPropertyCard>
              ))}
            </SwissADMEGrid>
          </SwissADMESection>
        )}

        {/* Medicinal Chemistry */}
        {item.medicinal_chemistry && (
          <SwissADMESection>
            <SwissADMESectionTitle>
              <Dna size={16} />
              Medicinal Chemistry
            </SwissADMESectionTitle>
            <SwissADMEGrid>
              {Object.entries(item.medicinal_chemistry).map(([key, value]) => (
                <SwissADMEPropertyCard key={key}>
                  <SwissADMEPropertyName>{key}</SwissADMEPropertyName>
                  <SwissADMEPropertyValue>
                    {formatPropertyValue(value)}
                  </SwissADMEPropertyValue>
                </SwissADMEPropertyCard>
              ))}
            </SwissADMEGrid>
          </SwissADMESection>
        )}
      </SwissADMEContainer>
    );
  };

  const renderResultItem = (item, source) => {
    if (source === "pubmed") {
      return (
        <ResultItem key={item.pmid || Math.random()}>
          <ResultTitle>{item.title || "No title available"}</ResultTitle>
          <ResultMeta>
            {item.authors && (
              <MetaTag>Authors: {item.authors.slice(0, 3).join(", ")}</MetaTag>
            )}
            {item.journal && <MetaTag>Journal: {item.journal}</MetaTag>}
            {item.publication_date && (
              <MetaTag>Date: {item.publication_date}</MetaTag>
            )}
            {item.pmid && <MetaTag>PMID: {item.pmid}</MetaTag>}
          </ResultMeta>
          {item.abstract && (
            <ResultDescription>
              {item.abstract.length > 200
                ? `${item.abstract.substring(0, 200)}...`
                : item.abstract}
            </ResultDescription>
          )}
          {item.url && (
            <ResultLink
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <ExternalLink size={14} />
              View Article
            </ResultLink>
          )}
        </ResultItem>
      );
    } else if (source === "uniprot") {
      return (
        <ResultItem key={item.accession || Math.random()}>
          <ResultTitle>{item.protein_name || "Unknown protein"}</ResultTitle>
          <ResultMeta>
            {item.accession && <MetaTag>Accession: {item.accession}</MetaTag>}
            {item.organism && <MetaTag>Organism: {item.organism}</MetaTag>}
            {item.sequence_length && (
              <MetaTag>Length: {item.sequence_length} aa</MetaTag>
            )}
            {item.reviewed && (
              <MetaTag>Reviewed: {item.reviewed ? "Yes" : "No"}</MetaTag>
            )}
          </ResultMeta>
          {item.gene_names && item.gene_names.length > 0 && (
            <ResultDescription>
              <strong>Gene names:</strong> {item.gene_names.join(", ")}
            </ResultDescription>
          )}
          {item.keywords && item.keywords.length > 0 && (
            <ResultDescription>
              <strong>Keywords:</strong> {item.keywords.slice(0, 5).join(", ")}
            </ResultDescription>
          )}
          {item.url && (
            <ResultLink
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <ExternalLink size={14} />
              View Protein
            </ResultLink>
          )}
        </ResultItem>
      );
    } else if (source === "swissadme") {
      return <div key={Math.random()}>{renderSwissADMEResults(item)}</div>;
    }

    return (
      <ResultItem key={Math.random()}>
        <ResultTitle>Result</ResultTitle>
        <ResultDescription>
          <JsonView value={item} collapsed={1} />
        </ResultDescription>
      </ResultItem>
    );
  };

  if (status === "loading") {
    return (
      <ResultsContainer>
        <ResultsHeader>
          <Database size={20} />
          <ResultsTitle>Processing Your Query...</ResultsTitle>
        </ResultsHeader>
        <ResultsBody>
          <LoadingMessage>
            Our AI agent is orchestrating searches across multiple biomedical
            databases. This may take a few moments.
          </LoadingMessage>
        </ResultsBody>
      </ResultsContainer>
    );
  }

  if (status === "error" || !results) {
    return (
      <ResultsContainer>
        <ResultsHeader>
          <Database size={20} />
          <ResultsTitle>Query Failed</ResultsTitle>
        </ResultsHeader>
        <ResultsBody>
          <ErrorMessage>
            There was an error processing your query. Please try again or
            contact support if the problem persists.
          </ErrorMessage>
        </ResultsBody>
      </ResultsContainer>
    );
  }

  const sourcesData = results.results || {};
  const totalResults = Object.values(sourcesData).reduce(
    (total, sourceResults) => {
      if (Array.isArray(sourceResults)) {
        return total + sourceResults.length;
      }
      return total;
    },
    0
  );

  return (
    <ResultsContainer>
      <ResultsHeader>
        <Database size={20} />
        <ResultsTitle>Search Results</ResultsTitle>
      </ResultsHeader>

      <ResultsBody>
        <SummarySection>
          <SummaryGrid>
            <SummaryCard>
              <SummaryNumber>{totalResults}</SummaryNumber>
              <SummaryLabel>Total Results</SummaryLabel>
            </SummaryCard>
            <SummaryCard>
              <SummaryNumber>{Object.keys(sourcesData).length}</SummaryNumber>
              <SummaryLabel>Sources Queried</SummaryLabel>
            </SummaryCard>
            <SummaryCard>
              <SummaryNumber>
                {results.orchestration_method || "N/A"}
              </SummaryNumber>
              <SummaryLabel>Orchestration Method</SummaryLabel>
            </SummaryCard>
          </SummaryGrid>
        </SummarySection>

        <SourcesSection>
          {Object.entries(sourcesData).map(([source, sourceResults]) => {
            if (sourceResults.error) {
              return (
                <SourceCard key={source}>
                  <SourceHeader source={source}>
                    <SourceInfo>
                      <SourceIcon>{getSourceIcon(source)}</SourceIcon>
                      <SourceDetails>
                        <SourceName>{getSourceDisplayName(source)}</SourceName>
                        <SourceCount>Error occurred</SourceCount>
                      </SourceDetails>
                    </SourceInfo>
                  </SourceHeader>
                  <SourceContent expanded={true}>
                    <ErrorMessage>{sourceResults.error}</ErrorMessage>
                  </SourceContent>
                </SourceCard>
              );
            }

            const resultCount = Array.isArray(sourceResults)
              ? sourceResults.length
              : 0;
            const isExpanded = expandedSources[source];

            return (
              <SourceCard key={source}>
                <SourceHeader
                  source={source}
                  onClick={() => toggleSource(source)}
                >
                  <SourceInfo>
                    <SourceIcon>{getSourceIcon(source)}</SourceIcon>
                    <SourceDetails>
                      <SourceName>{getSourceDisplayName(source)}</SourceName>
                      <SourceCount>{resultCount} results found</SourceCount>
                    </SourceDetails>
                  </SourceInfo>
                  <ExpandButton>
                    {isExpanded ? (
                      <ChevronDown size={20} />
                    ) : (
                      <ChevronRight size={20} />
                    )}
                  </ExpandButton>
                </SourceHeader>

                <SourceContent expanded={isExpanded}>
                  {Array.isArray(sourceResults) && sourceResults.length > 0 ? (
                    <ResultsList>
                      {sourceResults.map((item) =>
                        renderResultItem(item, source)
                      )}
                    </ResultsList>
                  ) : (
                    <div
                      style={{
                        textAlign: "center",
                        padding: "20px",
                        color: "#6c757d",
                      }}
                    >
                      No results found for this source.
                    </div>
                  )}
                </SourceContent>
              </SourceCard>
            );
          })}
        </SourcesSection>

        {results.ai_analysis && (
          <AIAnalysisSection>
            <AIAnalysisTitle>
              <Brain size={20} />
              AI Analysis & Synthesis
            </AIAnalysisTitle>
            <AIAnalysisContent>{results.ai_analysis}</AIAnalysisContent>
          </AIAnalysisSection>
        )}
      </ResultsBody>
    </ResultsContainer>
  );
}

export default ResultsView;
