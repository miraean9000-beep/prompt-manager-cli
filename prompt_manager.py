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


class ReturnToMenu(Exception):
    """현재 기능을 취소하고 메인 메뉴로 돌아간다."""


def read_action_input(message):
    value = input(f"[뒤로 가기: /뒤로] {message}").strip()
    if value == "/뒤로":
        raise ReturnToMenu
    return value


def read_nonempty(message):
    while True:
        value = read_action_input(message)
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
    else:
        print("0. 뒤로 가기")
    while True:
        choice = read_action_input("카테고리 번호: ")
        if choice == "0":
            if allow_custom:
                return read_nonempty("새 카테고리: ")
            raise ReturnToMenu
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
    print(f"추가 완료: {len(prompts)}번 [{category}] {title}")


def show_rows(rows, empty_message):
    if not rows:
        print(empty_message)
        return
    for number, prompt in rows:
        favorite = "⭐" if prompt["favorite"] else "-"
        print(f"{number}. [{prompt['category']}] {prompt['title']} {favorite}")


def show_list(prompts):
    print(f"등록된 프롬프트: {len(prompts)}개")
    show_rows(list(enumerate(prompts, start=1)), "등록된 프롬프트가 없습니다.")


def show_category(prompts):
    category = choose_category(prompts)
    rows = [
        (number, prompt)
        for number, prompt in enumerate(prompts, start=1)
        if prompt["category"] == category
    ]
    show_rows(rows, "이 카테고리에 등록된 프롬프트가 없습니다.")


def search_prompt(prompts):
    keyword = read_nonempty("검색어: ").casefold()
    rows = [
        (number, prompt)
        for number, prompt in enumerate(prompts, start=1)
        if keyword in prompt["title"].casefold() or keyword in prompt["content"].casefold()
    ]
    show_rows(rows, "검색 결과가 없습니다.")


def select_prompt(prompts):
    show_list(prompts)
    if not prompts:
        return None
    choice = read_action_input("프롬프트 번호 (0. 뒤로 가기): ")
    if choice == "0":
        raise ReturnToMenu
    try:
        index = int(choice) - 1
    except ValueError:
        index = -1
    if 0 <= index < len(prompts):
        return prompts[index]
    print("올바른 프롬프트 번호를 입력해 주세요.")
    return None


def show_detail(prompts):
    prompt = select_prompt(prompts)
    if prompt is None:
        return
    favorite = "⭐ 등록" if prompt["favorite"] else "미등록"
    print(f"제목: {prompt['title']}")
    print(f"카테고리: {prompt['category']}")
    print(f"즐겨찾기: {favorite}")
    print(f"내용: {prompt['content']}")


def toggle_favorite(prompts):
    prompt = select_prompt(prompts)
    if prompt is None:
        return
    prompt["favorite"] = not prompt["favorite"]
    status = "⭐ 즐겨찾기 등록 완료" if prompt["favorite"] else "즐겨찾기 해제 완료"
    print(f"{status}: {prompt['title']}")


def show_favorites(prompts):
    rows = [
        (number, prompt)
        for number, prompt in enumerate(prompts, start=1)
        if prompt["favorite"]
    ]
    show_rows(rows, "즐겨찾기에 등록된 프롬프트가 없습니다.")


MENU = {
    "1": ("프롬프트 추가", add_prompt),
    "2": ("전체 목록", show_detail),
    "3": ("카테고리별 조회", show_category),
    "4": ("프롬프트 검색", search_prompt),
    "5": ("프롬프트 상세 보기", show_detail),
    "6": ("즐겨찾기 추가/해제", toggle_favorite),
    "7": ("즐겨찾기 목록", show_favorites),
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
            label, action = MENU[choice]
            print(f"\n--- {label} ---")
            try:
                action(prompts)
            except ReturnToMenu:
                print("메인 메뉴로 돌아갑니다.")
            else:
                input("\nEnter를 누르면 메인 메뉴로 돌아갑니다. ")
        else:
            print("올바른 메뉴 번호를 입력해 주세요.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n프로그램을 종료합니다.")
