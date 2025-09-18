import React, { useState } from "react";
import styled from "styled-components";
import {
  Search,
  CheckSquare,
  Square,
  Settings,
  Brain,
  Zap,
} from "lucide-react";

const FormContainer = styled.div`
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 15px;
  // border: 1px solid #e9ecef;
  // box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  // position: sticky;
  // top: 20px;
  // height: 80%;
  // max-height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const FormTitle = styled.h3`
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0px;
  margin-bottom: 0px;
  color: #2c3e50;
  font-size: 1.1rem;
  font-weight: 600;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
`;

const Label = styled.label`
  font-weight: 500;
  color: #495057;
  font-size: 0.9rem;
`;

const TextArea = styled.textarea`
  width: 100%;
  min-height: 80px;
  padding: 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.3s ease;

  &:focus {
    outline: none;
    border-color: #4facfe;
    box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.1);
  }

  &::placeholder {
    color: #6c757d;
  }
`;

const SourcesSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const SourcesGrid = styled.div`
  display: flex;
  flex-direction: row;
  gap: 8px;
`;

const SourceCard = styled.div`
  background: ${(props) =>
    props.selected
      ? "linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%)"
      : "white"};
  border: 2px solid ${(props) => (props.selected ? "#4facfe" : "#e9ecef")};
  border-radius: 8px;
  padding: 10px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    border-color: #4facfe;
    transform: translateY(-1px);
    box-shadow: 0 3px 8px rgba(79, 172, 254, 0.12);
    background: ${(props) =>
      props.selected
        ? "linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%)"
        : "linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%)"};
  }
`;

const SourceHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
`;

const SourceCheckbox = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  color: ${(props) => (props.selected ? "#4facfe" : "#495057")};
  font-size: 0.9rem;
`;

const SourceDescription = styled.p`
  font-size: 0.8rem;
  color: #6c757d;
  margin: 0;
  line-height: 1.3;
`;

const SourceType = styled.span`
  display: inline-block;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 500;
  background: ${(props) => (props.type === "api" ? "#d4edda" : "#fff3cd")};
  color: ${(props) => (props.type === "api" ? "#155724" : "#856404")};
`;

const SettingsSection = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
`;

const NumberInput = styled.input`
  width: 70px;
  padding: 6px 10px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 0.85rem;
  text-align: center;

  &:focus {
    outline: none;
    border-color: #4facfe;
  }
`;

const SubmitButton = styled.button`
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  min-height: 42px;
  width: 100%;
  margin-bottom: 15px;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 6px 15px rgba(79, 172, 254, 0.25);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const ExampleQueries = styled.div`
  // margin-top: 20px;
  padding: 12px;
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border-radius: 8px;
  border-left: 3px solid #4facfe;
  box-shadow: 0 2px 6px rgba(79, 172, 254, 0.08);
`;

const ExampleTitle = styled.h4`
  margin: 0 0 8px 0;
  color: #4facfe;
  font-size: 0.85rem;
  font-weight: 600;
`;

const ExampleList = styled.ul`
  margin: 0;
  padding-left: 16px;
  color: #2c5aa0;
`;

const ExampleItem = styled.li`
  font-size: 0.8rem;
  margin-bottom: 4px;
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
`;

// Fixed header section
const FormHeader = styled.div`
  padding: 10px 8px 0px 15px;
  // border-bottom: 1px solid #e9ecef;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 15px 15px 0 0;
  flex-shrink: 0;
`;

const FormTitleContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0px;
`;

// Scrollable form content section
const FormContent = styled.div`
  flex: 1;
  padding: 15px;
  padding-right: 8px;
  overflow-y: auto;
  min-height: 0;
  border-radius: 0 0 15px 15px;
  border-bottom: 1px solid #e9ecef;
  &::-webkit-scrollbar {
    width: 3px;
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

// Fixed footer section
const FormFooter = styled.div`
  padding: 0px 8px 30px 15px;
  // border-top: 1px solid #e9ecef;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  flex-shrink: 0;
`;

const CompactToggleContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 15px;
  border: 1px solid #e9ecef;
`;

const CompactToggleOption = styled.div`
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 3px 6px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: ${(props) => (props.active ? "#4facfe" : "transparent")};
  color: ${(props) => (props.active ? "white" : "#6c757d")};
  font-size: 0.75rem;
  font-weight: ${(props) => (props.active ? "600" : "500")};

  &:hover {
    background: ${(props) => (props.active ? "#4facfe" : "#e3f2fd")};
    color: ${(props) => (props.active ? "white" : "#4facfe")};
  }
`;

