import jsPDF from 'jspdf';

class PDFExportService {
  constructor() {
    this.doc = null;
    this.currentY = 20;
    this.pageHeight = 280; // A4 page height in mm
    this.margin = 20;
    this.lineHeight = 6;
  }

  // Initialize new PDF document
  initPDF(title = 'Biomedical Research Results') {
    this.doc = new jsPDF('p', 'mm', 'a4');
    this.currentY = 20;
    
    // Add title
    this.doc.setFontSize(20);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text(title, this.margin, this.currentY);
    this.currentY += 15;

    // Add timestamp
    this.doc.setFontSize(10);
    this.doc.setFont('helvetica', 'normal');
    this.doc.text(`Generated on: ${new Date().toLocaleString()}`, this.margin, this.currentY);
    this.currentY += 10;

    this.addHorizontalLine();
  }

  // Add horizontal line separator
  addHorizontalLine() {
    this.doc.setDrawColor(200, 200, 200);
    this.doc.line(this.margin, this.currentY, 190, this.currentY);
    this.currentY += 5;
  }

  // Check if we need a new page
  checkNewPage(requiredSpace = 10) {
    if (this.currentY + requiredSpace > this.pageHeight) {
      this.doc.addPage();
      this.currentY = 20;
      return true;
    }
    return false;
  }

  // Add section header with ResultsView styling
  addSectionHeader(title, fontSize = 14, color = [44, 62, 80]) {
    this.checkNewPage(15);
    this.doc.setFontSize(fontSize);
    this.doc.setFont('helvetica', 'bold');
    this.doc.setTextColor(color[0], color[1], color[2]);
    this.doc.text(title, this.margin, this.currentY);
    this.doc.setTextColor(0, 0, 0); // Reset to black
    this.currentY += 8;
    this.addHorizontalLine();
  }

  // Add text content with proper wrapping
  addText(text, fontSize = 10, isBold = false, indent = 0) {
    if (!text || text === 'undefined' || text === 'null') return;
    
    this.checkNewPage(8);
    this.doc.setFontSize(fontSize);
    this.doc.setFont('helvetica', isBold ? 'bold' : 'normal');
    
    // Handle text wrapping
    const maxWidth = 170 - indent;
    const lines = this.doc.splitTextToSize(String(text), maxWidth);
    
    for (let i = 0; i < lines.length; i++) {
      this.checkNewPage(6);
      this.doc.text(lines[i], this.margin + indent, this.currentY);
      this.currentY += this.lineHeight;
    }
  }

  // Add key-value pair with proper formatting
  addKeyValue(key, value, fontSize = 10, indent = 0) {
    if (!key || (!value && value !== 0 && value !== false)) return;
    
    this.checkNewPage(8);
    this.doc.setFontSize(fontSize);
    this.doc.setFont('helvetica', 'bold');
    
    const keyText = `${key}:`;
    const keyWidth = this.doc.getTextWidth(keyText);
    this.doc.text(keyText, this.margin + indent, this.currentY);
    
    this.doc.setFont('helvetica', 'normal');
    const valueText = String(value);
    const maxValueWidth = 170 - indent - keyWidth - 3;
    const valueLines = this.doc.splitTextToSize(valueText, maxValueWidth);
    
    // First line on same line as key
    if (valueLines.length > 0) {
      this.doc.text(valueLines[0], this.margin + indent + keyWidth + 3, this.currentY);
      this.currentY += this.lineHeight;
      
      // Additional lines indented
      for (let i = 1; i < valueLines.length; i++) {
        this.checkNewPage(6);
        this.doc.text(valueLines[i], this.margin + indent + keyWidth + 3, this.currentY);
        this.currentY += this.lineHeight;
      }
    } else {
      this.currentY += this.lineHeight;
    }
  }

  // Add summary cards with ResultsView styling
  addSummaryCards(summaryData) {
    this.addSectionHeader('Summary Statistics', 14, [79, 172, 254]); // Blue color from ResultsView
    
    const cards = [
      { label: 'Total Results', value: summaryData.totalResults || 0 },
      { label: 'Sources Queried', value: summaryData.sourcesQueried || 0 },
      { label: 'Orchestration Method', value: summaryData.orchestrationMethod || 'N/A' }
    ];

    // Add background box for summary section
    this.doc.setFillColor(248, 249, 250); // Light gray background
    this.doc.rect(this.margin - 5, this.currentY - 5, 180, cards.length * 8 + 10, 'F');
    
    cards.forEach(card => {
      this.doc.setTextColor(79, 172, 254); // Blue color for values
      this.addKeyValue(card.label, card.value, 11);
      this.doc.setTextColor(0, 0, 0); // Reset to black
    });
    this.currentY += 5;
  }

