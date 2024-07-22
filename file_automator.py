from utils import FileAutomation

def run():
    input_dir = input("Enter the input directory: ")
    output_dir = input("Enter the output directory: ")
    recover = input("Do you want to reverse chages? (y/n): ").lower()

    # the json file is a template to use
    config_path = "data/config.json"
    
    file_automation = FileAutomation(input_dir, output_dir, config_path)

    # To reverse changes, uncomment the line below
    if recover == "y":
        file_automation.reverseChanges()
    else:
        file_automation.organizeFiles()


if __name__ == "__main__":
    run()