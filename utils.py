import bisect
import hashlib
import logging
import random
from os.path import dirname, abspath, join
from bs4 import BeautifulSoup

BASE_DIR = dirname(abspath(__file__))
DEBUG_PROD_SIZE = None  # set to `None` to disable

DEFAULT_ATTR_PATH = join(BASE_DIR, 'data/items_ins_v2_1000.json')
DEFAULT_FILE_PATH = join(BASE_DIR, 'data/items_shuffle_1000.json')

FEAT_CONV = join(BASE_DIR, 'data/feat_conv.pt') # NOT USED in RAGEN version
FEAT_IDS = join(BASE_DIR, 'data/feat_ids.pt') # NOT USED in RAGEN version

HUMAN_ATTR_PATH = join(BASE_DIR, 'data/items_human_ins.json')

def random_idx(cum_weights):
    """Generate random index by sampling uniformly from sum of all weights, then
    selecting the `min` between the position to keep the list sorted (via bisect)
    and the value of the second to last index
    """
    pos = random.uniform(0, cum_weights[-1])
    idx = bisect.bisect(cum_weights, pos)
    idx = min(idx, len(cum_weights) - 2)
    return idx

def setup_logger(session_id, user_log_dir):
    """Creates a log file and logging object for the corresponding session ID"""
    logger = logging.getLogger(session_id)
    formatter = logging.Formatter('%(message)s')
    file_handler = logging.FileHandler(
        user_log_dir / f'{session_id}.jsonl',
        mode='w'
    )
    file_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    return logger

def generate_mturk_code(session_id: str) -> str:
    """Generates a redeem code corresponding to the session ID for an MTurk
    worker once the session is completed
    """
    sha = hashlib.sha1(session_id.encode())
    return sha.hexdigest()[:10].upper()

from bs4 import BeautifulSoup

def html_to_markdown(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    
    markdown = ""
    
    # Convert headings
    for i in range(1, 7):
        for heading in soup.find_all(f'h{i}'):
            markdown += f"{'#' * i} {heading.get_text().strip()}\n\n"
    
    # Convert paragraphs
    for p in soup.find_all('p'):
        markdown += f"{p.get_text().strip()}\n\n"
    
    # Convert links
    for a in soup.find_all('a'):
        markdown += f"[{a.get_text().strip()}]({a.get('href', '')})\n\n"
    
    # Convert inputs
    for inp in soup.find_all('input'):
        markdown += f"[{inp.get('placeholder', 'Input')}]\n\n"
    
    # Convert lists
    for ul in soup.find_all('ul'):
        for li in ul.find_all('li'):
            markdown += f"* {li.get_text().strip()}\n"
        markdown += "\n"
    
    for ol in soup.find_all('ol'):
        for i, li in enumerate(ol.find_all('li')):
            markdown += f"{i+1}. {li.get_text().strip()}\n"
        markdown += "\n"
    
    return markdown.strip()