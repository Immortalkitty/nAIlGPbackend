from server import create_app
from config import ProductionConfig

app = create_app(ProductionConfig)
