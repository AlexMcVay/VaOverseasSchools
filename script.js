document.addEventListener('DOMContentLoaded', function() {
    // Load data and then initialize the application
    loadSchoolsData().then(() => {
        initializeApp();
    }).catch(error => {
        console.error('Error loading data:', error);
        // Initialize app anyway with existing static data
        initializeApp();
    });
});

// Data Loading Functions
async function loadSchoolsData() {
    try {
        // Show loading indicator
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = 'flex';
        }

        console.log('Loading schools data...');
        
        let data;
        try {
            // Try to fetch the JSON file first
            const response = await fetch('comprehensive_va_analysis.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            data = await response.json();
            console.log('Data loaded from JSON file');
        } catch (fetchError) {
            // If fetch fails (e.g., CORS issues with file:// protocol), use fallback data
            console.log('Fetch failed, using fallback data:', fetchError.message);
            if (typeof VA_SCHOOLS_DATA !== 'undefined') {
                data = VA_SCHOOLS_DATA;
                console.log('Using embedded fallback data');
            } else {
                throw new Error('No data source available');
            }
        }
        
        // Update the summary statistics
        updateSummaryStats(data);
        
        // Update the schools table
        updateSchoolsTable(data);
        
        // Update country analysis
        updateCountryAnalysis(data);
        
        console.log('Data loaded successfully');
        
        // Hide loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
        
        return data;
    } catch (error) {
        console.error('Error loading schools data:', error);
        
        // Hide loading indicator on error
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
        
        throw error;
    }
}

function updateSummaryStats(data) {
    const overview = data.overseas_analysis;
    
    // Update stat cards
    const statCards = document.querySelectorAll('.stat-card h3');
    if (statCards.length >= 3) {
        statCards[0].textContent = overview.total_schools || '51';
        statCards[1].textContent = Object.keys(overview.countries || {}).length || '10';
        statCards[2].textContent = overview.school_types?.Private || '33';
    }
}

let currentPage = 1;
const pageSize = 100;
let currentSchoolsList = [];

function updateSchoolsTable(data) {
    const tableBody = document.querySelector('#schoolsTable tbody');
    if (!tableBody || !data.overseas_analysis?.schools_list) {
        console.warn('Table body or schools data not found');
        return;
    }
    currentSchoolsList = data.overseas_analysis.schools_list;
    currentPage = 1;
    renderSchoolsPage();
    addShowMoreButton();
    console.log(`Updated table with ${currentSchoolsList.length} schools (paginated)`);
}

function renderSchoolsPage() {
    const tableBody = document.querySelector('#schoolsTable tbody');
    if (!tableBody) return;
    tableBody.innerHTML = '';
    const start = (currentPage - 1) * pageSize;
    const end = Math.min(start + pageSize, currentSchoolsList.length);
    for (let i = start; i < end; i++) {
        const school = currentSchoolsList[i];
        const row = document.createElement('tr');
        const costIndex = getCostOfLivingIndex(school.COUNTRY);
        row.innerHTML = `
            <td>${school.INSTITUTION || 'N/A'}</td>
            <td>${school.CITY || 'N/A'}</td>
            <td>${school.COUNTRY || 'N/A'}</td>
            <td>${school.TYPE || 'N/A'}</td>
            <td>${costIndex}</td>
        `;
        tableBody.appendChild(row);
    }
}

function addShowMoreButton() {
    let btn = document.getElementById('showMoreSchools');
    if (btn) btn.remove();
    const schoolsSection = document.querySelector('.schools-table');
    if (!schoolsSection) return;
    if (currentPage * pageSize < currentSchoolsList.length) {
        btn = document.createElement('button');
        btn.id = 'showMoreSchools';
        btn.textContent = 'Show More';
        btn.className = 'export-button';
        btn.style.margin = '20px auto 0 auto';
        btn.style.display = 'block';
        btn.onclick = function() {
            currentPage++;
            renderSchoolsPage();
            addShowMoreButton();
        };
        schoolsSection.appendChild(btn);
    }
}

