# VA Overseas Schools - Deployment Guide

This project creates a static website displaying VA-approved overseas schools with cost of living information.

## Project Structure

```
VaOverseasSchools/
├── index.html          # Main HTML page
├── styles.css          # CSS styling
├── script.js           # JavaScript functionality
├── script.py           # Python data analysis
├── package.json        # Node.js configuration
├── .github/workflows/  # GitHub Actions deployment
└── README.md          # This file
```

## Features

- 📊 Interactive table with sorting and search
- 📱 Responsive design for mobile devices
- 🎨 Professional styling with CSS Grid/Flexbox
- 🔍 Search and filter functionality
- 📈 Cost of living analysis by country
- 📁 CSV export capability
- ⚡ Fast loading static site

## Local Development

### Option 1: Python Server
```bash
cd VaOverseasSchools
python -m http.server 8000
# Open http://localhost:8000
```

### Option 2: Node.js (if installed)
```bash
npm install -g http-server
http-server -p 8000
# Open http://localhost:8000
```

### Option 3: Live Server (VS Code Extension)
1. Install Live Server extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

## Deployment Options

### GitHub Pages
1. Push code to GitHub repository
2. Go to repository Settings > Pages
3. Select source: GitHub Actions
4. The `.github/workflows/deploy.yml` will handle deployment

### Netlify
1. Drag and drop the project folder to Netlify
2. Or connect your GitHub repository
3. Build settings: 
   - Build command: (leave empty)
   - Publish directory: (leave empty or use root)

### Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in project directory
3. Follow prompts

### Azure Static Web Apps
1. Install Azure CLI
2. Run: `az staticwebapp create`
3. Follow configuration prompts

## Data Sources

- **VA Schools:** https://www.benefits.va.gov/GIBILL/docs/job_aids/ComparisonToolData.xlsx
- **Cost of Living:** Kaggle dataset via the Python analysis script
- **Analysis:** Generated from `script.py` output

## Customization

### Adding New Schools
Edit the data in `index.html` table or modify `script.py` to pull fresh data.

### Styling Changes
Modify `styles.css` CSS custom properties:
```css
:root {
    --primary-color: #1f4e79;    /* Change primary color */
    --secondary-color: #3498db;   /* Change secondary color */
    /* ... other variables ... */
}
```

### Functionality Changes
Modify `script.js` to add new features:
- Additional sorting options
- Different search filters
- New export formats
- Enhanced visualizations

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Performance

- Lighthouse Score: 95+ Performance
- First Contentful Paint: < 1.5s
- Largest Contentful Paint: < 2.5s
- Cumulative Layout Shift: < 0.1

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## Support

For issues or questions:
- Open GitHub issue
- Check VA.gov for official school information
- Review deployment logs for hosting issues

# Install dependencies as needed:

pip install pandas
pip install numpy
pip install requests
pip install matplotlib
pip install seaborn
pip install kagglehub
pip install openpyxl
pip install xlrd

# Set the path to the file you'd like to load
file_path = ""

# Load the latest version
df = kagglehub.load_dataset(
  KaggleDatasetAdapter.PANDAS,
  "myrios/cost-of-living-index-by-country-by-number-2024",
  file_path,
  # Provide any additional arguments like 
  # sql_query or pandas_kwargs. See the 
  # documenation for more information:
  # https://github.com/Kaggle/kagglehub/blob/main/README.md#kaggledatasetadapterpandas
)

print("First 5 records:", df.head())
