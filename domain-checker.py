import nltk
from nltk.corpus import words
import whois
import json
import time
import socket
from pathlib import Path
from typing import Set, List, Dict, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('domain_checker.log'),
        logging.StreamHandler()
    ]
)

class DomainChecker:
    def __init__(self, word_limit: Optional[int] = None):
        self.common_tlds: Set[str] = {"com", "net", "org", "info", "biz", "us", "co", "io", "tech"}
        self.word_limit = word_limit
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize results containers
        self.checked_domains: List[str] = []
        self.available_domains: List[str] = []
        self.unavailable_domains: List[str] = []
        self.error_domains: List[str] = []
        
        # Load existing results if any
        self._load_existing_results()

    def _load_existing_results(self) -> None:
        """Load any existing results from previous runs."""
        for result_type in ['checked', 'available', 'unavailable', 'error']:
            file_path = self.results_dir / f"{result_type}_domains.json"
            if file_path.exists():
                with open(file_path) as f:
                    setattr(self, f"{result_type}_domains", json.load(f))
                logging.info(f"Loaded {len(getattr(self, f'{result_type}_domains'))} {result_type} domains")

    def save_progress(self) -> None:
        """Save current progress to JSON files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for result_type in ['checked', 'available', 'unavailable', 'error']:
            data = getattr(self, f"{result_type}_domains")
            file_path = self.results_dir / f"{result_type}_domains_{timestamp}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        logging.info("Progress saved")

    def split_word(self, word: str) -> List[str]:
        """Generate potential domain splits for the given word with valid TLDs."""
        domains = []
        length = len(word)
        for i in range(1, length):
            left = word[:i]
            right = word[i:]
            if right.lower() in self.common_tlds:
                domains.append(f"{left}.{right}")
        return domains

    def check_domain(self, domain: str) -> Optional[bool]:
        """Check domain availability with retries and exponential backoff."""
        max_attempts = 3
        backoff = 1  # Initial backoff duration in seconds
        
        for attempt in range(max_attempts):
            try:
                socket.setdefaulttimeout(10)
                result = whois.whois(domain)
                
                if result.domain_name:
                    logging.info(f"Domain {domain} is registered")
                    return False
                return True
                
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1}: Error checking {domain}: {str(e)}")
                if attempt < max_attempts - 1:
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    return None
    
    def run(self) -> Dict[str, List[str]]:
        """Run the domain checking process."""
        try:
            logging.info("Starting domain availability check...")
            
            # Download NLTK words dataset if needed
            nltk.download('words', quiet=True)
            word_list = words.words()
            if self.word_limit:
                word_list = word_list[:self.word_limit]
            
            logging.info(f"Processing {len(word_list)} words...")
            
            for i, word in enumerate(word_list, 1):
                if i % 100 == 0:
                    logging.info(f"Processed {i}/{len(word_list)} words")
                    self.save_progress()
                
                for domain in self.split_word(word):
                    if domain in self.checked_domains:
                        continue
                        
                    self.checked_domains.append(domain)
                    domain_status = self.check_domain(domain)
                    
                    if domain_status is True:
                        self.available_domains.append(domain)
                    elif domain_status is False:
                        self.unavailable_domains.append(domain)
                    else:
                        self.error_domains.append(domain)
                    
                    time.sleep(1)  # Rate limiting
            
            self.save_progress()
            logging.info("Domain checking completed")
            
            return {
                'available': self.available_domains,
                'unavailable': self.unavailable_domains,
                'errors': self.error_domains
            }
            
        except KeyboardInterrupt:
            logging.info("Process interrupted by user")
            self.save_progress()
            return {
                'available': self.available_domains,
                'unavailable': self.unavailable_domains,
                'errors': self.error_domains
            }
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            self.save_progress()
            raise

if __name__ == "__main__":
    checker = DomainChecker(word_limit=1000)  # Limit for testing
    results = checker.run()
    
    print("\nResults Summary:")
    print(f"Available domains: {len(results['available'])}")
    print(f"Unavailable domains: {len(results['unavailable'])}")
    print(f"Errors encountered: {len(results['errors'])}")
