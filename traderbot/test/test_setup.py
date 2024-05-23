import sys
import os
import django

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "traderbot.settings")
django.setup()
