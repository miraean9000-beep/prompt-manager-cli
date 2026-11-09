CATEGORIES = ["텍스트 생성", "이미지 생성", "영상 생성", "페르소나", "자동화", "기타"]


def load_default_prompts():
    """실행할 때마다 새 프롬프트 목록을 만든다."""
    return [
        {
            "title": "회의록 요약",
            "content": "회의록을 핵심 결정, 담당자, 마감일로 정리해 주세요.",
            "category": "텍스트 생성",
            "favorite": False,
        },
        {
            "title": "제주 여행 포스터",
            "content": "푸른 바다와 현무암 해변을 담은 제주 여행 포스터를 만들어 주세요.",
            "category": "이미지 생성",
            "favorite": False,
        },
        {
            "title": "파이썬 학습 코치",
            "content": "초보자의 답을 듣고 다음 힌트를 한 단계씩 주는 코치로 행동해 주세요.",
            "category": "페르소나",
            "favorite": False,
        },
    ]


def read_nonempty(message):
    while True:
        value = input(message).strip()
        if value:
            return value
        print("빈 값은 입력할 수 없습니다.")


def get_categories(prompts):
    return list(dict.fromkeys(CATEGORIES + [prompt["category"] for prompt in prompts]))


def choose_category(prompts, allow_custom=False):
    categories = get_categories(prompts)
    for number, category in enumerate(categories, start=1):
        print(f"{number}. {category}")
    if allow_custom:
        print("0. 직접 입력")
    while True:
        choice = input("카테고리 번호: ").strip()
        if allow_custom and choice == "0":
            return read_nonempty("새 카테고리: ")
        try:
            index = int(choice) - 1
        except ValueError:
            index = -1
        if 0 <= index < len(categories):
            return categories[index]
        print("올바른 카테고리 번호를 입력해 주세요.")


def add_prompt(prompts):
    title = read_nonempty("제목: ")
    content = read_nonempty("내용: ")
    category = choose_category(prompts, allow_custom=True)
    prompts.append({
        "title": title,
        "content": content,
        "category": category,
        "favorite": False,
    })
    print(f"'{title}' 프롬프트를 추가했습니다.")


def show_rows(rows, empty_message):
    if not rows:
        print(empty_message)
        return
    for number, prompt in rows:
        favorite = "⭐" if prompt["favorite"] else "-"
        print(f"{number}. [{prompt['category']}] {prompt['title']} {favorite}")


def show_list(prompts):
    show_rows(list(enumerate(prompts, start=1)), "등록된 프롬프트가 없습니다.")


MENU = {
    "1": ("프롬프트 추가", add_prompt),
    "2": ("전체 목록", show_list),
}


def show_menu():
    print("\n=== 프롬프트 관리 콘솔 ===")
    for number, (label, _) in MENU.items():
        print(f"{number}. {label}")
    print("0. 종료")


def main():
    prompts = load_default_prompts()
    while True:
        show_menu()
        choice = input("메뉴 번호: ").strip()
        if choice == "0":
            print("프로그램을 종료합니다.")
            return
        if choice in MENU:
            _, action = MENU[choice]
            action(prompts)
        else:
            print("올바른 메뉴 번호를 입력해 주세요.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n프로그램을 종료합니다.")
