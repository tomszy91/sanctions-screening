# Automated Sanctions Screening System

    A Python-based system for automated screening of companies against international sanctions lists using fuzzy string matching.

## Features

    - Downloads and parses sanctions lists from UN consolidated XML
    - Fuzzy matching algorithm to detect similar company names
    - Distinguishes between sanctioned entities (companies) and individuals
    - Handles multiple name aliases and variations
    - Generates detailed CSV reports with match scores
    - Configurable matching threshold and algorithms

## Technical Stack

    - **Python 3.12+**
    - **pandas** - Data processing
    - **rapidfuzz** - Fuzzy string matching
    - **requests** - API calls
    - **pyyaml** - Configuration management

## Project Structure

    sanctions-screening/
    ├── config.yaml              # Configuration file
    ├── requirements.txt         # Python dependencies
    ├── data/
    │   └── sample_companies.csv # Sample input data
    ├── src/
    │   ├── data_loader.py      # Downloads and parses sanctions lists
    │   ├── matcher.py          # Fuzzy matching logic
    │   └── main.py             # Main orchestration script
    └── outputs/
        └── reports/            # Generated screening results

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tomszy91/sanctions-screening.git
cd sanctions-screening
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Prepare your companies CSV file in `data/sample_companies.csv`:

    csv
    company_id,company_name,country
    1,Example Corp,USA
    2,Test Trading Ltd,UK

2. Run the screening:

    bash
    python src/main.py

3. Check results in `outputs/reports/screening_results_TIMESTAMP.csv`

## Configuration

Edit `config.yaml` to customize:

- **threshold**: Minimum similarity score (0-100). Default: 75
- **algorithm**: Fuzzy matching algorithm. Options: `token_sort_ratio`, `token_set_ratio`
- **sanctions_sources**: Add or remove sanctions list sources

## How It Works

### 1. Data Loading

- Downloads UN consolidated sanctions list (XML format)
- Parses entities and individuals with all name aliases
- Categorizes records by type (ENTITY vs INDIVIDUAL)

### 2. Name Normalization

- Converts to uppercase
- Removes legal suffixes (Ltd, Inc, Corp, etc.)
- Removes punctuation and extra spaces

### 3. Fuzzy Matching

- Compares each company against all sanctioned entities
- Uses token-based similarity scoring
- Returns matches above configured threshold

### 4. Results

- Multiple matches per company (due to aliases)
- Match scores indicate confidence level
- Includes reference numbers for further investigation

## Why This Approach?

**Threshold 75%**: Industry standard for compliance screening. Balances false positives vs false negatives.

**Entity vs Individual**: Companies matched only against sanctioned entities (not individuals) to reduce noise, though configurable for comprehensive screening.

**Token Sort Ratio**: Handles word order variations (e.g., "Smith Trading Company" matches "Trading Company Smith").

## Example Output

Total companies screened: 10
Companies with potential matches: 6
Total match records (including aliases): 19
Clean companies: 4

POTENTIAL MATCHES:
company_name              sanctions_name           match_score  reference_number
Hanifa Money Exchange     Hanifa Money Exchange    100.0        QDe.153
Roshan Trading Company    Roshan Trading Company   100.0        TAe.011

## Limitations

- Requires internet connection to download sanctions lists
- Processing time increases with large company datasets
- Manual review required for matches below 90% confidence

## Future Enhancements

- [ ] HTML report generation
- [ ] Multiple sanctions sources (EU, OFAC)
- [ ] Scheduling/automation support
- [ ] API endpoint for real-time screening
- [ ] Database storage for historical results

## License

MIT License

## Author

Data Analyst with 3.5 years experience in compliance monitoring and automation.
