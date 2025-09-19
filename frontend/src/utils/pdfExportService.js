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

  // Add PubMed result with enhanced hierarchy
  addPubMedResult(item) {
    // Title with proper hierarchy
    if (item.title) {
      this.doc.setFontSize(12);
      this.doc.setFont('helvetica', 'bold');
      this.doc.setTextColor(33, 37, 41); // Dark gray for title
      this.addText(item.title, 12, true, 1);
      this.doc.setTextColor(0, 0, 0);
    }
    
    // Publication details in structured format
    this.currentY += 2;
    
    // Authors
    if (item.authors && Array.isArray(item.authors) && item.authors.length > 0) {
      this.addKeyValue('Authors', item.authors.slice(0, 5).join(", ") + (item.authors.length > 5 ? ' et al.' : ''), 9, 1);
    }
    
    // Journal and publication info
    if (item.journal) {
      this.addKeyValue('Journal', item.journal, 9, 1);
    }
    
    if (item.publication_date) {
      this.addKeyValue('Published', item.publication_date, 9, 1);
    }
    
    if (item.pmid) {
      this.addKeyValue('PMID', item.pmid, 9, 1);
    }
    
    // Abstract with better formatting
    if (item.abstract) {
      this.currentY += 2;
      this.doc.setFontSize(10);
      this.doc.setFont('helvetica', 'bold');
      this.doc.setTextColor(52, 58, 64);
      this.doc.text('Abstract:', this.margin, this.currentY);
      this.currentY += 4;
      
      const abstract = item.abstract.length > 400 
        ? `${item.abstract.substring(0, 400)}...` 
        : item.abstract;
      
      this.doc.setFont('helvetica', 'normal');
      this.doc.setTextColor(73, 80, 87);
      this.addText(abstract, 9, false, 1);
      this.doc.setTextColor(0, 0, 0);
    }
    
    // Source link with proper styling
    if (item.url) {
      this.currentY += 3;
      this.doc.setFontSize(9);
      this.doc.setFont('helvetica', 'bold');
      this.doc.setTextColor(0, 123, 255); // Bootstrap primary blue
      this.doc.text('Source: ', this.margin, this.currentY);
      
      this.doc.setFont('helvetica', 'normal');
      this.doc.setTextColor(0, 123, 255);
      this.doc.text(item.url, this.margin + 15, this.currentY);
      this.doc.setTextColor(0, 0, 0);
    }
  }

  // Add UniProt result with enhanced hierarchy
  addUniProtResult(item) {
    // Protein name with proper hierarchy
    if (item.protein_name) {
      this.doc.setFontSize(12);
      this.doc.setFont('helvetica', 'bold');
      this.doc.setTextColor(33, 37, 41);
      this.addText(item.protein_name, 12, true, 1);
      this.doc.setTextColor(0, 0, 0);
    }
    
    this.currentY += 2;
    
    // Basic protein information
    if (item.accession) {
      this.addKeyValue('Accession', item.accession, 9, 1);
    }
    
    if (item.organism) {
      this.addKeyValue('Organism', item.organism, 9, 1);
    }
    
    if (item.sequence_length) {
      this.addKeyValue('Sequence Length', `${item.sequence_length} amino acids`, 9, 1);
    }
    
    if (item.reviewed !== undefined) {
      this.addKeyValue('Reviewed', item.reviewed ? "Yes (Swiss-Prot)" : "No (TrEMBL)", 9, 1);
    }
    
    // Gene names with better formatting
    if (item.gene_names && Array.isArray(item.gene_names) && item.gene_names.length > 0) {
      this.addKeyValue('Gene Names', item.gene_names.join(", "), 9, 1);
    }
    
    // Keywords with categorization
    if (item.keywords && Array.isArray(item.keywords) && item.keywords.length > 0) {
      this.addKeyValue('Keywords', item.keywords.slice(0, 8).join(", "), 9, 1);
    }
    
    // Function description if available
    if (item.function_description) {
      this.currentY += 2;
      this.doc.setFontSize(10);
      this.doc.setFont('helvetica', 'bold');
      this.doc.setTextColor(52, 58, 64);
      this.doc.text('Function:', this.margin, this.currentY);
      this.currentY += 4;
      
      const functionText = item.function_description.length > 300 
        ? `${item.function_description.substring(0, 300)}...` 
        : item.function_description;
      
      this.doc.setFont('helvetica', 'normal');
      this.doc.setTextColor(73, 80, 87);
      this.addText(functionText, 9, false, 1);
      this.doc.setTextColor(0, 0, 0);
    }
    
    // Source link with proper styling
    if (item.url) {
      this.currentY += 3;
      this.doc.setFontSize(9);
      this.doc.setFont('helvetica', 'bold');
      this.doc.setTextColor(0, 123, 255);
      this.doc.text('Source: ', this.margin, this.currentY);
      
      this.doc.setFont('helvetica', 'normal');
      this.doc.setTextColor(0, 123, 255);
      this.doc.text(item.url, this.margin + 15, this.currentY);
      this.doc.setTextColor(0, 0, 0);
    }
  }

  // Add SwissADME result with enhanced table formatting
  addSwissADMEResult(item) {
    const smiles = item.smiles || [];
    const molecules = smiles.length > 0 ? smiles : ["Unknown"];

    // Boiled Egg Plot section with enhanced styling
    if (item.boiled_egg_plot) {
      this.checkNewPage(20);
      this.doc.setFillColor(255, 243, 205); // Light yellow background
      this.doc.rect(this.margin - 3, this.currentY - 3, 176, 15, 'F');
      this.doc.setTextColor(133, 100, 4); // Orange-brown color
      this.doc.setFontSize(11);
      this.doc.setFont('helvetica', 'bold');
      this.doc.text('🥚 Boiled Egg Plot (ADME Properties)', this.margin, this.currentY + 3);
      this.doc.setFont('helvetica', 'normal');
      this.doc.setFontSize(9);
      this.doc.text('Visual representation of drug absorption and distribution properties', this.margin, this.currentY + 7);
      this.doc.text('Available in web interface for interactive viewing', this.margin, this.currentY + 10);
      this.doc.setTextColor(0, 0, 0);
      this.currentY += 8;
    }

    // Process each molecule with enhanced table structure
    molecules.forEach((smile, index) => {
      this.checkNewPage(40);
      
      // Molecule header with enhanced styling
      this.doc.setFillColor(52, 144, 220); // Professional blue
      this.doc.rect(this.margin - 3, this.currentY - 3, 176, 12, 'F');
      this.doc.setTextColor(255, 255, 255);
      this.doc.setFontSize(12);
      this.doc.setFont('helvetica', 'bold');
      this.doc.text(`Molecule ${index + 1}`, this.margin, this.currentY + 3);
      this.doc.setTextColor(0, 0, 0);
      this.currentY += 8;
      
      // SMILES string with enhanced formatting
      if (smile && smile !== "Unknown") {
        this.doc.setFillColor(240, 248, 255); // Light blue background
        this.doc.rect(this.margin, this.currentY - 2, 170, 8, 'F');
        this.doc.setFontSize(9);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(52, 58, 64);
        this.doc.text('SMILES:', this.margin + 2, this.currentY + 1);
        this.doc.setFont('courier', 'normal');
        this.doc.setTextColor(73, 80, 87);
        this.doc.text(smile, this.margin + 2, this.currentY + 4);
        this.doc.setFont('helvetica', 'normal');
        this.doc.setTextColor(0, 0, 0);
        this.currentY += 6;
      }

      // Create comprehensive property tables
      this.addSwissADMETable('Physicochemical Properties', item.physicochemical_properties, smile);
      this.addSwissADMETable('Lipophilicity', item.lipophilicity, smile);
      this.addSwissADMETable('Water Solubility', item.water_solubility, smile);
      this.addSwissADMETable('Pharmacokinetics', item.pharmacokinetics, smile);
      this.addSwissADMETable('Drug Likeness', item.druglikeness, smile);
      this.addSwissADMETable('Medicinal Chemistry', item.medicinal_chemistry, smile);

      // Enhanced image information
      if (item.images && item.images[smile]) {
        this.currentY += 3;
        this.doc.setFillColor(248, 249, 250);
        this.doc.rect(this.margin, this.currentY - 2, 170, 10, 'F');
        this.doc.setFontSize(9);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(52, 58, 64);
        this.doc.text('📊 Molecular Visualizations:', this.margin + 2, this.currentY + 1);
        this.doc.setFont('helvetica', 'normal');
        this.doc.setTextColor(108, 117, 125);
        this.doc.text('• 2D molecular structure', this.margin + 2, this.currentY + 4);
        this.doc.text('• 3D molecular visualization', this.margin + 2, this.currentY + 6);
        this.doc.text('• ADME radar plot', this.margin + 2, this.currentY + 8);
        this.doc.text('Available in web interface for interactive viewing', this.margin + 2, this.currentY + 10);
        this.doc.setTextColor(0, 0, 0);
        this.currentY += 8;
      }
      
      this.currentY += 5; // Space between molecules
    });
  }

  // Enhanced method to add SwissADME property tables
  addSwissADMETable(sectionName, dataObject, smile) {
    if (!dataObject || !dataObject[smile]) return;
    
    this.checkNewPage(25);
    
    // Section header with enhanced styling
    const sectionIcons = {
      'Physicochemical Properties': '💊',
      'Lipophilicity': '🧪', 
      'Water Solubility': '💧',
      'Pharmacokinetics': '🧠',
      'Drug Likeness': '✅',
      'Medicinal Chemistry': '🧬'
    };
    
    const icon = sectionIcons[sectionName] || '📊';
    
    // Section header background
    this.doc.setFillColor(52, 58, 64); // Dark gray header
    this.doc.rect(this.margin, this.currentY - 2, 170, 8, 'F');
    this.doc.setTextColor(255, 255, 255);
    this.doc.setFontSize(10);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text(`${icon} ${sectionName}`, this.margin + 2, this.currentY + 2);
    this.doc.setTextColor(0, 0, 0);
    this.currentY += 6;
    
    const properties = dataObject[smile];
    if (typeof properties === 'object' && properties !== null) {
      // Create table structure
      const entries = Object.entries(properties).filter(([key, value]) => 
        value !== undefined && value !== null && value !== ''
      );
      
      if (entries.length === 0) {
        this.doc.setFontSize(8);
        this.doc.setTextColor(108, 117, 125);
        this.doc.text('No data available', this.margin + 2, this.currentY + 2);
        this.doc.setTextColor(0, 0, 0);
        this.currentY += 4;
        return;
      }
      
      // Table header
      this.doc.setFillColor(240, 248, 255); // Light blue header
      this.doc.rect(this.margin, this.currentY - 1, 170, 6, 'F');
      this.doc.setFontSize(8);
      this.doc.setFont('helvetica', 'bold');
      this.doc.setTextColor(52, 58, 64);
      this.doc.text('Property', this.margin + 2, this.currentY + 2);
      this.doc.text('Value', this.margin + 90, this.currentY + 2);
      this.doc.setTextColor(0, 0, 0);
      this.currentY += 4;
      
      // Table rows with alternating colors
      entries.forEach(([key, value], index) => {
        const formattedKey = key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
        const formattedValue = this.formatPropertyValue(key, value);
        
        // Alternating row colors
        if (index % 2 === 0) {
          this.doc.setFillColor(248, 249, 250); // Light gray
        } else {
          this.doc.setFillColor(255, 255, 255); // White
        }
        this.doc.rect(this.margin, this.currentY - 1, 170, 6, 'F');
        
        // Property name
        this.doc.setFontSize(8);
        this.doc.setFont('helvetica', 'normal');
        this.doc.setTextColor(73, 80, 87);
        this.doc.text(formattedKey, this.margin + 2, this.currentY + 2);
        
        // Property value with color coding based on type
        this.doc.setFont('helvetica', 'bold');
        if (typeof value === 'number') {
          this.doc.setTextColor(40, 167, 69); // Green for numbers
        } else if (typeof value === 'boolean') {
          this.doc.setTextColor(value ? 40 : 220, value ? 167 : 53, value ? 69 : 53); // Green/Red for boolean
        } else {
          this.doc.setTextColor(52, 58, 64); // Dark for text
        }
        
        // Handle long values by wrapping
        const maxWidth = 70;
        const valueWidth = this.doc.getTextWidth(formattedValue);
        if (valueWidth > maxWidth) {
          const words = formattedValue.split(' ');
          let line = '';
          let yOffset = 0;
          
          words.forEach(word => {
            const testLine = line + (line ? ' ' : '') + word;
            if (this.doc.getTextWidth(testLine) > maxWidth && line) {
              this.doc.text(line, this.margin + 90, this.currentY + 2 + yOffset);
              line = word;
              yOffset += 3;
            } else {
              line = testLine;
            }
          });
          if (line) {
            this.doc.text(line, this.margin + 90, this.currentY + 2 + yOffset);
          }
        } else {
          this.doc.text(formattedValue, this.margin + 90, this.currentY + 2);
        }
        
        this.doc.setTextColor(0, 0, 0);
        this.currentY += 4;
      });
    }
    this.currentY += 3; // Space after table
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

  // Add AI analysis with enhanced formatting and hierarchy
  addAIAnalysis(aiAnalysis) {
    if (!aiAnalysis) return;
    
    this.checkNewPage(40);
    
    // Enhanced AI Analysis header with gradient effect
    this.doc.setFillColor(111, 66, 193); // Purple background
    this.doc.rect(this.margin - 5, this.currentY - 5, 180, 20, 'F');
    
    // Add title with enhanced styling
    this.doc.setFontSize(16);
    this.doc.setFont('helvetica', 'bold');
    this.doc.setTextColor(255, 255, 255);
    this.doc.text('🧠 AI Analysis & Synthesis', this.margin, this.currentY + 3);
    
    // Add subtitle
    this.doc.setFontSize(10);
    this.doc.setFont('helvetica', 'normal');
    this.doc.text('Comprehensive analysis of biomedical research findings', this.margin, this.currentY + 8);
    this.currentY += 15;
    
    // Parse and format markdown content with proper hierarchy
    const formattedContent = this.parseMarkdownContent(aiAnalysis);
    
    // Add content with enhanced background
    this.doc.setFillColor(248, 250, 252); // Light gray background
    const contentHeight = Math.min(80, this.pageHeight - this.currentY - 20);
    this.doc.rect(this.margin - 3, this.currentY - 3, 176, contentHeight, 'F');
    
    // Render formatted content
    this.renderFormattedContent(formattedContent);
    
    this.currentY += 5;
  }
  
  // Parse markdown content into structured format
  parseMarkdownContent(content) {
    const lines = String(content).split('\n');
    const parsed = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      if (!line) continue;
      
      // Headers
      if (line.startsWith('#')) {
        const level = line.match(/^#+/)[0].length;
        const text = line.replace(/^#+\s*/, '');
        parsed.push({ type: 'header', level, text, bold: true });
      }
      // Bold text
      else if (line.includes('**')) {
        const parts = line.split(/(\*\*.*?\*\*)/g);
        const formattedParts = parts.map(part => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return { type: 'text', text: part.slice(2, -2), bold: true };
          }
          return { type: 'text', text: part, bold: false };
        });
        parsed.push({ type: 'paragraph', parts: formattedParts });
      }
      // Lists
      else if (line.startsWith('- ') || line.startsWith('* ')) {
        parsed.push({ type: 'list', text: line.substring(2), level: 1 });
      }
      else if (line.match(/^\s+- /) || line.match(/^\s+\* /)) {
        const level = Math.floor((line.length - line.trimStart().length) / 2) + 1;
        parsed.push({ type: 'list', text: line.trim().substring(2), level });
      }
      // Numbered lists
      else if (line.match(/^\d+\./)) {
        parsed.push({ type: 'numbered', text: line.replace(/^\d+\.\s*/, ''), number: line.match(/^(\d+)/)[1] });
      }
      // Regular paragraphs
      else {
        parsed.push({ type: 'paragraph', text: line });
      }
    }
    
    return parsed;
  }
  
  // Render formatted content with proper hierarchy
  renderFormattedContent(content) {
    content.forEach(item => {
      this.checkNewPage(15);
      
      switch (item.type) {
        case 'header':
          this.doc.setFontSize(12 - item.level);
          this.doc.setFont('helvetica', 'bold');
          this.doc.setTextColor(52, 58, 64);
          this.doc.text(item.text, this.margin + (item.level - 1) * 5, this.currentY + 2);
          this.currentY += 6;
          break;
          
        case 'paragraph':
          if (item.parts) {
            // Mixed formatting paragraph
            let x = this.margin;
            item.parts.forEach(part => {
              this.doc.setFont('helvetica', part.bold ? 'bold' : 'normal');
              this.doc.setTextColor(73, 80, 87);
              this.doc.setFontSize(9);
              this.doc.text(part.text, x, this.currentY + 2);
              x += this.doc.getTextWidth(part.text);
            });
          } else {
            // Regular paragraph
            this.doc.setFontSize(9);
            this.doc.setFont('helvetica', 'normal');
            this.doc.setTextColor(73, 80, 87);
            this.addText(item.text, 9, false, 0);
          }
          this.currentY += 4;
          break;
          
        case 'list':
          this.doc.setFontSize(9);
          this.doc.setFont('helvetica', 'normal');
          this.doc.setTextColor(73, 80, 87);
          const indent = this.margin + (item.level - 1) * 8;
          this.doc.text('•', indent, this.currentY + 2);
          this.doc.text(item.text, indent + 4, this.currentY + 2);
          this.currentY += 4;
          break;
          
        case 'numbered':
          this.doc.setFontSize(9);
          this.doc.setFont('helvetica', 'normal');
          this.doc.setTextColor(73, 80, 87);
          this.doc.text(`${item.number}.`, this.margin, this.currentY + 2);
          this.doc.text(item.text, this.margin + 8, this.currentY + 2);
          this.currentY += 4;
          break;
      }
    });
    
    this.doc.setTextColor(0, 0, 0); // Reset to black
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