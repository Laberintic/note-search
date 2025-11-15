import logging

# Global setup – done once
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    logging.info("Starting application")
    try:
        pass
    except Exception as e:
        logging.critical(f"Unrecoverable error: {e}", exc_info=True)