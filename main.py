from database import DEFAULT_DB_PATH, FinanceDB


def main() -> None:
    db = FinanceDB(DEFAULT_DB_PATH)
    db.initialize()


if __name__ == "__main__":
    main()
