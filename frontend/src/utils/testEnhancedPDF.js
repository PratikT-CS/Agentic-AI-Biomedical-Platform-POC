// Test script for enhanced PDF export functionality
import PDFExportService from './pdfExportService.js';

// Enhanced test data that matches the expected structure
const enhancedTestResults = {
  orchestration_method: "ai_agent",
  sources_data: {
    pubmed: [
      {
        title: "Novel therapeutic approaches for cancer treatment using targeted drug delivery systems",
        authors: ["Smith, J.", "Johnson, A.", "Brown, M.", "Davis, K.", "Wilson, P."],
        journal: "Nature Medicine",
        publication_date: "2024-01-15",
        pmid: "12345678",
        abstract: "This comprehensive study explores innovative approaches to cancer treatment through the development of targeted drug delivery systems. The research demonstrates significant improvements in therapeutic efficacy while minimizing systemic toxicity. Our findings suggest that personalized medicine strategies combined with advanced nanotechnology can revolutionize cancer care.",
        url: "https://pubmed.ncbi.nlm.nih.gov/12345678/"
      },
      {
        title: "Molecular mechanisms of tumor suppression: Role of p53 protein in DNA repair",
        authors: ["Garcia, L.", "Martinez, R.", "Lee, S."],
        journal: "Cell",
        publication_date: "2024-02-20",
        pmid: "87654321",
        abstract: "The p53 tumor suppressor protein plays a critical role in maintaining genomic stability through its involvement in DNA repair mechanisms. This study provides new insights into the molecular pathways that regulate p53 activity and their implications for cancer therapy.",
        url: "https://pubmed.ncbi.nlm.nih.gov/87654321/"
      }
    ],
    uniprot: [
      {
        protein_name: "Cellular tumor antigen p53",
        accession: "P04637",
        organism: "Homo sapiens (Human)",
        sequence_length: 393,
        reviewed: true,
        gene_names: ["TP53", "TRP53", "P53"],
        keywords: ["Tumor suppressor", "DNA-binding", "Transcription regulation", "Apoptosis", "Cell cycle"],
        function_description: "Acts as a tumor suppressor in many tumor types; induces growth arrest or apoptosis depending on the physiological circumstances and cell type. Involved in cell cycle regulation as a trans-activator that acts to negatively regulate cell division by controlling a set of genes required for this process.",
        url: "https://www.uniprot.org/uniprot/P04637"
      }
    ],
    swissadme: [
      {
        smiles: ["CC(=O)OC1=CC=CC=C1C(=O)O", "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"],
        boiled_egg_plot: true,
        physicochemical_properties: {
          "CC(=O)OC1=CC=CC=C1C(=O)O": {
            molecular_weight: 180.16,
            log_p: 1.87,
            tpsa: 26.3,
            num_rotatable_bonds: 2,
            num_hbd: 1,
            num_hba: 4
          },
          "CN1C=NC2=C1C(=O)N(C(=O)N2C)C": {
            molecular_weight: 194.19,
            log_p: -0.07,
            tpsa: 61.82,
            num_rotatable_bonds: 0,
            num_hbd: 2,
            num_hba: 4
          }
        },
        lipophilicity: {
          "CC(=O)OC1=CC=CC=C1C(=O)O": {
            log_p: 1.87,
            log_d: 1.87,
            log_s: -1.23
          },
          "CN1C=NC2=C1C(=O)N(C(=O)N2C)C": {
            log_p: -0.07,
            log_d: -0.07,
            log_s: -0.45
          }
        },
        water_solubility: {
          "CC(=O)OC1=CC=CC=C1C(=O)O": {
            log_s: -1.23,
            solubility_class: "Soluble",
            mol_solubility: 0.059
          },
          "CN1C=NC2=C1C(=O)N(C(=O)N2C)C": {
            log_s: -0.45,
            solubility_class: "Very soluble",
            mol_solubility: 0.355
          }
        },
        pharmacokinetics: {
          "CC(=O)OC1=CC=CC=C1C(=O)O": {
            gi_absorption: "High",
            bbb_permeant: "No",
            p_gp_substrate: "No",
            cyp1a2_inhibitor: "No",
            cyp2c19_inhibitor: "No",
            cyp2c9_inhibitor: "No",
            cyp2d6_inhibitor: "No",
            cyp3a4_inhibitor: "No"
          },
          "CN1C=NC2=C1C(=O)N(C(=O)N2C)C": {
            gi_absorption: "High",
            bbb_permeant: "No",
            p_gp_substrate: "No",
            cyp1a2_inhibitor: "No",
            cyp2c19_inhibitor: "No",
            cyp2c9_inhibitor: "No",
            cyp2d6_inhibitor: "No",
            cyp3a4_inhibitor: "No"
          }
        },
        druglikeness: {
          "CC(=O)OC1=CC=CC=C1C(=O)O": {
            lipinski_violations: 0,
            ghose_violations: 0,
            veber_violations: 0,
            egan_violations: 0,
            muegge_violations: 0,
            bioavailability_score: 0.55
          },
          "CN1C=NC2=C1C(=O)N(C(=O)N2C)C": {
            lipinski_violations: 0,
            ghose_violations: 0,
            veber_violations: 0,
            egan_violations: 0,
            muegge_violations: 0,
            bioavailability_score: 0.55
          }
        },
        medicinal_chemistry: {
          "CC(=O)OC1=CC=CC=C1C(=O)O": {
            lead_likeness: "Yes",
            synthetic_accessibility: 1.0,
            drug_score: 0.85
          },
          "CN1C=NC2=C1C(=O)N(C(=O)N2C)C": {
            lead_likeness: "Yes",
            synthetic_accessibility: 1.0,
            drug_score: 0.90
          }
        },
        images: {
          "CC(=O)OC1=CC=CC=C1C(=O)O": ["2d_structure", "3d_structure", "radar_plot"],
          "CN1C=NC2=C1C(=O)N(C(=O)N2C)C": ["2d_structure", "3d_structure", "radar_plot"]
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
export const testEnhancedPDFExport = async () => {
  try {
    console.log('🧪 Testing enhanced PDF export functionality...');
    
    const pdfService = new PDFExportService();
    await pdfService.generatePDF(enhancedTestResults, 'enhanced-biomedical-results.pdf');
    
    console.log('✅ Enhanced PDF export test completed successfully!');
    console.log('📄 PDF should now have:');
    console.log('   • Proper hierarchy for PubMed results with source links');
    console.log('   • Structured UniProt results with detailed information');
    console.log('   • Professional table formatting for SwissADME properties');
    console.log('   • Enhanced AI analysis with markdown parsing');
    console.log('   • Better visual hierarchy and readability');
    return true;
  } catch (error) {
    console.error('❌ Enhanced PDF export test failed:', error);
    return false;
  }
};

// Auto-run test if in browser environment
if (typeof window !== 'undefined') {
  window.testEnhancedPDFExport = testEnhancedPDFExport;
  console.log('Enhanced PDF test function available as window.testEnhancedPDFExport()');
}
