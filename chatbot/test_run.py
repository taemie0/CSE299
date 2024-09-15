import yaml

# Load model from config
def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    model_name = config.get("model_name")
    print(f"The selected model is: {model_name}")

if __name__ == "__main__":
    main()