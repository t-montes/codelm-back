from dotenv import load_dotenv
load_dotenv()

from .gptcall import request as gptcall
from .serpcall import request as serpcall
from .diff import diff, reconstruct, show_diff