  // Add source data with ResultsView styling
  addSourceData(sourceName, sourceResults) {
    // Get source-specific colors matching ResultsView
    const sourceColors = {
      'pubmed': [0, 123, 255],      // Blue gradient
      'uniprot': [40, 167, 69],     // Green gradient  
      'swissadme': [253, 126, 20],  // Orange gradient
      'default': [108, 117, 125]    // Gray gradient
    };
    
    const sourceKey = sourceName.toLowerCase().includes('pubmed') ? 'pubmed' :
                     sourceName.toLowerCase().includes('uniprot') ? 'uniprot' :
                     sourceName.toLowerCase().includes('swissadme') ? 'swissadme' : 'default';
    
    const color = sourceColors[sourceKey];
    this.addSectionHeader(`${sourceName}`, 12, color);
    
    if (sourceResults && sourceResults.error) {
      // Error styling matching ResultsView
      this.doc.setFillColor(248, 215, 218); // Light red background
      this.doc.rect(this.margin - 2, this.currentY - 2, 174, 12, 'F');
      this.doc.setTextColor(114, 28, 36); // Dark red text
      this.addText(`Error: ${sourceResults.error}`, 10);
      this.doc.setTextColor(0, 0, 0); // Reset to black
      this.currentY += 5;
      return;
    }

    if (!Array.isArray(sourceResults) || sourceResults.length === 0) {
      this.doc.setTextColor(108, 117, 125); // Gray color
      this.addText('No results found for this source.', 10);
      this.doc.setTextColor(0, 0, 0); // Reset to black
      this.currentY += 5;
      return;
    }

    this.doc.setTextColor(color[0], color[1], color[2]);
    this.addText(`Found ${sourceResults.length} results:`, 10, true);
    this.doc.setTextColor(0, 0, 0); // Reset to black
    this.currentY += 3;

    sourceResults.forEach((item, index) => {
      if (item && typeof item === 'object') {
        this.addResultItem(item, sourceName.toLowerCase(), index + 1);
      }
    });
  }

  // Add individual result item with ResultsView styling
  addResultItem(item, source, index) {
    this.checkNewPage(25);
    
    // Add result card background (light gradient effect)
    this.doc.setFillColor(248, 249, 250); // Light gray background
    this.doc.rect(this.margin - 3, this.currentY - 3, 176, 20, 'F');
    
    // Add result number with styling matching ResultsView
    this.doc.setFontSize(11);
    this.doc.setFont('helvetica', 'bold');
    this.doc.setTextColor(44, 62, 80); // Dark blue-gray color from ResultsView
    this.doc.text(`Result ${index}`, this.margin, this.currentY);
    this.doc.setTextColor(0, 0, 0); // Reset to black
    this.currentY += 10;

    // Determine source type from source name or data structure
    if (source.includes('pubmed') || item.pmid || item.abstract) {
      this.addPubMedResult(item);
    } else if (source.includes('uniprot') || item.accession || item.protein_name) {
      this.addUniProtResult(item);
    } else if (source.includes('swissadme') || item.smiles || item.physicochemical_properties) {
      this.addSwissADMEResult(item);
    } else {
      this.addGenericResult(item);
    }

    this.currentY += 8;
  }

  // Add PubMed result
  addPubMedResult(item) {
    // Title
    if (item.title) {
      this.addText(item.title, 11, true);
    }
    
    // Meta information
    const metaItems = [];
    if (item.authors && Array.isArray(item.authors) && item.authors.length > 0) {
      metaItems.push(`Authors: ${item.authors.slice(0, 3).join(", ")}${item.authors.length > 3 ? ' et al.' : ''}`);
    }
    if (item.journal) {
      metaItems.push(`Journal: ${item.journal}`);
    }
    if (item.publication_date) {
      metaItems.push(`Date: ${item.publication_date}`);
    }
    if (item.pmid) {
      metaItems.push(`PMID: ${item.pmid}`);
    }
    
    if (metaItems.length > 0) {
      this.doc.setTextColor(108, 117, 125); // Gray color for meta
      this.addText(metaItems.join(' | '), 9, false, 2);
      this.doc.setTextColor(0, 0, 0); // Reset to black
    }
    
    // Abstract
    if (item.abstract) {
      const abstract = item.abstract.length > 300 
        ? `${item.abstract.substring(0, 300)}...` 
        : item.abstract;
      this.addText(abstract, 9, false, 2);
    }
    
    // URL
    if (item.url) {
      this.doc.setTextColor(79, 172, 254); // Blue color for links
      this.addText(`View Article: ${item.url}`, 8, false, 2);
      this.doc.setTextColor(0, 0, 0);
    }
  }

