document.addEventListener('DOMContentLoaded', async () => {
    const NOTEBOOK_FILE_PATH = 'Kaggle.ipynb'; // **UPDATE THIS**
    const TARGET_CELL_INDEX = null; // **UPDATE THIS**
    const TARGET_HTML_SUBSTRING = "<table"; // **UPDATE THIS**

    const outputContainer = document.getElementById('notebook-output-container');

    console.log("Script started."); // Debug point 1

    if (!outputContainer) {
        console.error("Error: 'notebook-output-container' div not found.");
        return;
    }

    try {
        outputContainer.innerHTML = '<p class="loading-message">Fetching notebook data...</p>';
        console.log(`Attempting to fetch: ${NOTEBOOK_FILE_PATH}`); // Debug point 2

        const response = await fetch(NOTEBOOK_FILE_PATH);
        console.log("Fetch response received.", response); // Debug point 3

        if (!response.ok) {
            throw new Error(`HTTP status ${response.status}: ${response.statusText}`);
        }
        const notebookData = await response.json();
        console.log("Notebook data parsed:", notebookData); // Debug point 4 (Check this object!)

        if (!notebookData || !Array.isArray(notebookData.cells)) {
            throw new Error("Invalid .ipynb file structure: 'cells' array not found.");
        }

        let extractedHtml = '';
        let htmlFound = false;

        let cellsToProcess = [];
        if (TARGET_CELL_INDEX !== null && TARGET_CELL_INDEX >= 0 && TARGET_CELL_INDEX < notebookData.cells.length) {
            cellsToProcess.push(notebookData.cells[TARGET_CELL_INDEX]);
            console.log(`Targeting specific cell at index: ${TARGET_CELL_INDEX}`); // Debug point 5a
        } else {
            cellsToProcess = notebookData.cells;
            console.log(`Searching all ${notebookData.cells.length} cells.`); // Debug point 5b
        }

        for (const [i, cell] of cellsToProcess.entries()) { // Use Array.prototype.entries() to get index
            console.log(`Processing cell ${TARGET_CELL_INDEX !== null ? TARGET_CELL_INDEX : i}: type=${cell.cell_type}`); // Debug point 6
            if (cell.cell_type === 'code' && Array.isArray(cell.outputs)) {
                console.log(`  Cell ${TARGET_CELL_INDEX !== null ? TARGET_CELL_INDEX : i} has ${cell.outputs.length} outputs.`); // Debug point 7
                for (const output of cell.outputs) {
                    console.log(`    Output type: ${output.output_type}, name: ${output.name || 'N/A'}`); // Debug point 8

                    if (output.output_type === 'stream' && output.name === 'stdout' && Array.isArray(output.text)) {
                        const textContent = output.text.join('');
                        console.log(`      Stream output text (first 100 chars): ${textContent.substring(0, 100)}...`); // Debug point 9
                        
                        if (textContent.trim().startsWith('<') && textContent.includes('>')) {
                            console.log(`      Heuristic check passed: looks like HTML.`); // Debug point 10
                            if (!TARGET_HTML_SUBSTRING || textContent.includes(TARGET_HTML_SUBSTRING)) {
                                extractedHtml = textContent;
                                htmlFound = true;
                                console.log(`      HTML found and extracted!`); // Debug point 11
                                break; 
                            } else {
                                console.log(`      HTML heuristic passed, but "${TARGET_HTML_SUBSTRING}" not found.`);
                            }
                        } else {
                            console.log(`      Heuristic check failed: does not look like HTML.`);
                        }
                    }
                    // Also keep the display_data check for completeness, just in case
                    else if (output.output_type === 'display_data' && output.data && output.data['text/html']) {
                        const htmlContent = Array.isArray(output.data['text/html']) ? output.data['text/html'].join('') : output.data['text/html'];
                        console.log(`      Display data HTML (first 100 chars): ${htmlContent.substring(0, 100)}...`);
                        if (!TARGET_HTML_SUBSTRING || htmlContent.includes(TARGET_HTML_SUBSTRING)) {
                            extractedHtml = htmlContent;
                            htmlFound = true;
                            console.log(`      HTML found and extracted (display_data)!`);
                            break; 
                        } else {
                            console.log(`      Display data HTML found, but "${TARGET_HTML_SUBSTRING}" not found.`);
                        }
                    }
                }
            }
            if (htmlFound) {
                break; 
            }
        }

        if (htmlFound && extractedHtml) {
            outputContainer.innerHTML = extractedHtml;
            console.log("HTML successfully injected into container."); // Debug point 12
        } else {
            outputContainer.innerHTML = '<p class="error-message">Could not find the expected HTML output in the notebook.</p>';
            console.warn("No HTML found for injection based on criteria."); // Debug point 13
        }

    } catch (error) {
        console.error("Failed to load or parse notebook:", error); // Debug point 14
        outputContainer.innerHTML = `<p class="error-message">Failed to load content: ${error.message}</p>`;
    }
});