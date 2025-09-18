// Test file for PDF export functionality
import PDFExportService from './pdfExportService';

// Sample test data that mimics the structure from ResultsView
const sampleResults = {
  orchestration_method: "ai_agent",
  results: {
    pubmed: [
      {
        title: "Novel therapeutic approaches for cancer treatment",
        authors: ["Smith, J.", "Johnson, A.", "Brown, M."],
        journal: "Nature Medicine",
        publication_date: "2024-01-15",
        pmid: "12345678",
        abstract: "This study explores innovative therapeutic approaches for cancer treatment, focusing on targeted drug delivery systems and personalized medicine strategies.",
        url: "https://pubmed.ncbi.nlm.nih.gov/12345678/"
      },
      {
        title: "Advances in molecular biology research",
        authors: ["Wilson, K.", "Davis, L."],
        journal: "Science",
        publication_date: "2024-01-10",
        pmid: "87654321",
        abstract: "Recent advances in molecular biology have opened new possibilities for understanding disease mechanisms and developing effective treatments.",
        url: "https://pubmed.ncbi.nlm.nih.gov/87654321/"
      }
    ],
    uniprot: [
      {
        protein_name: "Tumor suppressor protein p53",
        accession: "P04637",
        organism: "Homo sapiens",
        sequence_length: 393,
        reviewed: true,
        gene_names: ["TP53", "P53"],
        keywords: ["tumor suppressor", "DNA binding", "transcription regulation"],
        url: "https://www.uniprot.org/uniprot/P04637"
      }
    ],
    swissadme: [
      {
        smiles: ["CC(=O)OC1=CC=CC=C1C(=O)O", "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"],
        physicochemical_properties: {
          "CC(=O)OC1=CC=CC=C1C(=O)O": {
            molecular_weight: 180.157,
            tpsa: 26.3,
            num_heavy_atoms: 13,
            num_rotatable_bonds: 2
          }
        },
        lipophilicity: {
          "CC(=O)OC1=CC=CC=C1C(=O)O": {
            "log_po/w_(ilogp)": 1.23,
            "log_po/w_(xlogp3)": 1.45
          }
        },
        water_solubility: {
          "CC(=O)OC1=CC=CC=C1C(=O)O": {
            "log_s_(esol)": -1.23,
            "log_s_(ali)": -1.45
          }
        },
        pharmacokinetics: {
          "CC(=O)OC1=CC=CC=C1C(=O)O": {
            "GI_absorption": "High",
            "BBB_permeant": "No"
          }
        },
        druglikeness: {
          "CC(=O)OC1=CC=CC=C1C(=O)O": {
            "Lipinski": "Yes",
            "Ghose": "Yes"
          }
        },
        medicinal_chemistry: {
          "CC(=O)OC1=CC=CC=C1C(=O)O": {
            "PAINS": "0",
            "Brenk": "0"
          }
        }
      }
    ]
  },
  ai_analysis: `# AI Analysis Summary

Based on the comprehensive search across multiple biomedical databases, several key findings emerge:

## **Therapeutic Targets**
The research reveals **novel therapeutic approaches** for cancer treatment, with particular focus on:
- Targeted drug delivery systems
- Personalized medicine strategies
- Tumor suppressor mechanisms

## **Molecular Insights**
The analysis of **p53 protein** (UniProt: P04637) shows:
- Critical role in tumor suppression
- DNA binding and transcription regulation functions
- Potential therapeutic target for cancer treatment

## **Drug Properties**
The SwissADME analysis indicates:
- **Good drug-like properties** for the analyzed compounds
- Favorable absorption characteristics
- Appropriate molecular weight and lipophilicity profiles

## **Clinical Implications**
These findings suggest promising avenues for:
1. **Drug development** targeting cancer pathways
2. **Personalized treatment** strategies
3. **Combination therapy** approaches

*Note: Further experimental validation is recommended for clinical translation.*`
};

// Test function
export const testPDFExport = async () => {
  try {
    console.log('Testing PDF export functionality with UI-matched formatting...');
    
    const pdfService = new PDFExportService();
    await pdfService.generatePDF(sampleResults, 'test-biomedical-results-formatted.pdf');
    
    console.log('✅ PDF export test completed successfully!');
    console.log('📄 PDF should now match the UI formatting exactly');
    return true;
  } catch (error) {
    console.error('❌ PDF export test failed:', error);
    return false;
  }
};

// Export for use in browser console or testing
if (typeof window !== 'undefined') {
  window.testPDFExport = testPDFExport;
  window.sampleResults = sampleResults;
}