function updateCountryAnalysis(data) {
    const countryGrid = document.querySelector('.country-grid');
    if (!countryGrid || !data.overseas_analysis?.countries) {
        console.warn('Country grid or countries data not found');
        return;
    }
    
    // Clear existing cards
    countryGrid.innerHTML = '';
    
    // Add new country cards from JSON data
    Object.entries(data.overseas_analysis.countries).forEach(([country, count]) => {
        const card = document.createElement('div');
        card.className = 'country-card';
        card.innerHTML = `
            <h3>${country}</h3>
            <p class="school-count">${count} school${count !== 1 ? 's' : ''}</p>
        `;
        countryGrid.appendChild(card);
    });
    
    console.log(`Updated country analysis with ${Object.keys(data.overseas_analysis.countries).length} countries`);
}

function getCostOfLivingIndex(country) {
    // Cost of living index mapping (you can extend this or load from another JSON file)
    const costMapping = {
        'United Kingdom': '62.0',
        'Germany': '62.2',
        'France': '63.7',
        'Japan': '46.1',
        'Australia': '70.2',
        'Canada': '64.8',
        'Spain': '47.3',
        'Italy': '56.2',
        'Switzerland': '101.1',
        'Netherlands': '63.1'
    };
    
    return costMapping[country] || 'N/A';
}

function initializeApp() {
    // Add table sorting functionality
    addTableSorting();
    
    // Add search/filter functionality
    addSearchFilter();
    
    // Add responsive table wrapper
    makeTablesResponsive();
    
    // Add smooth scrolling for anchor links
    addSmoothScrolling();
    
    // Initialize tooltips or additional interactive elements
    initializeTooltips();
    
    // Add export functionality
    addExportButton();
}

function addTableSorting() {
    const table = document.getElementById('schoolsTable');
    if (!table) return;
    
    const headers = table.querySelectorAll('th');
    
    headers.forEach((header, index) => {
        header.style.cursor = 'pointer';
        header.style.userSelect = 'none';
        header.title = 'Click to sort';
        
        // Add sort indicator
        const sortIndicator = document.createElement('span');
        sortIndicator.className = 'sort-indicator';
        sortIndicator.innerHTML = ' ↕️';
        header.appendChild(sortIndicator);
        
        header.addEventListener('click', () => {
            sortTable(table, index);
            updateSortIndicators(headers, header, index);
        });
    });
}

function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Determine if this column is currently sorted
    const currentSort = table.dataset.sortColumn;
    const currentDirection = table.dataset.sortDirection || 'asc';
    const newDirection = (currentSort == columnIndex && currentDirection === 'asc') ? 'desc' : 'asc';
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        // Check if values are numeric
        const aNum = parseFloat(aValue.replace(/[$,]/g, ''));
        const bNum = parseFloat(bValue.replace(/[$,]/g, ''));
        
        let comparison = 0;
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            // Numeric comparison
            comparison = aNum - bNum;
        } else {
            // String comparison
            comparison = aValue.localeCompare(bValue);
        }
        
        return newDirection === 'asc' ? comparison : -comparison;
    });
    
    // Update table data attributes
    table.dataset.sortColumn = columnIndex;
    table.dataset.sortDirection = newDirection;
    
    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
}

function updateSortIndicators(headers, activeHeader, activeIndex) {
    headers.forEach((header, index) => {
        const indicator = header.querySelector('.sort-indicator');
        if (index === activeIndex) {
            const direction = activeHeader.closest('table').dataset.sortDirection;
            indicator.innerHTML = direction === 'asc' ? ' ↑' : ' ↓';
            header.style.color = '#3498db';
        } else {
            indicator.innerHTML = ' ↕️';
            header.style.color = '';
        }
    });
}

