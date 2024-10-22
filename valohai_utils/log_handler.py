import logging
import re
import json


# Function to add a custom logging handler to print logs in JSON format
def start_json_logging():
    log_pattern = re.compile(
        r"(\d{2}:\d{2}:\d{2}) - mmengine - INFO - Epoch\(train\) \[(\d+)\]\[\s*(\d+)/\d+\] lr: ([\d\.e-]+) eta: (.+?) time: ([\d\.]+) data_time: ([\d\.]+) memory: (\d+) grad_norm: ([\d\.]+) loss: ([\d\.]+) loss_cls: ([\d\.]+) loss_bbox: ([\d\.]+) loss_dir: ([\d\.]+)"
    )
    # Custom log handler
    class JSONLogHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            match = log_pattern.search(log_entry)
            if match:
                log_data = {
                    "Timestamp": match.group(1),
                    "Epoch": int(match.group(2)),
                    "Batch": int(match.group(3)),
                    "Learning Rate": float(match.group(4)),
                    "ETA": match.group(5),
                    "Time": float(match.group(6)),
                    "Data Time": float(match.group(7)),
                    "Memory": int(match.group(8)),
                    "Grad Norm": float(match.group(9)),
                    "Loss": float(match.group(10)),
                    "Loss_cls": float(match.group(11)),
                    "Loss_bbox": float(match.group(12)),
                    "Loss_dir": float(match.group(13)),
                }
                print(json.dumps(log_data))

    # Configure logging to add the custom handler
    logger = logging.getLogger("mmengine")
    json_handler = JSONLogHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    json_handler.setFormatter(formatter)

    # Add handler to the logger
    logger.addHandler(json_handler)

    # Set logging level to INFO or DEBUG as per your needs
    logger.setLevel(logging.INFO)