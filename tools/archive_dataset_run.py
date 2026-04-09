import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tools.archive_dataset import DatasetArchiver

if __name__ == "__main__":

    archiver = DatasetArchiver()

    archiver.archive()