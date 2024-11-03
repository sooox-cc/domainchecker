# Domain Availability Checker

A Python tool that analyzes the NLTK words corpus to find available domain names by intelligently splitting words and checking their availability with common TLDs (Top Level Domains).

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)

![WTFPL Licence](http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-4.png)

## 🚀 Features

- Intelligently splits words to find potential domain names
- Checks domain availability across multiple TLDs
- Implements robust error handling and retry mechanisms
- Saves progress automatically and can resume interrupted checks
- Comprehensive logging system
- Rate limiting to respect WHOIS servers
- Progress tracking with detailed statistics

## 📋 Requirements

- Python 3.8 or higher
- Required packages listed in `requirements.txt`

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/sooox-cc/domainchecker.git
cd domain-checker
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Download NLTK data (the script will do this automatically on first run):
```python
import nltk
nltk.download('words')
```

## 💻 Usage

Basic usage:
```python
from domain_checker import DomainChecker

# Initialize checker with default settings
checker = DomainChecker()
results = checker.run()

# Or specify a word limit for testing
checker = DomainChecker(word_limit=1000)
results = checker.run()
```

The script will create a `results` directory containing:
- JSON files with available domains
- JSON files with unavailable domains
- JSON files with domains that encountered errors
- A detailed log file

## 📊 Output Structure

Results are saved in the following format:
```json
{
    "available": ["domain1.com", "domain2.net", ...],
    "unavailable": ["taken1.com", "taken2.org", ...],
    "errors": ["error1.com", "error2.io", ...]
}
```

## ⚠️ Rate Limiting

The script implements a 1-second delay between WHOIS requests to avoid rate limiting. You can adjust this in the code if needed, but be cautious about making too many rapid requests.

## 📝 Logging

Logs are saved to `domain_checker.log` and include:
- Start/end of checking process
- Individual domain check results
- Errors and exceptions
- Progress updates

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
