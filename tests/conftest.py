import os
import sys

# garante que o diretório do projeto esteja no sys.path para que os módulos possam ser importados corretamente
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
