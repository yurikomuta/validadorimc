// Global variable to hold the CodeMirror editor instance
let codeEditor;

// Initialize the CodeMirror editor
function initCodeEditor() {
    codeEditor = CodeMirror.fromTextArea(document.getElementById("codeEditor"), {
        mode: "python",
        theme: "monokai",
        lineNumbers: true,
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false,
        lineWrapping: true,
        matchBrackets: true,
        autoCloseBrackets: true,
        extraKeys: {
            "Tab": function(cm) {
                if (cm.getOption("indentWithTabs")) {
                    cm.replaceSelection("\t");
                } else {
                    cm.execCommand("insertSoftTab");
                }
            }
        }
    });
    
    // Set a reasonable height for the editor
    codeEditor.setSize(null, 300);
    
    // Add a sample code to help the user
    codeEditor.setValue(`# Enter your Python code here
def hello_world():
    """This is a sample function"""
    print("Hello, World!")

hello_world()
`);
}

// Function to validate the Python code
async function validateCode() {
    // Show a loading indicator
    const validateBtn = document.getElementById("validateBtn");
    const originalButtonText = validateBtn.innerHTML;
    validateBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Validating...';
    validateBtn.disabled = true;
    
    try {
        // Create a FormData object to send the code or file
        const formData = new FormData(document.getElementById("codeForm"));
        
        // Update the form data with the current content of the code editor
        formData.set("code", codeEditor.getValue());
        
        // Send the request to the server
        const response = await fetch("/validate", {
            method: "POST",
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error("Error validating code:", error);
        // Display an error message to the user
        const resultsPanel = document.getElementById("resultsPanel");
        resultsPanel.style.display = "block";
        
        const validationMessage = document.getElementById("validationMessage");
        validationMessage.className = "alert alert-danger";
        validationMessage.textContent = `An error occurred: ${error.message}`;
        
        document.getElementById("errorDetails").style.display = "none";
        document.getElementById("suggestionsSection").style.display = "none";
    } finally {
        // Restore the button
        validateBtn.innerHTML = originalButtonText;
        validateBtn.disabled = false;
    }
}

// Function to display the validation results
function displayResults(data) {
    const resultsPanel = document.getElementById("resultsPanel");
    const resultsHeader = document.getElementById("resultsHeader");
    const resultsTitle = document.getElementById("resultsTitle");
    const validationMessage = document.getElementById("validationMessage");
    const errorDetails = document.getElementById("errorDetails");
    const errorLine = document.getElementById("errorLine");
    const errorMessage = document.getElementById("errorMessage");
    const suggestionsSection = document.getElementById("suggestionsSection");
    const suggestionsList = document.getElementById("suggestionsList");
    const skillLevelSection = document.getElementById("skillLevelSection");
    
    // Show the results panel
    resultsPanel.style.display = "block";
    
    // Check if this is a multi-file result
    if (data.multi_file === true && data.results) {
        // Multiple file results
        resultsHeader.className = "card-header bg-primary bg-gradient";
        resultsTitle.innerHTML = '<i class="fas fa-file-code me-2"></i>Resultados da Análise de Múltiplos Arquivos';
        
        // Generate a summary message
        const totalFiles = data.results.length;
        const validFiles = data.results.filter(result => result.valid).length;
        
        validationMessage.className = "alert alert-info";
        validationMessage.innerHTML = `
            <h5 class="alert-heading">Resumo da Análise</h5>
            <p>Total de arquivos analisados: <strong>${totalFiles}</strong></p>
            <p>Arquivos válidos: <strong>${validFiles}</strong> | Arquivos com erros: <strong>${totalFiles - validFiles}</strong></p>
            <p>Veja os detalhes de cada arquivo abaixo ou consulte a tabela de análises anteriores na página principal.</p>
        `;
        
        // Hide the standard sections
        errorDetails.style.display = "none";
        skillLevelSection.style.display = "none";
        
        // Display a summary of each file in the suggestions section
        suggestionsSection.style.display = "block";
        suggestionsList.innerHTML = ""; // Clear previous suggestions
        
        // Create a panel for each file result
        data.results.forEach(result => {
            const item = document.createElement("div");
            item.className = "list-group-item mb-3";
            
            // Define the status icon and class
            const statusClass = result.valid ? "success" : "danger";
            const statusIcon = result.valid ? "check-circle" : "times-circle";
            const statusText = result.valid ? "Válido" : "Inválido";
            
            // Start building the item content
            let content = `
                <div class="d-flex w-100 justify-content-between align-items-center mb-2">
                    <h5 class="mb-0 text-${statusClass}">
                        <i class="fas fa-${statusIcon} me-2"></i>
                        ${result.filename}
                    </h5>
                    <span class="badge bg-${statusClass}">${statusText}</span>
                </div>
            `;
            
            // Add error details if not valid
            if (!result.valid) {
                content += `
                    <div class="alert alert-danger py-2 mb-2">
                        <strong>Erro Linha ${result.error_line}:</strong> ${result.error_message}
                    </div>
                `;
            }
            
            // Add skill level if available (now available even with invalid code)
            if (result.skill_level) {
                // Determine badge color based on score
                let levelBadgeClass = "bg-secondary";
                
                if (result.skill_level.score >= 100) {
                    levelBadgeClass = "bg-success";
                } else if (result.skill_level.score >= 50) {
                    levelBadgeClass = "bg-info";
                } else if (result.skill_level.score >= 25) {
                    levelBadgeClass = "bg-warning";
                } else {
                    levelBadgeClass = "bg-danger";
                }
                
                content += `
                    <div class="d-flex align-items-center mb-2">
                        <span class="badge ${levelBadgeClass} me-2">Nível: ${result.skill_level.level}</span>
                        <span class="badge bg-secondary me-2">Pontuação: ${result.skill_level.score}</span>
                        ${result.analysis_id ? 
                            `<a href="/analysis/${result.analysis_id}" class="btn btn-sm btn-outline-primary ms-auto">
                                <i class="fas fa-eye me-1"></i>Ver Detalhes
                            </a>` : ''}
                    </div>
                `;
                
                // Add IMC information if available
                if (result.skill_level.imc_analysis && result.skill_level.imc_analysis.is_imc_calculator) {
                    const imcAnalysis = result.skill_level.imc_analysis;
                    const criticalClass = imcAnalysis.has_functional_calculation ? "success" : "danger";
                    const desirableClass = imcAnalysis.has_classification ? "success" : "warning";
                    
                    content += `
                        <div class="mt-2 mb-1">
                            <span class="badge bg-info me-1">Calculadora IMC</span>
                            <span class="badge bg-${criticalClass} me-1">Critério Crítico ${imcAnalysis.has_functional_calculation ? '✓' : '✗'}</span>
                            <span class="badge bg-${desirableClass} me-1">Critério Desejável ${imcAnalysis.has_classification ? '✓' : '✗'}</span>
                        </div>
                    `;
                }
            }
            
            item.innerHTML = content;
            suggestionsList.appendChild(item);
        });
        
    } else {
        // Single file result (backward compatibility)
        // Update the header and message based on validation result
        if (data.valid) {
            resultsHeader.className = "card-header bg-success bg-gradient";
            resultsTitle.innerHTML = '<i class="fas fa-check-circle me-2"></i>Validation Successful';
            validationMessage.className = "alert alert-success";
            validationMessage.textContent = `Your Python code is syntactically valid!`;
            
            // Hide error details
            errorDetails.style.display = "none";
        } else {
            resultsHeader.className = "card-header bg-danger bg-gradient";
            resultsTitle.innerHTML = '<i class="fas fa-times-circle me-2"></i>Validation Failed';
            validationMessage.className = "alert alert-danger";
            validationMessage.textContent = `Your Python code contains syntax errors.`;
            
            // Show error details
            errorDetails.style.display = "block";
            errorLine.textContent = data.error_line !== -1 ? data.error_line : "Unknown";
            errorMessage.textContent = data.error_message;
        }
        
        // Display skill level if available (now available even for invalid code)
        if (data.skill_level) {
            displaySkillLevel(data.skill_level);
            skillLevelSection.style.display = "block";
        } else {
            skillLevelSection.style.display = "none";
        }
        
        // Display suggestions if available
        if (data.suggestions && data.suggestions.length > 0) {
            suggestionsSection.style.display = "block";
            suggestionsList.innerHTML = ""; // Clear previous suggestions
            
            data.suggestions.forEach(suggestion => {
                const item = document.createElement("div");
                item.className = "list-group-item";
                
                // Add appropriate icon based on suggestion type
                let icon = "info-circle";
                let textClass = "text-info";
                
                if (suggestion.type === "warning") {
                    icon = "exclamation-triangle";
                    textClass = "text-warning";
                } else if (suggestion.type === "style") {
                    icon = "paint-brush";
                    textClass = "text-primary";
                } else if (suggestion.type === "documentation") {
                    icon = "file-alt";
                    textClass = "text-secondary";
                }
                
                item.innerHTML = `
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1 ${textClass}">
                            <i class="fas fa-${icon} me-2"></i>
                            Line ${suggestion.line}
                        </h5>
                        <small class="text-muted">${suggestion.type}</small>
                    </div>
                    <p class="mb-1">${suggestion.message}</p>
                `;
                
                suggestionsList.appendChild(item);
            });
        } else {
            suggestionsSection.style.display = data.valid ? "block" : "none";
            if (data.valid) {
                suggestionsList.innerHTML = `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1 text-success">
                                <i class="fas fa-check-circle me-2"></i>
                                No suggestions
                            </h5>
                        </div>
                        <p class="mb-1">Your code looks good! No improvement suggestions found.</p>
                    </div>
                `;
            }
        }
    }
    
    // Scroll to the results panel
    resultsPanel.scrollIntoView({ behavior: "smooth" });
}

// Function to display the skill level information
function displaySkillLevel(skillLevel) {
    // Update the skill level and score
    document.getElementById("skillLevel").textContent = skillLevel.level;
    document.getElementById("skillScore").textContent = skillLevel.score;
    
    // Update the progress bar based on the score (now using 0-100 scale)
    const progressBar = document.getElementById("skillProgressBar");
    const progressPercent = Math.min(skillLevel.score, 100);
    progressBar.style.width = `${progressPercent}%`;
    progressBar.textContent = `${progressPercent}%`;
    progressBar.setAttribute("aria-valuenow", progressPercent);
    
    // Set the color of the progress bar based on the score
    if (progressPercent >= 100) {
        progressBar.className = "progress-bar bg-success";
    } else if (progressPercent >= 50) {
        progressBar.className = "progress-bar bg-info";
    } else if (progressPercent >= 25) {
        progressBar.className = "progress-bar bg-warning";
    } else {
        progressBar.className = "progress-bar bg-danger";
    }
    
    // Display IMC-specific analysis if available
    if (skillLevel.imc_analysis) {
        displayImcAnalysis(skillLevel.imc_analysis);
    }
    
    // Display the detected features
    const featuresContainer = document.getElementById("codeFeatures");
    featuresContainer.innerHTML = ""; // Clear previous features
    
    // Define feature display names and icons
    const featureInfo = {
        "functions": { name: "Funções", icon: "code" },
        "classes": { name: "Classes", icon: "cube" },
        "imports": { name: "Imports", icon: "download" },
        "comprehensions": { name: "Comprehensions", icon: "list" },
        "error_handling": { name: "Tratamento de Erros", icon: "exclamation-circle" },
        "advanced_types": { name: "Tipos Avançados", icon: "layer-group" },
        "docstrings": { name: "Documentação", icon: "file-alt" },
        "decorators": { name: "Decoradores", icon: "paint-brush" },
        "complex_structures": { name: "Estruturas Complexas", icon: "project-diagram" },
        "advanced_features": { name: "Recursos Avançados", icon: "star" }
    };
    
    // Create a card for each feature
    for (const [feature, count] of Object.entries(skillLevel.features)) {
        if (count > 0) {
            const featureDisplay = featureInfo[feature] || { name: feature, icon: "code" };
            
            const featureCol = document.createElement("div");
            featureCol.className = "col-md-6 col-lg-4 mb-3";
            
            featureCol.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="me-3">
                        <i class="fas fa-${featureDisplay.icon} fa-2x text-info"></i>
                    </div>
                    <div>
                        <h6 class="mb-0">${featureDisplay.name}</h6>
                        <span class="badge bg-info">${count}</span>
                    </div>
                </div>
            `;
            
            featuresContainer.appendChild(featureCol);
        }
    }
    
    // If no features were found
    if (featuresContainer.children.length === 0) {
        featuresContainer.innerHTML = `
            <div class="col-12">
                <p class="text-muted">Nenhuma característica avançada detectada no código.</p>
            </div>
        `;
    }
}

// Function to display IMC-specific analysis
function displayImcAnalysis(imcAnalysis) {
    const imcSection = document.getElementById("imcAnalysisSection");
    
    // Only show the IMC analysis section if it's an IMC calculator
    if (imcAnalysis.is_imc_calculator) {
        imcSection.style.display = "block";
        
        // Get the elements we need to update
        const imcLevelAlert = document.getElementById("imcLevelAlert");
        const imcLevelTitle = document.getElementById("imcLevelTitle");
        const imcLevelDescription = document.getElementById("imcLevelDescription");
        const criticalCheck = document.getElementById("criticalCheck");
        const desirableCheck = document.getElementById("desirableCheck");
        
        // Update the critical criteria check
        if (imcAnalysis.has_functional_calculation) {
            criticalCheck.innerHTML = '<i class="fas fa-check-circle text-success"></i>';
        } else {
            criticalCheck.innerHTML = '<i class="fas fa-times-circle text-danger"></i>';
        }
        
        // Update the desirable criteria check
        if (imcAnalysis.has_classification) {
            desirableCheck.innerHTML = '<i class="fas fa-check-circle text-success"></i>';
        } else {
            desirableCheck.innerHTML = '<i class="fas fa-times-circle text-danger"></i>';
        }
        
        // Update the IMC level alert based on the result
        let alertClass = "alert-warning";
        let description = "";
        
        switch (imcAnalysis.level) {
            case "Desejável":
                alertClass = "alert-success";
                description = "Parabéns! Seu código atende a todos os critérios para a calculadora de IMC. Ele realiza o cálculo corretamente e também fornece a classificação do IMC.";
                break;
                
            case "Crítico":
                alertClass = "alert-info";
                description = "Seu código atende ao critério crítico para a calculadora de IMC, realizando o cálculo corretamente. Para atingir o nível 'Desejável', adicione uma classificação do IMC (ex: abaixo do peso, normal, sobrepeso, etc).";
                break;
                
            default:
                alertClass = "alert-danger";
                description = "Seu código foi identificado como uma tentativa de calculadora de IMC, mas não realiza o cálculo corretamente. Verifique a fórmula IMC = peso / (altura * altura) e certifique-se de que o código esteja funcionando.";
                break;
        }
        
        // Update the UI elements
        imcLevelTitle.textContent = `Nível: ${imcAnalysis.level}`;
        imcLevelDescription.textContent = description;
        imcLevelAlert.className = `alert ${alertClass}`;
        
    } else {
        // Hide the IMC section if it's not an IMC calculator
        imcSection.style.display = "none";
    }
}

// Function to handle file uploads
function handleFileUpload(event) {
    const files = event.target.files;
    if (files.length === 1) {
        // Single file, load it into the editor
        const file = files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            codeEditor.setValue(e.target.result);
        };
        reader.readAsText(file);
    } else if (files.length > 1) {
        // Multiple files selected, clear the editor and show a message
        codeEditor.setValue('# Multiple files selected for upload\n# Click "Validate Code" to analyze all files');
    }
}

// Function to clear the code editor
function clearCodeEditor() {
    if (codeEditor) {
        codeEditor.setValue(''); // Clear the editor
    }
    
    // Reset the input file element
    const fileInput = document.getElementById("codeFile");
    if (fileInput) {
        fileInput.value = '';
    }
    
    // Hide results panel if visible
    const resultsPanel = document.getElementById("resultsPanel");
    if (resultsPanel) {
        resultsPanel.style.display = "none";
    }
}

// Set up event listeners when the DOM is loaded
document.addEventListener("DOMContentLoaded", function() {
    // Initialize CodeMirror
    initCodeEditor();
    
    // Set up the validate button
    const validateBtn = document.getElementById("validateBtn");
    if (validateBtn) {
        validateBtn.addEventListener("click", validateCode);
    }
    
    // Set up the clear button
    const clearBtn = document.getElementById("clearBtn");
    if (clearBtn) {
        clearBtn.addEventListener("click", clearCodeEditor);
    }
    
    // Set up the file input change handler
    const codeFile = document.getElementById("codeFile");
    if (codeFile) {
        codeFile.addEventListener("change", handleFileUpload);
    }
    
    // Set up CSV export button if it exists
    const exportBtn = document.getElementById("exportIndexCsvBtn");
    if (exportBtn) {
        exportBtn.addEventListener("click", exportTableToCSV);
    }
});
