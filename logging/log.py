import datetime

def log_greenness(greenness):
    timestamp = datetime.datetime.now().isoformat()
    with open("greenness_log.txt", "a") as file:
        for index, g in enumerate(greenness):

            name = name_map.get(f"ROI{index + 1}")

            log_string = f"{timestamp},{name},{g}\n"
            print(f"Logging: {log_string}")
            file.write(f"{timestamp},{name},{g}\n")