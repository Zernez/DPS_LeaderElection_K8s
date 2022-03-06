import logging

logging.basicConfig(filename='app.log', force='True', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('metric_info')