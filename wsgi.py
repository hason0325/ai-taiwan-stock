import sys
import os

# 加入專案路徑
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

from run import application

# PythonAnywhere 需要這個
app = application