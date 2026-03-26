package site.to_mato.llm.prompt.option;

public enum TopicOption {

    TECH_CHALLENGE,
    PRACTICAL_SERVICE,
    CREATIVE_IDEA,
    PORTFOLIO_IMPACT;

    public String buildPrompt() {
        return switch (this) {
            case TECH_CHALLENGE -> """
                [추가 요구사항 - 기술 도전형]
                - 최신 기술 또는 복잡한 시스템 설계를 포함하세요.
                - 기술적 난이도가 있는 요소를 반드시 포함하세요.
                - content에 "기술적 도전 요소" 항목을 추가하세요.
            """;
            case PRACTICAL_SERVICE -> """
                [추가 요구사항 - 실용 서비스형]
                - 실제 사용자 문제 해결에 집중하세요.
                - content에 반드시 "타겟 사용자"와 "사용 시나리오"를 포함하세요.
            """;
            case CREATIVE_IDEA -> """
                [추가 요구사항 - 창의 아이디어형]
                - 기존 서비스와 차별화된 새로운 컨셉을 포함하세요.
                - 예상치 못한 조합이나 접근 방식을 활용하세요.
                - content에 "차별화 포인트"를 명확히 작성하세요.
            """;
            case PORTFOLIO_IMPACT -> """
                [추가 요구사항 - 포트폴리오 임팩트형]
                - 면접에서 설명하기 좋은 기술적 포인트를 포함하세요.
                - 시스템 구조, 확장성, 성능 등을 강조하세요.
                - content에 "기술적 강조 포인트 (면접 어필 요소)" 항목을 포함하세요.
            """;
        };
    }
}
