package site.to_mato.llm.prompt.tempate;

import org.springframework.stereotype.Component;
import site.to_mato.llm.prompt.model.ChildTopicPromptDto;
import site.to_mato.llm.prompt.option.TopicOption;

@Component
public class ChildTopicPromptTemplate {

    public String getSystemPrompt() {
        return """
        당신은 IT 프로젝트 기획 전문가입니다.

        사용자의 팀 상황과 주어진 프로젝트 주제를 기반으로
        현실적이고 실행 가능한 하위 프로젝트 기획안을 작성해야 합니다.

        반드시 아래 규칙을 지켜주세요:
        1. 추상적인 설명이 아닌 실제 구현 가능한 수준으로 작성
        2. 팀 규모와 기간에 맞게 난이도 조절
        3. 결과는 반드시 지정된 출력 형식(JSON)을 따를 것
        4. 불필요한 설명 없이 결과만 출력
        """;
    }

    public String buildUserPrompt(ChildTopicPromptDto data, TopicOption option) {
        String optionPrompt = option != null ? option.buildPrompt() : "";

        return """
        아래 정보를 기반으로 프로젝트 하위 주제를 구체화하세요.

        %s

        %s
        
        [요구사항]
        - 결과는 반드시 JSON 형식응로만 출력하세요.
        - content는 "마크다운 형식의 기획서"로 작성하세요.
        - content에는 다음 내용을 포함하세요:
            1. 프로젝트 개요
            2. 핵심 기능
            3. 기술 스택
            4. 개발 일정
        
        %s

        [출력 형식]
        {
          "title": "하위 주제 제목",
          "content": "마크다운 형식 기획서"
        }
        """.formatted(
                buildTeamInfo(data.team()),
                buildTopicInfo(data.topic()),
                optionPrompt
        );
    }

    private String buildTeamInfo(ChildTopicPromptDto.TeamInfo team) {
        return """
        [팀 정보]
        - 팀원 수: %d명
        - 기술 스택: %s
        - 관심 도메인: %s
        - 개발 기간: %d주
        """.formatted(
                team.memberCount(),
                formatList(team.skills()),
                formatList(team.domains()),
                team.durationWeeks()
        );
    }

    private String buildTopicInfo(ChildTopicPromptDto.TopicInfo topic) {
        return """
        [주제 정보]
        - 제목: %s
        - 설명: %s
        - 난이도: %d
        - 권장 팀 규모: %d명
        - 권장 개발 기간: %d주
        """.formatted(
                topic.title(),
                topic.description(),
                topic.difficulty(),
                topic.recommendedTeamSize(),
                topic.expectedDurationWeek()
        );
    }

    private String formatList(java.util.List<String> list) {
        return (list == null || list.isEmpty()) ? "없음" : String.join(", ", list);
    }
}
