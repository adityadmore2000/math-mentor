import json

from app.pipeline import run_pipeline


def main():
    while True:
        user_input = input().strip()
        if user_input == "exit":
            break
        if not user_input:
            continue
        print(json.dumps(run_pipeline(user_input), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
