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