  // Add UniProt result
  addUniProtResult(item) {
    // Protein name
    if (item.protein_name) {
      this.addText(item.protein_name, 11, true);
    }
    
    // Meta information
    const metaItems = [];
    if (item.accession) {
      metaItems.push(`Accession: ${item.accession}`);
    }
    if (item.organism) {
      metaItems.push(`Organism: ${item.organism}`);
    }
    if (item.sequence_length) {
      metaItems.push(`Length: ${item.sequence_length} aa`);
    }
    if (item.reviewed !== undefined) {
      metaItems.push(`Reviewed: ${item.reviewed ? "Yes" : "No"}`);
    }
    
    if (metaItems.length > 0) {
      this.doc.setTextColor(108, 117, 125);
      this.addText(metaItems.join(' | '), 9, false, 2);
      this.doc.setTextColor(0, 0, 0);
    }
    
    // Gene names
    if (item.gene_names && Array.isArray(item.gene_names) && item.gene_names.length > 0) {
      this.addKeyValue('Gene names', item.gene_names.join(", "), 9, 2);
    }
    
    // Keywords
    if (item.keywords && Array.isArray(item.keywords) && item.keywords.length > 0) {
      this.addKeyValue('Keywords', item.keywords.slice(0, 5).join(", "), 9, 2);
    }
    
    // URL
    if (item.url) {
      this.doc.setTextColor(79, 172, 254);
      this.addText(`View Protein: ${item.url}`, 8, false, 2);
      this.doc.setTextColor(0, 0, 0);
    }
  }

  // Add SwissADME result with ResultsView styling
  addSwissADMEResult(item) {
    const smiles = item.smiles || [];
    const molecules = smiles.length > 0 ? smiles : ["Unknown"];

    // Boiled Egg Plot section with yellow gradient background (matching ResultsView)
    if (item.boiled_egg_plot) {
      this.checkNewPage(15);
      this.doc.setFillColor(255, 243, 205); // Light yellow background
      this.doc.rect(this.margin - 3, this.currentY - 3, 176, 12, 'F');
      this.doc.setTextColor(133, 100, 4); // Orange-brown color
      this.addText('🥚 Boiled Egg Plot (ADME Properties): Available in web interface', 10, true, 2);
      this.doc.setTextColor(0, 0, 0);
      this.currentY += 5;
    }

    // Process each molecule with card-like styling
    molecules.forEach((smile, index) => {
      this.checkNewPage(30);
      
      // Molecule card background (light gray)
      this.doc.setFillColor(248, 249, 250);
      const cardHeight = 25;
      this.doc.rect(this.margin - 3, this.currentY - 3, 176, cardHeight, 'F');
      
      // Molecule header with blue gradient styling
      this.doc.setFillColor(79, 172, 254); // Blue background for header
      this.doc.rect(this.margin - 3, this.currentY - 3, 176, 8, 'F');
      this.doc.setTextColor(255, 255, 255); // White text
      this.addText(`Molecule ${index + 1}`, 10, true, 2);
      this.doc.setTextColor(0, 0, 0); // Reset to black
      this.currentY += 3;
      
      // SMILES string with monospace font and background
      if (smile && smile !== "Unknown") {
        this.doc.setFillColor(233, 236, 239); // Light gray background for SMILES
        this.doc.rect(this.margin + 2, this.currentY - 1, 170, 6, 'F');
        this.doc.setFont('courier', 'normal');
        this.doc.setTextColor(73, 80, 87); // Dark gray text
        this.addText(`SMILES: ${smile}`, 8, false, 4);
        this.doc.setFont('helvetica', 'normal');
        this.doc.setTextColor(0, 0, 0);
      }
      this.currentY += 5;

      // Add property sections with enhanced styling
      this.addMoleculeSection('Physicochemical Properties', item.physicochemical_properties, smile, 4);
      this.addMoleculeSection('Lipophilicity', item.lipophilicity, smile, 4);
      this.addMoleculeSection('Water Solubility', item.water_solubility, smile, 4);
      this.addMoleculeSection('Pharmacokinetics', item.pharmacokinetics, smile, 4);
      this.addMoleculeSection('Drug Likeness', item.druglikeness, smile, 4);
      this.addMoleculeSection('Medicinal Chemistry', item.medicinal_chemistry, smile, 4);

      // Images note with gray styling
      if (item.images && item.images[smile]) {
        this.doc.setFillColor(248, 249, 250); // Light background
        this.doc.rect(this.margin + 2, this.currentY - 1, 170, 6, 'F');
        this.doc.setTextColor(108, 117, 125);
        this.addText('📊 Molecular structure images and radar plots available in web interface', 8, false, 4);
        this.doc.setTextColor(0, 0, 0);
        this.currentY += 5;
      }
    });
  }

