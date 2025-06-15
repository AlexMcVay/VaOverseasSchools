document.addEventListener('DOMContentLoaded', async () => {
    // --- Configuration ---
    // IMPORTANT: Make sure this path is correct and accessible via your web server.
    // If 'index.html' and 'Kaggle.ipynb' are in the same folder, this relative path works.
    const NOTEBOOK_FILE_PATH = 'Kaggle.ipynb'; // **VERIFY THIS IS THE EXACT FILENAME**

    // IMPORTANT: Identify the cell index or a unique substring to find your HTML.
    // Option 1: If you know the 0-based index of the cell containing the HTML output.
    //           (e.g., if it's the 3rd cell, use 2)
    const TARGET_CELL_INDEX = null; // Set to a number (e.g., 2) if known, otherwise keep null to search all.

    // Option 2: If you want to search for specific HTML content (e.g., part of a table ID, a unique class).
    //           This will search all code cell outputs for the first match.
    //           You've specified "<table ", which is a good identifier for a table.
    const TARGET_HTML_SUBSTRING = "<table "; 
    
    // --- DOM Elements ---
    const outputContainer = document.getElementById('notebook-output-container');
    const searchFilter = document.getElementById('search-filter');
    const countryFilter = document.getElementById('country-filter');
    const resetFiltersBtn = document.getElementById('reset-filters');

    // --- Initial Debugging Logs and Setup ---
    console.log("🚀 Script execution started."); 

    if (!outputContainer) {
        console.error("❌ Error: 'notebook-output-container' div not found in index.html. Please ensure it exists.");
        return; // Stop execution if the container is missing
    }

    try {
        outputContainer.innerHTML = '<p class="loading-message">Fetching notebook data...</p>';
        console.log(`📡 Attempting to fetch notebook from: ${NOTEBOOK_FILE_PATH}`);

        // 1. Fetch the raw .ipynb file content as JSON
        const response = await fetch(NOTEBOOK_FILE_PATH);
        console.log("✅ Fetch response received:", response);

        if (!response.ok) {
            throw new Error(`HTTP status ${response.status}: ${response.statusText}`);
        }
        
        const notebookData = await response.json();
        // IMPORTANT: Inspect this object in your console to understand its full structure!
        // Expand the 'cells' array to see the content and outputs of each cell.
        console.log("📄 Notebook data parsed (inspect 'cells' array below):", notebookData); 

        // 2. Validate notebook structure
        if (!notebookData || !Array.isArray(notebookData.cells)) {
            throw new Error("Invalid .ipynb file: 'cells' array is missing or malformed.");
        }

        let extractedHtml = '';
        let htmlFound = false;

        // Determine which cells to process (specific index or all)
        let cellsToProcess = [];
        if (TARGET_CELL_INDEX !== null && TARGET_CELL_INDEX >= 0 && TARGET_CELL_INDEX < notebookData.cells.length) {
            cellsToProcess.push(notebookData.cells[TARGET_CELL_INDEX]);
            console.log(`🎯 Targeting specific cell at index: ${TARGET_CELL_INDEX}`);
        } else {
            cellsToProcess = notebookData.cells;
            console.log(`🔍 Searching all ${notebookData.cells.length} cells for HTML output.`);
        }

        // 3. Iterate through identified cells and their outputs to find the HTML
        for (let i = 0; i < cellsToProcess.length; i++) {
            const cell = cellsToProcess[i];
            // Get the actual index of the cell in the original notebook for logging clarity
            const currentCellOriginalIndex = (TARGET_CELL_INDEX !== null) ? TARGET_CELL_INDEX : i;

            console.log(`--- Processing cell [${currentCellOriginalIndex}] (Type: ${cell.cell_type}) ---`);

            // Only process 'code' cells as they contain 'outputs'
            if (cell.cell_type === 'code' && Array.isArray(cell.outputs)) {
                console.log(`  Found ${cell.outputs.length} outputs in code cell [${currentCellOriginalIndex}].`);

                for (let j = 0; j < cell.outputs.length; j++) {
                    const output = cell.outputs[j];
                    console.log(`    Processing output [${j}] (Type: ${output.output_type}, Name: ${output.name || 'N/A'})`);

                    // Primary Check: 'stream' output (for content printed with Python's print() function)
                    if (output.output_type === 'stream' && output.name === 'stdout') {
                        // **** FIX: Handle output.text as a string or array of strings ****
                        const textContent = Array.isArray(output.text) ? output.text.join('') : output.text;
                        
                        console.log(`      💡 Debug: output.text type: ${typeof output.text}, IsArray: ${Array.isArray(output.text)}`);
                        // ************************************************

                        // **** THIS IS THE CRUCIAL LOG FOR YOU TO INSPECT ****
                        console.log(`      💡 Cell [${currentCellOriginalIndex}] Stream Output Content (first 500 chars):`, textContent.substring(0, 500), '...'); 
                        console.log(`      💡 Cell [${currentCellOriginalIndex}] Stream Output Content (FULL STRING - copy from console):`, textContent);
                        // ****************************************************

                        // Heuristic to check if the stream content broadly looks like HTML
                        // It must start with '<' (after trimming whitespace) and contain '>'
                        const isHtmlLike = textContent.trim().startsWith('<') && textContent.includes('>');
                        console.log(`      HTML heuristic check (startsWith('<') && includes('>')): ${isHtmlLike ? 'PASSED' : 'FAILED'}`);

                        // Check if the specific substring is present in the content
                        const hasSubstring = !TARGET_HTML_SUBSTRING || textContent.includes(TARGET_HTML_SUBSTRING);
                        console.log(`      Substring "${TARGET_HTML_SUBSTRING}" check: ${hasSubstring ? 'PASSED' : 'FAILED'}`);

                        if (isHtmlLike && hasSubstring) {
                            extractedHtml = textContent;
                            htmlFound = true;
                            console.log(`      ✨ Success! HTML extracted from stream output of cell [${currentCellOriginalIndex}].`);
                            break; // Stop looking in this cell's outputs
                        }
                    }
                    // Secondary Check: 'display_data' HTML (for richer outputs like df.to_html() or plots from libraries)
                    else if (output.output_type === 'display_data' && output.data && output.data['text/html']) {
                        const htmlContent = Array.isArray(output.data['text/html']) ? output.data['text/html'].join('') : output.data['text/html'];
                        
                        console.log(`      💡 Cell [${currentCellOriginalIndex}] Display Data HTML Content (first 500 chars):`, htmlContent.substring(0, 500), '...');
                        console.log(`      💡 Cell [${currentCellOriginalIndex}] Display Data HTML Content (FULL STRING - copy from console):`, htmlContent);

                        // display_data 'text/html' is usually always valid HTML, so no 'isHtmlLike' heuristic needed.
                        const hasSubstring = !TARGET_HTML_SUBSTRING || htmlContent.includes(TARGET_HTML_SUBSTRING);
                        console.log(`      Substring "${TARGET_HTML_SUBSTRING}" check: ${hasSubstring ? 'PASSED' : 'FAILED'}`);

                        if (hasSubstring) {
                            extractedHtml = htmlContent;
                            htmlFound = true;
                            console.log(`      ✨ Success! HTML extracted from display_data output of cell [${currentCellOriginalIndex}].`);
                            break; // Stop looking in this cell's outputs
                        }
                    }
                    console.log("    --- End of output check for current output ---");
                }
            }
            if (htmlFound) {
                break; // Stop looking in other cells if HTML was found
            }
            console.log("--- End of cell processing ---");
        }        // Final injection step
        if (htmlFound && extractedHtml.trim().length > 0) { // Also check if extracted HTML is not just whitespace
            outputContainer.innerHTML = extractedHtml;
            console.log("✅ HTML successfully injected into container. Please check your page!");
            
            // Initialize table filtering functionality after HTML is injected
            initializeTableFilters();
        } else {
            outputContainer.innerHTML = '<p class="error-message">😔 No relevant HTML output found in the notebook based on the configuration or extracted HTML was empty.</p>';
            console.warn("⚠️ No HTML found for injection based on criteria or extracted HTML was empty.");
        }

    } catch (error) {
        // Catch any errors during fetch or JSON parsing
        console.error("❌ Critical Error during notebook processing:", error);
        outputContainer.innerHTML = `<p class="error-message">Failed to load content: ${error.message}</p>`;
    }
    console.log("🏁 Script execution finished.");
    
    // ============== TABLE FILTERING FUNCTIONS ==============
    
    function initializeTableFilters() {
        const table = outputContainer.querySelector('table');
        if (!table) {
            console.error("❌ Error: Table not found in the injected HTML");
            return;
        }
        
        // Add IDs to table headers for sorting
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.setAttribute('data-column', index);
            // Create a wrapper for the header content and indicators
            const headerText = header.textContent;
            header.textContent = ''; // Clear original content
            
            // Create and append text span
            const textSpan = document.createElement('span');
            textSpan.textContent = headerText;
            header.appendChild(textSpan);
            
            // Add click event for sorting
            header.addEventListener('click', () => sortTable(index));
        });
        
        // Populate country filter dropdown with unique values
        populateCountryFilter();
        
        // Add event listeners to filters
        if (searchFilter) {
            searchFilter.addEventListener('input', applyFilters);
        }
        if (countryFilter) {
            countryFilter.addEventListener('change', applyFilters);
        }
        if (resetFiltersBtn) {
            resetFiltersBtn.addEventListener('click', resetFilters);
        }
        
        console.log("✅ Table filtering functionality initialized!");
    }
    
    function populateCountryFilter() {
        const table = outputContainer.querySelector('table');
        if (!table || !countryFilter) return;
        
        // Find country column index (assuming it's named "Country" or "country")
        const headers = Array.from(table.querySelectorAll('th'));
        const countryColIndex = headers.findIndex(h => 
            h.textContent.toLowerCase() === 'country');
        
        if (countryColIndex === -1) {
            console.warn("⚠️ Country column not found in table headers");
            return;
        }
        
        // Get all unique country values
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        const uniqueCountries = new Set();
        
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length > countryColIndex) {
                const countryValue = cells[countryColIndex].textContent.trim();
                if (countryValue) uniqueCountries.add(countryValue);
            }
        });
        
        // Sort countries alphabetically
        const sortedCountries = Array.from(uniqueCountries).sort();
        
        // Clear existing options except the first one (All Countries)
        while (countryFilter.options.length > 1) {
            countryFilter.remove(1);
        }
        
        // Add country options to dropdown
        sortedCountries.forEach(country => {
            const option = document.createElement('option');
            option.value = country;
            option.textContent = country;
            countryFilter.appendChild(option);
        });
        
        console.log(`✅ Country filter populated with ${sortedCountries.length} countries`);
    }
    
    function applyFilters() {
        const table = outputContainer.querySelector('table');
        if (!table) return;
        
        const searchText = searchFilter ? searchFilter.value.toLowerCase() : '';
        const selectedCountry = countryFilter ? countryFilter.value : '';
        
        // Find country column index
        const headers = Array.from(table.querySelectorAll('th'));
        const countryColIndex = headers.findIndex(h => 
            h.textContent.toLowerCase() === 'country');
        
        const rows = table.querySelectorAll('tbody tr');
        let visibleCount = 0;
        
        rows.forEach(row => {
            let showRow = true;
            
            // Country filter
            if (selectedCountry && countryColIndex !== -1) {
                const countryCell = row.querySelectorAll('td')[countryColIndex];
                if (countryCell && countryCell.textContent.trim() !== selectedCountry) {
                    showRow = false;
                }
            }
            
            // Text search filter (searches all columns)
            if (showRow && searchText) {
                const rowText = row.textContent.toLowerCase();
                if (!rowText.includes(searchText)) {
                    showRow = false;
                }
            }
            
            // Show or hide row
            if (showRow) {
                row.classList.remove('filtered');
                visibleCount++;
            } else {
                row.classList.add('filtered');
            }
        });
        
        console.log(`Filter applied - ${visibleCount} rows visible out of ${rows.length}`);
    }
    
    function resetFilters() {
        if (searchFilter) searchFilter.value = '';
        if (countryFilter) countryFilter.value = '';
        
        // Show all rows
        const table = outputContainer.querySelector('table');
        if (table) {
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                row.classList.remove('filtered');
            });
        }
        
        console.log("Filters reset - all rows visible");
    }
    
    function sortTable(columnIndex) {
        const table = outputContainer.querySelector('table');
        if (!table) return;
        
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        // Get current sort direction from the clicked header
        const th = table.querySelector(`th[data-column="${columnIndex}"]`);
        const currentDirection = th.getAttribute('data-sort') === 'asc' ? 'desc' : 'asc';
        
        // Reset all headers
        table.querySelectorAll('th').forEach(header => {
            header.removeAttribute('data-sort');
        });
        
        // Set new direction on clicked header
        th.setAttribute('data-sort', currentDirection);
        
        // Sort rows
        const sortedRows = rows.sort((a, b) => {
            const aValue = a.querySelectorAll('td')[columnIndex].textContent.trim();
            const bValue = b.querySelectorAll('td')[columnIndex].textContent.trim();
            
            // Check if values are numeric
            const aNum = parseFloat(aValue);
            const bNum = parseFloat(bValue);
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return currentDirection === 'asc' ? aNum - bNum : bNum - aNum;
            }
            
            // String comparison
            return currentDirection === 'asc' 
                ? aValue.localeCompare(bValue) 
                : bValue.localeCompare(aValue);
        });
        
        // Remove existing rows
        rows.forEach(row => row.remove());
        
        // Add sorted rows
        sortedRows.forEach(row => {
            tbody.appendChild(row);
        });
        
        console.log(`Table sorted by column ${columnIndex} in ${currentDirection} order`);
    }
});
