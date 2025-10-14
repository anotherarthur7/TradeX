#!/usr/bin/env python
import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tradeapp.settings'  # Your project name
    django.setup()
    
    from django.test.runner import DiscoverRunner
    
    test_runner = DiscoverRunner(
        pattern="test_*.py",
        verbosity=2,
        interactive=True,
        failfast=False
    )
    
    # Fix the path - adjust based on your actual app name
    failures = test_runner.run_tests(["your_app_name.tests"])  # Change "your_app_name" to your actual app name
    sys.exit(bool(failures))