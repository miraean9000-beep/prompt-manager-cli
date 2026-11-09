import json
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile


CATEGORIES = ["텍스트 생성", "이미지 생성", "영상 생성", "페르소나", "자동화", "기타"]
LEGACY_DATA_FILE = Path(__file__).resolve().with_name("prompts.json")
DATA_FILE = LEGACY_DATA_FILE.parent / "data" / "prompts.json"


def load_default_prompts():
    """저장 파일이 없을 때 쓸 기본 프롬프트를 만든다."""
    return [
        {
            "title": "회의록 요약",
            "content": "회의록을 핵심 결정, 담당자, 마감일로 정리해 주세요.",
            "category": "텍스트 생성",
            "favorite": False,
            "views": 0,
        },
        {
            "title": "제주 여행 포스터",
            "content": "푸른 바다와 현무암 해변을 담은 제주 여행 포스터를 만들어 주세요.",
            "category": "이미지 생성",
            "favorite": False,
            "views": 0,
        },
        {
            "title": "파이썬 학습 코치",
            "content": "초보자의 답을 듣고 다음 힌트를 한 단계씩 주는 코치로 행동해 주세요.",
            "category": "페르소나",
            "favorite": False,
            "views": 0,
        },
    ]


def load_prompts():
    try:
        raw_data = DATA_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        try:
            raw_data = LEGACY_DATA_FILE.read_text(encoding="utf-8")
        except FileNotFoundError:
            prompts = load_default_prompts()
            save_prompts(prompts)
            return prompts
        prompts = parse_prompts(raw_data)
        save_prompts(prompts)
        return prompts
    return parse_prompts(raw_data)


def parse_prompts(raw_data):
    prompts = json.loads(raw_data)
    if not isinstance(prompts, list):
        raise ValueError("프롬프트 저장 형식은 리스트여야 합니다.")
    for prompt in prompts:
        if not isinstance(prompt, dict) or not all(
            isinstance(prompt.get(field), str) for field in ("title", "content", "category")
        ):
            raise ValueError("저장된 프롬프트에 제목, 내용 또는 카테고리가 없습니다.")
        favorite = prompt.setdefault("favorite", False)
        views = prompt.setdefault("views", 0)
        if type(favorite) is not bool or type(views) is not int or views < 0:
            raise ValueError("저장된 즐겨찾기 또는 조회수 형식이 올바르지 않습니다.")
    return prompts


def save_prompts(prompts):
    DATA_FILE.parent.mkdir(exist_ok=True)
    file = NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=DATA_FILE.parent,
        prefix=".prompts-", suffix=".tmp", delete=False,
    )
    temporary_path = Path(file.name)
    try:
        with file:
            json.dump(prompts, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temporary_path.replace(DATA_FILE)
    finally:
        temporary_path.unlink(missing_ok=True)


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


def choose_category(prompts, allow_custom=False, current=None):
    categories = get_categories(prompts)
    for number, category in enumerate(categories, start=1):
        print(f"{number}. {category}")
    if allow_custom:
        print("0. 직접 입력")
    else:
        print("0. 뒤로 가기")
    if current is not None:
        print(f"Enter. 현재 카테고리 유지 [{current}]")
    while True:
        choice = read_action_input("카테고리 번호: ")
        if not choice and current is not None:
            return current
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
        "views": 0,
    })
    save_prompts(prompts)
    print(f"추가 완료: {len(prompts)}번 [{category}] {title}")


def show_rows(rows, empty_message):
    if not rows:
        print(empty_message)
        return
    for number, prompt in rows:
        favorite = "⭐" if prompt["favorite"] else "-"
        print(f"{number}. [{prompt['category']}] {prompt['title']} {favorite} (조회수 {prompt['views']})")


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


def select_prompt_index(prompts):
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
        return index
    print("올바른 프롬프트 번호를 입력해 주세요.")
    return None


def show_detail(prompts):
    index = select_prompt_index(prompts)
    if index is None:
        return
    prompt = prompts[index]
    prompt["views"] += 1
    save_prompts(prompts)
    favorite = "⭐ 등록" if prompt["favorite"] else "미등록"
    print(f"제목: {prompt['title']}")
    print(f"카테고리: {prompt['category']}")
    print(f"즐겨찾기: {favorite}")
    print(f"조회수: {prompt['views']}")
    print(f"내용: {prompt['content']}")


def toggle_favorite(prompts):
    index = select_prompt_index(prompts)
    if index is None:
        return
    prompt = prompts[index]
    prompt["favorite"] = not prompt["favorite"]
    save_prompts(prompts)
    status = "⭐ 즐겨찾기 등록 완료" if prompt["favorite"] else "즐겨찾기 해제 완료"
    print(f"{status}: {prompt['title']}")


def show_favorites(prompts):
    rows = [
        (number, prompt)
        for number, prompt in enumerate(prompts, start=1)
        if prompt["favorite"]
    ]
    show_rows(rows, "즐겨찾기에 등록된 프롬프트가 없습니다.")


def show_top_prompts(prompts):
    rows = sorted(
        enumerate(prompts, start=1),
        key=lambda row: row[1]["views"],
        reverse=True,
    )
    show_rows(rows, "등록된 프롬프트가 없습니다.")


def delete_prompt(prompts):
    index = select_prompt_index(prompts)
    if index is None:
        return
    title = prompts[index]["title"]
    confirmation = read_action_input(f"'{title}'을 삭제할까요? (y/N): ")
    if confirmation.casefold() != "y":
        print("삭제를 취소했습니다.")
        return
    del prompts[index]
    save_prompts(prompts)
    print(f"삭제 완료: {title}")


def edit_prompt(prompts):
    index = select_prompt_index(prompts)
    if index is None:
        return
    prompt = prompts[index]
    print("Enter를 누르면 기존 값을 유지합니다.")
    title = read_action_input(f"제목 [{prompt['title']}]: ") or prompt["title"]
    content = read_action_input(f"내용 [{prompt['content']}]: ") or prompt["content"]
    category = choose_category(prompts, allow_custom=True, current=prompt["category"])
    prompt.update(title=title, content=content, category=category)
    save_prompts(prompts)
    print(f"수정 완료: {index + 1}번 [{category}] {title}")


MENU = {
    "1": ("프롬프트 추가", add_prompt),
    "2": ("전체 목록", show_detail),
    "3": ("카테고리별 조회", show_category),
    "4": ("프롬프트 검색", search_prompt),
    "5": ("프롬프트 상세 보기", show_detail),
    "6": ("즐겨찾기 추가/해제", toggle_favorite),
    "7": ("즐겨찾기 목록", show_favorites),
    "8": ("조회수 TOP 목록", show_top_prompts),
    "9": ("프롬프트 삭제", delete_prompt),
    "10": ("프롬프트 수정", edit_prompt),
}


def show_menu():
    print("\n=== 프롬프트 관리 콘솔 ===")
    for number, (label, _) in MENU.items():
        print(f"{number}. {label}")
    print("0. 종료")


def main():
    prompts = load_prompts()
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
    except (OSError, ValueError) as error:
        sys.exit(f"프롬프트 파일을 읽거나 저장하지 못했습니다. {error}")