function QueryForm({ onSubmit, availableSources, loading }) {
  const [formData, setFormData] = useState({
    query: "",
    sources: ["pubmed", "uniprot", "swissadme"],
    maxResults: 10,
    processingMode: "ai", // "ai" or "direct"
  });

  const exampleQueries = [
    "COVID-19 vaccine efficacy",
    "Insulin resistance diabetes",
    "Cancer immunotherapy",
    "Alzheimer's disease biomarkers",
    "CRISPR gene editing",
  ];

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSourceToggle = (source) => {
    setFormData((prev) => ({
      ...prev,
      sources: prev.sources.includes(source)
        ? prev.sources.filter((s) => s !== source)
        : [...prev.sources, source],
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.query.trim() && formData.sources.length > 0) {
      onSubmit(formData);
    }
  };

  const handleExampleClick = (example) => {
    setFormData((prev) => ({
      ...prev,
      query: example,
    }));
  };

  const handleProcessingModeChange = (mode) => {
    setFormData((prev) => ({
      ...prev,
      processingMode: mode,
    }));
  };

  return (
    <FormContainer>
      {/* Fixed Header - Processing Status */}
      <FormHeader>
        <FormTitleContainer>
          <FormTitle>
            <Search size={16} />
            Research Query
          </FormTitle>
          <CompactToggleContainer>
            <CompactToggleOption
              active={formData.processingMode === "ai"}
              onClick={() => handleProcessingModeChange("ai")}
            >
              <Brain size={12} />
              AI
            </CompactToggleOption>
            <CompactToggleOption
              active={formData.processingMode === "direct"}
              onClick={() => handleProcessingModeChange("direct")}
            >
              <Zap size={12} />
              Direct
            </CompactToggleOption>
          </CompactToggleContainer>
        </FormTitleContainer>
      </FormHeader>

      {/* Scrollable Content - Form Details */}
      <FormContent>
        <Form onSubmit={handleSubmit}>
          <InputGroup>
            <TextArea
              id="query"
              value={formData.query}
              onChange={(e) => handleInputChange("query", e.target.value)}
              placeholder="Describe what you're looking for... (e.g., 'COVID-19 vaccine efficacy studies')"
              required
            />
          </InputGroup>

          <SourcesSection>
            <Label>
              <Settings size={14} style={{ marginRight: "6px" }} />
              Select Data Sources:
            </Label>
            <SourcesGrid>
              {availableSources.map((source) => (
                <SourceCard
                  key={source.name}
                  selected={formData.sources.includes(source.name)}
                  onClick={() => handleSourceToggle(source.name)}
                >
                  <SourceHeader>
                    <SourceCheckbox
                      selected={formData.sources.includes(source.name)}
                    >
                      {formData.sources.includes(source.name) ? (
                        <CheckSquare size={14} />
                      ) : (
                        <Square size={14} />
                      )}
                      {source.name.toUpperCase()}
                    </SourceCheckbox>
                  </SourceHeader>
                  <SourceType type={source.type}>
                    {source.type.toUpperCase()}
                  </SourceType>
                  <SourceDescription>{source.description}</SourceDescription>
                </SourceCard>
              ))}
            </SourcesGrid>
          </SourcesSection>

          <SettingsSection>
            <Label htmlFor="maxResults">Max Results per Source:</Label>
            <NumberInput
              id="maxResults"
              type="number"
              min="1"
              max="50"
              value={formData.maxResults}
              onChange={(e) =>
                handleInputChange("maxResults", parseInt(e.target.value))
              }
            />
          </SettingsSection>
        </Form>
      </FormContent>

      {/* Fixed Footer - Submit Button */}
      <FormFooter>
        <SubmitButton
          type="submit"
          disabled={
            loading || !formData.query.trim() || formData.sources.length === 0
          }
          onClick={handleSubmit}
        >
          <Search size={16} />
          {loading ? "Processing..." : "Search Biomedical Databases"}
        </SubmitButton>
        <ExampleQueries>
          <ExampleTitle>💡 Example Queries:</ExampleTitle>
          <ExampleList>
            {exampleQueries.map((example, index) => (
              <ExampleItem
                key={index}
                onClick={() => handleExampleClick(example)}
              >
                {example}
              </ExampleItem>
            ))}
          </ExampleList>
        </ExampleQueries>
      </FormFooter>
    </FormContainer>
  );
}

export default QueryForm;
