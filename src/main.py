'''
Docstring for src.main
Main script for sanctions screening
'''

import yaml
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime

from data_loader import SanctionsLoader
from matcher import SanctionsMatcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path='config.yaml'):
    '''
    Docstring for load_config
    Load configuration from YAML file
    '''
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def main():
    '''
    Docstring for main
    Main execution flow
    '''
    logger.info('Starting sanctions screening system')
    
    # Load config
    config = load_config()
    logger.info('Configuration loaded')
    
    # Download and load sanctions lists
    loader = SanctionsLoader(config)
    sanctions_df = loader.load_all_lists()
    
    if sanctions_df.empty:
        logger.error('No sanctions data loaded. Exiting.')
        return
    
    logger.info(f'Loaded {len(sanctions_df)} sanctions records')
    
    # Check type distribution
    if 'type' in sanctions_df.columns:
        type_counts = sanctions_df['type'].value_counts()
        logger.info(f'Sanctions breakdown: {type_counts.to_dict()}')
                
    # Load companies to check
    companies_file = config['input']['companies_file']
    logger.info(f'Loading companies from {companies_file}')
    
    companies_df = pd.read_csv(companies_file)
    logger.info(f'Loaded {len(companies_df)} companies to screen')
    
    # Perform matching
    matcher = SanctionsMatcher(config)
    results_df = matcher.match_companies(companies_df, sanctions_df)
            
    # Save results
    output_dir = Path(config['output']['report_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = output_dir / f'screening_results_{timestamp}.csv'
    results_df.to_csv(results_file, index=False)
    
    logger.info(f'Reults saved to {results_file}')
    
    # Summary
    matches = results_df[results_df['match_found'] == True]
    unique_matched_companies = matches['company_id'].nunique()  # Zlicz unikalne firmy z matchem
    clean_companies = len(companies_df) - unique_matched_companies
    
    print("\n" + "="*80)
    print("SANCTIONS SCREENING SUMMARY")
    print("="*80)
    print(f"Total companies screened: {len(companies_df)}")
    print(f"Companies with potential matches: {unique_matched_companies}")
    print(f"Total match records (including aliases): {len(matches)}")
    print(f"Clean companies: {clean_companies}")
    print("="*80)
    
    if not matches.empty:
        print("\nPOTENTIAL MATCHES:")
        print(matches[['company_name', 'sanctions_name', 'match_score', 'reference_number']].to_string(index=False)) 
    
    logger.info('Sanctions screening system completed successfully')



if __name__ == '__main__':
    main()