function addSearchFilter() {
    // Create search input if it doesn't exist
    const schoolsSection = document.querySelector('.schools-table');
    if (!schoolsSection) return;
    
    const searchContainer = document.createElement('div');
    searchContainer.className = 'search-container';
    searchContainer.style.marginBottom = '20px';
    
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.id = 'schoolSearch';
    searchInput.placeholder = 'Search schools, countries, or cities...';
    searchInput.className = 'search-input';
    
    // Style the search input
    searchInput.style.cssText = `
        width: 100%;
        max-width: 400px;
        padding: 12px 20px;
        border: 2px solid #e9ecef;
        border-radius: 25px;
        font-size: 16px;
        outline: none;
        transition: border-color 0.3s ease;
    `;
    
    searchContainer.appendChild(searchInput);
    schoolsSection.insertBefore(searchContainer, schoolsSection.querySelector('.table-container'));
    
    // Add search functionality
    searchInput.addEventListener('input', function() {
        filterTable(this.value);
    });
    
    // Style focus state
    searchInput.addEventListener('focus', function() {
        this.style.borderColor = '#3498db';
    });
    
    searchInput.addEventListener('blur', function() {
        this.style.borderColor = '#e9ecef';
    });
}

function filterTable(searchTerm) {
    const table = document.getElementById('schoolsTable');
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(term)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
    
    // Update visible count
    updateVisibleCount(rows, term);
}

function updateVisibleCount(rows, searchTerm) {
    const visibleRows = Array.from(rows).filter(row => row.style.display !== 'none');
    
    // Create or update count display
    let countDisplay = document.getElementById('search-count');
    if (!countDisplay) {
        countDisplay = document.createElement('div');
        countDisplay.id = 'search-count';
        countDisplay.style.cssText = `
            margin-top: 10px;
            font-size: 14px;
            color: #7f8c8d;
            text-align: center;
        `;
        
        const searchContainer = document.querySelector('.search-container');
        if (searchContainer) {
            searchContainer.appendChild(countDisplay);
        }
    }
    
    if (searchTerm) {
        countDisplay.textContent = `Showing ${visibleRows.length} of ${rows.length} schools`;
    } else {
        countDisplay.textContent = '';
    }
}

function makeTablesResponsive() {
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
        const wrapper = table.parentElement;
        if (!wrapper.classList.contains('table-container')) {
            const newWrapper = document.createElement('div');
            newWrapper.className = 'table-container';
            table.parentNode.insertBefore(newWrapper, table);
            newWrapper.appendChild(table);
        }
    });
}

function addSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function initializeTooltips() {
    // Add tooltips for cost of living indices
    const costCells = document.querySelectorAll('td');
    
    costCells.forEach(cell => {
        const value = parseFloat(cell.textContent);
        if (!isNaN(value) && value > 0 && value < 200) {
            // Assume this is a cost of living index
            cell.title = `Cost of Living Index: ${value} (New York City = 100)`;
            cell.style.cursor = 'help';
        }
    });
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + F to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        const searchInput = document.getElementById('schoolSearch');
        if (searchInput) {
            searchInput.focus();
        }
    }
});

// Export data functionality (optional)
function exportTableData() {
    const table = document.getElementById('schoolsTable');
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    let csvContent = '';
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('th, td');
        const rowData = Array.from(cells).map(cell => {
            return '"' + cell.textContent.replace(/"/g, '""') + '"';
        });
        csvContent += rowData.join(',') + '\n';
    });
    
    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'va_overseas_schools.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Add export button to the page
function addExportButton() {
    const schoolsSection = document.querySelector('.schools-table');
    if (!schoolsSection) return;
    
    const exportButton = document.createElement('button');
    exportButton.textContent = 'Export CSV';
    exportButton.className = 'export-button';
    exportButton.style.cssText = `
        background: #27ae60;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        margin-left: 10px;
        transition: background 0.3s ease;
    `;
    
    exportButton.addEventListener('click', exportTableData);
    exportButton.addEventListener('mouseover', function() {
        this.style.background = '#229954';
    });
    exportButton.addEventListener('mouseout', function() {
        this.style.background = '#27ae60';
    });
    
    const searchContainer = document.querySelector('.search-container');
    if (searchContainer) {
        searchContainer.appendChild(exportButton);
    }
}

// Export button will be added during app initialization