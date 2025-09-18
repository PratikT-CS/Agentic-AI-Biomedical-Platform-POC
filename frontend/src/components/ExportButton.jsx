import React, { useState } from "react";
import styled from "styled-components";
import { Download, FileText, FileJson, FileSpreadsheet, FileImage } from "lucide-react";

const ExportContainer = styled.div`
  position: relative;
  display: inline-block;
`;

const ExportButton = styled.button`
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;

  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 6px 8px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;

  &:hover {
    background: linear-gradient(165deg, #28a745 0%, #20c997 100%);
    border-color: rgba(255, 255, 255, 0.5);
  }
`;

const Dropdown = styled.div`
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 180px;
  overflow: hidden;
`;

const DropdownItem = styled.button`
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: white;
  color: #495057;
  text-align: left;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  transition: background-color 0.2s ease;

  &:hover {
    background: #f8f9fa;
  }

  &:not(:last-child) {
    border-bottom: 1px solid #e9ecef;
  }
`;

const IconWrapper = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  color: #6c757d;
`;

function ExportButtonComponent({ onExport }) {
  const [isOpen, setIsOpen] = useState(false);

  const handleExport = (format) => {
    onExport(format);
    setIsOpen(false);
  };

  const exportOptions = [
    {
      format: "pdf",
      label: "Export as PDF",
      icon: <FileImage size={14} />,
      description: "Formatted report with all details",
    },
    {
      format: "json",
      label: "Export as JSON",
      icon: <FileJson size={14} />,
      description: "Structured data format",
    },
    {
      format: "csv",
      label: "Export as CSV",
      icon: <FileSpreadsheet size={14} />,
      description: "Spreadsheet format",
    },
    {
      format: "txt",
      label: "Export as Text",
      icon: <FileText size={14} />,
      description: "Plain text format",
    },
  ];

  return (
    <ExportContainer>
      <ExportButton onClick={() => setIsOpen(!isOpen)}>
        <Download size={14} />
        Export Results
      </ExportButton>

      {isOpen && (
        <>
          <div
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 999,
            }}
            onClick={() => setIsOpen(false)}
          />
          <Dropdown>
            {exportOptions.map((option) => (
              <DropdownItem
                key={option.format}
                onClick={() => handleExport(option.format)}
                title={option.description}
              >
                <IconWrapper>{option.icon}</IconWrapper>
                {option.label}
              </DropdownItem>
            ))}
          </Dropdown>
        </>
      )}
    </ExportContainer>
  );
}

export default ExportButtonComponent;
