from app.pipeline import run_pipeline


def main():
    while True:
        user_input = input()
        if user_input == "exit":
            break
        print(run_pipeline(user_input))


if __name__ == "__main__":
    main()

