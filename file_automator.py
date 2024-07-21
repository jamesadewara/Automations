from utils import FileAutomation

def run():
    input_dir = "test/input dir"
    output_dir = "test/output dir"
    config_path = "data/config.json"
    
    file_automation = FileAutomation(input_dir, output_dir, config_path)
    file_automation.organizeFiles()
    # To reverse changes, uncomment the line below
    # file_automation.reverseChanges()

if __name__ == "__main__":
    run()