import sys
import os

# 加入專案路徑
project_path = '/opt/render/project/src'
sys.path.insert(0, project_path)

# 導入應用
from run import application

if __name__ == '__main__':
    application.run()
