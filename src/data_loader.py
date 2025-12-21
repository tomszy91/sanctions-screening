'''
Module for downloading and loading sanctions lists from external sources
'''

import requests
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SanctionsLoader:
    '''
    Downloads and parses sanctions list from configured sources
    '''
    def __init__(self, config):
        '''
        Docstring for __init__
        Initialize loader with configuration
        Args:
            config (dict): configuration dictionary with sanctions sources
        '''
        self.config = config
        self.data_dir = Path('data/sanctions_lists')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def download_un_list(self, url):
        '''
        Download UN sanctions list XML from given URL
        Args:
            url (str): URL to UN XML sanctions list
        Returns:
            str: path to downloaded file
        '''
        logger.info(f"Downloading UN sanctions list from {url}")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            file_path = self.data_dir / 'un_consolidated.xml'
            file_path.write_bytes(response.content)
            
            logger.info(f'Downloaded UN sanctions list to {file_path}')
            return str(file_path)
        
        except requests.exceptions.RequestException as e:
            logger.error(f'Failed to download UN sanctions list: {e}')
            raise
        
    def download_eu_list(self, url):
        '''
        Download Consolidated EU sanctions list XML from given URL
        Args:
            url (str): URL to EU XML sanctions list
        Returns:
            str: path to downloaded file
        '''
        logger.info(f"Downloading EU sanctions list from {url}")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            file_path = self.data_dir / 'eu_consolidated.xml'
            file_path.write_bytes(response.content)
            
            logger.info(f'Downloaded EU sanctions list to {file_path}')
            return str(file_path)
        
        except requests.exceptions.RequestException as e:
            logger.error(f'Failed to download EU sanctions list: {e}')
            raise        
        
    def parse_un_xml(self, xml_path):
        '''
        Docstring for parse_un_xml
        Parse UN XML sanctions list into a DataFrame
        Args:
            xml_path (str): Path to the UN sanctions list XML file
        Returns:
            pd.DataFrame: DataFrame containing parsed sanctions data
        '''
        logger.info(f'Parsing UN sanctions list from {xml_path}')
        
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        entities = []
        # UN XML structure has INDIVIDUAL and ENTITY elements
        for entity in root.findall('.//INDIVIDUAL') + root.findall('.//ENTITY'):
            # Extract name variations
            names = []
            
            if entity.tag == 'INDIVIDUAL':
                kind = 'INDIVIDUAL'
                # Primary name
                first_name = entity.findtext('.//FIRST_NAME', '')
                second_name = entity.findtext('.//SECOND_NAME', '')
                third_name = entity.findtext('.//THIRD_NAME', '')
                fourth_name = entity.findtext('.//FOURTH_NAME', '')
    
                full_name = ' '.join([first_name, second_name, third_name, fourth_name]).strip()
                if full_name:
                    names.append(full_name)
                
            else: # ENTITY
                kind = 'ENTITY'
                # Company name
                entity_name = entity.findtext('.//FIRST_NAME','').strip() # For entities, name is in FIRST_NAME
                if entity_name:
                    names.append(entity_name)
                
            # Aliases
            for alias in entity.findall('.//INDIVIDUAL_ALIAS') + entity.findall('.//ENTITY_ALIAS'):
                alias_name = alias.findtext('.//ALIAS_NAME', '')
                if alias_name:
                    names.append(alias_name)
                    
            # Add all variations as separate records
            for name in names:
                entities.append({
                    'name': name,
                    'reference_number': entity.findtext('.//REFERENCE_NUMBER', ''),
                    'list_type': entity.findtext('.//UN_LIST_TYPE', ''),
                    'source': 'UN',
                    'type': kind
                    })
                
        df = pd.DataFrame(entities)
        logger.info(f'Parsed {len(df)} entities from UN list')
        
        return df
    
    
    def parse_eu_xml(self, xml_path):
        '''
        Parse EU XML sanctions list into a DataFrame
        Args:
            xml_path (str): Path to the EU sanctions list XML file
        Returns:
            pd.DataFrame: DataFrame containing parsed sanctions data
        '''
        logger.info(f'Parsing EU sanctions list from {xml_path}')
        
        tree = ET.parse(xml_path)
        root = tree.getroot()
        

        name_space = {'eu' : 'http://eu.europa.ec/fpi/fsd/export'}
        
        entities = []
        # EU XML structure has sanctionEntity elements
        for entity in root.findall('eu:sanctionEntity', name_space):
            # Get sanctionEntity type
            subject_type = entity.findtext('eu:subjectType/eu:code', default='', namespaces=name_space).lower()
            
            # Get all aliases
            for name_alias in entity.findall('eu:nameAlias', name_space):
                whole_name = name_alias.get('wholeName', '').strip()

                if whole_name:
                    entities.append({
                        'name': whole_name,
                        'reference_number': entity.get('euReferenceNumber',''),
                        'list_type': "EU Consolidated List",
                        'source': "EU",
                        'type': "ENTITY" if subject_type == 'enterprise' else 'INDIVIDUAL'
                    })
            
        df = pd.DataFrame(entities)
        logger.info(f'Parsed {len(df)} entities from EU Consolidated list')
        
        return df
    
    def load_all_lists(self):
        '''
        Docstring for load_all_lists
        Download and load all configured sanctions lists
        Returns:
            pd.DataFrame: combined lists
        '''
        all_sanctions = []
        
        sources = self.config.get('sanctions_sources',{})

        for source_name, source_config in sources.items():
            if not source_config.get('enabled', True):
                continue
            logger.info(f'Processing source: {source_name}')
        
            if source_name == 'un_consolidated':
                xml_path = self.download_un_list(source_config['url'])
                df = self.parse_un_xml(xml_path)
                all_sanctions.append(df)
                
            if source_name == 'eu_consolidated':
                xml_path = self.download_eu_list(source_config['url'])
                df = self.parse_eu_xml(xml_path)
                all_sanctions.append(df)
                
        if not all_sanctions:
            logger.warning('No sanctions lists loaded')
            return pd.DataFrame()
        
        combined = pd.concat(all_sanctions, ignore_index=True)
        logger.info(f'Total sanctions entities loaded: {len(combined)}')           
        
        return combined