  // Helper method to add molecule property sections with ResultsView styling
  addMoleculeSection(sectionName, dataObject, smile, indent) {
    if (!dataObject || !dataObject[smile]) return;
    
    this.checkNewPage(20);
    
    // Section header with icon and color
    const sectionIcons = {
      'Physicochemical Properties': '💊',
      'Lipophilicity': '💊', 
      'Water Solubility': '💊',
      'Pharmacokinetics': '🧠',
      'Drug Likeness': '💊',
      'Medicinal Chemistry': '🧬'
    };
    
    const icon = sectionIcons[sectionName] || '📊';
    this.doc.setTextColor(44, 62, 80); // Dark blue-gray
    this.addText(`${icon} ${sectionName}:`, 9, true, indent);
    this.doc.setTextColor(0, 0, 0);
    
    const properties = dataObject[smile];
    if (typeof properties === 'object' && properties !== null) {
      // Create property grid effect with alternating backgrounds
      let propertyIndex = 0;
      Object.entries(properties).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          // Alternating background colors for properties
          if (propertyIndex % 2 === 0) {
            this.doc.setFillColor(248, 249, 250); // Light gray
          } else {
            this.doc.setFillColor(255, 255, 255); // White
          }
          this.doc.rect(this.margin + indent, this.currentY - 1, 160, 6, 'F');
          
          const formattedKey = key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
          const formattedValue = this.formatPropertyValue(key, value);
          
          // Property name in gray
          this.doc.setTextColor(108, 117, 125);
          this.doc.setFontSize(8);
          this.doc.setFont('helvetica', 'normal');
          this.doc.text(formattedKey + ':', this.margin + indent + 2, this.currentY);
          
          // Property value in dark color
          this.doc.setTextColor(44, 62, 80);
          this.doc.setFont('helvetica', 'bold');
          const keyWidth = this.doc.getTextWidth(formattedKey + ': ');
          this.doc.text(formattedValue, this.margin + indent + 2 + keyWidth, this.currentY);
          
          this.doc.setTextColor(0, 0, 0); // Reset
          this.doc.setFont('helvetica', 'normal');
          this.currentY += this.lineHeight;
          propertyIndex++;
        }
      });
    }
    this.currentY += 3;
  }

  // Add generic result for unknown data types
  addGenericResult(item) {
    this.addText('Result Data:', 10, true, 2);
    
    if (typeof item === 'object' && item !== null) {
      Object.entries(item).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          const displayValue = typeof value === 'object' 
            ? JSON.stringify(value, null, 2).substring(0, 200) + '...'
            : String(value);
          this.addKeyValue(key, displayValue, 9, 4);
        }
      });
    } else {
      this.addText(String(item), 9, false, 4);
    }
  }

  // Format property values (exact copy from ResultsView but with additional safety checks)
  formatPropertyValue(key, value) {
    if (value === undefined || value === null) return 'N/A';
    
    if (typeof value === "number") {
      if (isNaN(value) || !isFinite(value)) return 'N/A';
      
      const unitMap = {
        molecular_weight: "g/mol", mw: "g/mol", "molecular weight": "g/mol",
        molar_refractivity: "", mr: "", "molar refractivity": "",
        tpsa: "Å²", topological_polar_surface_area: "Å²", "topological polar surface area": "Å²",
        "log_po/w_(ilogp)": "", "log_po/w_(xlogp3)": "", "log_po/w_(wlogp)": "", 
        "log_po/w_(mlogp)": "", "log_po/w_(silicos-it)": "",
        ilogp: "", xlogp3: "", wlogp: "", mlogp: "", "silicos-it": "",
        "log_s_(esol)": "mg/ml", "log_s_(ali)": "mg/ml", "log_s_(silicos-it)": "mg/ml",
        esol: "mg/ml", ali: "mg/ml",
        "log_kp_(skin_permeation)": "cm/s", "log kp (skin permeation)": "cm/s",
        log_kp: "cm/s", skin_permeation: "cm/s", "skin permeation": "cm/s",
        num_heavy_atoms: "", num_arom_heavy_atoms: "", num_rotatable_bonds: "",
        "num_h-bond_acceptors": "", "num_h-bond_donors": "", heavy_atoms: "",
        arom_heavy_atoms: "", rotatable_bonds: "", "h-bond_acceptors": "", "h-bond_donors": "",
        fraction_csp3: "", csp3: "",
      };

      const unit = unitMap[key.toLowerCase()] || "";

      if (Math.abs(value) < 0.001 && value !== 0) {
        const formattedValue = value.toExponential(2);
        return `${formattedValue}${unit ? ` ${unit}` : ""}`;
      }

      return `${value.toFixed(3)}${unit ? ` ${unit}` : ""}`;
    }
    if (typeof value === "boolean") {
      return value ? "Yes" : "No";
    }
    return String(value);
  }

  // Add AI analysis with ResultsView styling
  addAIAnalysis(aiAnalysis) {
    if (!aiAnalysis) return;
    
    this.checkNewPage(30);
    
    // Add AI Analysis section with purple gradient background (matching ResultsView)
    this.doc.setFillColor(111, 66, 193); // Purple background
    this.doc.rect(this.margin - 5, this.currentY - 5, 180, 25, 'F');
    
    // Add title with white text on purple background
    this.doc.setFontSize(14);
    this.doc.setFont('helvetica', 'bold');
    this.doc.setTextColor(255, 255, 255); // White text
    this.doc.text('🧠 AI Analysis & Synthesis', this.margin, this.currentY + 5);
    this.currentY += 20;
    
    // Add content background (light purple)
    this.doc.setFillColor(240, 235, 255); // Light purple background
    const contentHeight = Math.min(50, this.pageHeight - this.currentY - 20);
    this.doc.rect(this.margin - 3, this.currentY - 3, 176, contentHeight, 'F');
    
    // Convert markdown to plain text for PDF
    const plainText = String(aiAnalysis)
      .replace(/#{1,6}\s+/g, '') // Remove markdown headers
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold markdown
      .replace(/\*(.*?)\*/g, '$1') // Remove italic markdown
      .replace(/`(.*?)`/g, '$1') // Remove code markdown
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Remove links, keep text
      .replace(/\n\s*\n/g, '\n') // Clean up extra newlines
      .trim();
    
    this.doc.setTextColor(44, 62, 80); // Dark text for readability
    this.addText(plainText, 10);
    this.doc.setTextColor(0, 0, 0); // Reset to black
    this.currentY += 5;
  }

  // Generate and download PDF
  async generatePDF(results, filename = 'biomedical-research-results.pdf') {
    try {
      if (!results || typeof results !== 'object') {
        throw new Error('Invalid results data provided');
      }

      this.initPDF('Biomedical Research Results');
      
      // Add summary
      const sourcesData = results.results || {};
      const totalResults = Object.values(sourcesData).reduce((total, sourceResults) => {
        if (Array.isArray(sourceResults)) {
          return total + sourceResults.length;
        }
        return total;
      }, 0);

      this.addSummaryCards({
        totalResults,
        sourcesQueried: Object.keys(sourcesData).length,
        orchestrationMethod: results.orchestration_method
      });

      // Add source data
      Object.entries(sourcesData).forEach(([source, sourceResults]) => {
        const sourceDisplayName = this.getSourceDisplayName(source);
        this.addSourceData(sourceDisplayName, sourceResults);
      });

      // Add AI analysis
      if (results.ai_analysis) {
        this.addAIAnalysis(results.ai_analysis);
      }

      // Save PDF
      this.doc.save(filename);
      
      return true;
    } catch (error) {
      console.error('Error generating PDF:', error);
      throw error;
    }
  }

  // Get source display name
  getSourceDisplayName(source) {
    const sourceMap = {
      "pubmed": "PubMed Articles",
      "uniprot": "UniProt Proteins", 
      "swissadme": "SwissADME Drug Properties"
    };
    return sourceMap[source] || source.toUpperCase();
  }
}

export default PDFExportService;