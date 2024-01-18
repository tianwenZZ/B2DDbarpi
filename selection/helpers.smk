"""Helper functions for defining inputs and outputs for rules."""
import os
from os.path import isfile, join
import yaml


OUTPUT_DIR = os.path.join(os.path.dirname(workflow.snakefile), 'output')
TUPLES_DIR = os.path.join(OUTPUT_DIR, 'tuples')


def output_path(path):
    assert not path.startswith('/')
    return os.path.join(OUTPUT_DIR, path)


def tuples_path(path):
    assert not path.startswith('/')
    return os.path.join(TUPLES_DIR, path)
