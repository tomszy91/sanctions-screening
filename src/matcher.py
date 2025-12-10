'''
Docstring for src.matcher
Fuzzy matching logic for comparing company names against sanctions list
'''

import pandas as pd
from rapidfuzz import fuzz, process
import logging

logger = logging.getLogger(__name__)

class SanctionsMatcher:
    '''
    Docstring for SanctionsMatcher
    Performs fuzzy matching between company names and sanctions lists
    '''
    
    def __init__(self, config):
        '''
        Docstring for __init
        
        config (dict): Configuration with matching parameters
        '''
        self.threshold = config['matching']['threshold']
        self.algorithm = config['matching']['algorithm']
        logger.info(f'Matcher initialized with threshold={self.threshold} and algorithm={self.algorithm}')
        
    def normalize_name(self, name):
        '''
        Docstring for normalize_name
        Normalize company name for better matching
        Args:
            name (str): Company name    
        Returns:
            str: Normalized name
        '''
        if pd.isna(name):
            return ""
        
        # Convert to uppercase
        name = str(name).upper()
        
        # Remove common legal suffixes
        suffixes = [
            'LTD', 'LIMITED', 'INC', 'INCORPORATED', 'CORP', 'CORPORATION',
            'LLC', 'GMBH', 'SA', 'SPA', 'AG', 'NV', 'BV', 'SP Z OO', 'SP. Z O.O.'
        ]
        
        for suffix in suffixes:
            name = name.replace(f' {suffix}', '')
            name = name.replace(f'.{suffix}', '')
            
        # Remove dots
        name = name.replace('.', '').replace(',', '').replace('-', '')
        
        # Remove extra spaces
        name = ' '.join(name.split())
        
        return name
    
    def calculate_similarity(self, name1, name2):
        '''
        Docstring for calculate_similarity
        Calculate similarity score between two names.
        
        Args:
            name1 (str): First name
            name2 (str): Second name
        Returns:
            float: Similarity score (0-100)
        '''
        if self.algorithm == 'token_sort_ratio':
            return fuzz.token_sort_ratio(name1, name2)
        elif self.algorithm == 'token_set_ratio':
            return fuzz.token_set_ratio(name1, name2)
        else:
            return fuzz.ratio(name1, name2)
        
    def match_single_company(self, company_name, sanctions_df):
        '''
        Docstring for match_single_company
        Match a single company against sanctions list
        
        Args:
            company_name (str): Company name to check
            sanctions_df (pd.DataFrame): Sanctions list
            
        Returns:
            list: List of matches with scores
        '''
        
        normalized_company = self.normalize_name(company_name)
        
        if not normalized_company:
            return []
        
        matches = []
        # Compare against all sanctioned entities
        for idx, row in sanctions_df.iterrows():
            sanctions_name = self.normalize_name(row['name'])
            
            if not sanctions_name:
                continue
            
            score = self.calculate_similarity(normalized_company, sanctions_name)
            
            if score >= self.threshold:
                matches.append({
                    'sanctions_name': row['name'],
                    'normalized_sanctions_name': sanctions_name,
                    'type': row.get('type', 'UNKNOWN'),
                    'reference_number': row['reference_number'],
                    'list_type': row['list_type'],
                    'source': row['source'],
                    'score': score
                })
                
        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches
    
    def match_companies(self, companies_df, sanctions_df):
        '''
        Docstring for match_companies
        Match all companies against sanctions list.
        Args:
            companies_df (pd.DataFrame): Companies to check
            sanctions_df (pd.DataFrame): Sanctions list
            
        Returns:
            pd.DataFrame: Results with matches
        '''
        # Note: We match against both ENTITY and INDIVIDUAL types
        # Reason: A company may be owned/controlled by a sanctioned individual
        # This increases false positives but reduces compliance risk
    
        # if 'type' in sanctions_df.columns:
        #     entity_sanctions = sanctions_df[sanctions_df['type'] == 'ENTITY'].copy()
        #     logger.info(f'Filtered to {len(entity_sanctions)} sanctioned entities from {len(sanctions_df)} total')
        # else:
        #     entity_sanctions = sanctions_df
        #     logger.warning("'type' column not found in sanctions data")
        
        logger.info(f'Matching {len(companies_df)} companies against {len(sanctions_df)} sanctioned entities')

        results = []
        
        for idx, company in companies_df.iterrows():
            company_id = company.get('company_id', idx)
            company_name = company.get('company_name', '')
            country = company.get('country', '')
            
            logger.info(f'Checking company: {company_name}')
            
            matches = self.match_single_company(company_name, sanctions_df)
            
            if matches:
                logger.warning(f'POTENTIAL MATCH FOUND for {company_name}: {len(matches)} matches')
                
                for match in matches:
                    results.append({
                        'company_id': company_id,
                        'company_name': company_name,
                        'country': country,
                        'match_found': True,
                        'sanctions_name': match['sanctions_name'],
                        'reference_number': match['reference_number'],
                        'list_type': match['list_type'],
                        'source': match['source'],
                        'match_score': match['score']
                    })        
            else:
                # no match found
                results.append({
                    'company_id': company_id,
                    'company_name': company_name,
                    'country': country,
                    'match_found': False,
                    'sanctions_name': None,
                    'reference_number': None,
                    'list_type': None,
                    'source': None,
                    'match_score': None
                })
            
        results_df = pd.DataFrame(results)
        
        matches_count = results_df['match_found'].sum()
        logger.info(f'Matching complete. Found {matches_count} potential matches out of {len(companies_df)} companies')
        
        return results_df