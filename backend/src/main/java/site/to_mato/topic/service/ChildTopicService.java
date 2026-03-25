package site.to_mato.topic.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.common.ai.OpenAiClient;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.project.entity.Project;
import site.to_mato.project.repository.ProjectDomainRepository;
import site.to_mato.project.repository.ProjectMemberRepository;
import site.to_mato.project.repository.ProjectRepository;
import site.to_mato.project.repository.ProjectSkillRepository;
import site.to_mato.topic.dto.response.RefinedTopicResponse;
import site.to_mato.topic.entity.ChildTopic;
import site.to_mato.topic.entity.Topic;
import site.to_mato.topic.repository.ChildTopicRepository;
import site.to_mato.topic.repository.TopicRepository;

import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChildTopicService {

    private final ProjectRepository projectRepository;
    private final ProjectMemberRepository projectMemberRepository;
    private final ProjectSkillRepository projectSkillRepository;
    private final ProjectDomainRepository projectDomainRepository;
    private final TopicRepository topicRepository;
    private final ChildTopicRepository childTopicRepository;
    private final OpenAiClient openAiClient;
    private final ObjectMapper objectMapper;
    private final String systemPrompt = "당신은 IT 프로젝트 기획자입니다. 주어진 대주제(Topic) 원본 정보를 사용자 팀의 상황(인원, 선호 기술 스택, 도메인, 개발 기간)에 맞게 1페이지 분량으로 상세히 구체화하여 하위 주제 기획안을 작성해야 합니다. " +
            " 반드시 사용자가 요구한 출력 형식을 정확히 지켜야 합니다. 형식을 지키지 않으면 잘못된 응답입니다.";

    @Transactional
    public RefinedTopicResponse refineTopic(Long userId, Long projectId, Long topicId) {
        Project project = getProjectWithAuthCheck(projectId, userId);
        Topic topic = getTopic(topicId);

        String userPrompt = buildUserPrompt(project, topic);


        String llmResponse = openAiClient.generateText(systemPrompt, userPrompt);

        String fallbackTitle = "구체화된 " + topic.getTitle();
        ChildTopicParser.ParsedTopic parsed = ChildTopicParser.parse(llmResponse, fallbackTitle, objectMapper);

        ChildTopic childTopic = ChildTopic.create(parsed.title(), parsed.content(), topic, project);
        ChildTopic savedChildTopic = childTopicRepository.save(childTopic);

        return RefinedTopicResponse.from(savedChildTopic);
    }

    public String refineMockTopic() {
        String userPrompt = buildMockPrompt();

        String llmResponse = openAiClient.generateText(systemPrompt, userPrompt);
        return llmResponse;
    }

    private Project getProjectWithAuthCheck(Long projectId, Long userId) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PROJECT_NOT_FOUND));

        if (!projectMemberRepository.existsByProject_IdAndUser_Id(projectId, userId)) {
            throw new BusinessException(ErrorCode.PROJECT_FORBIDDEN);
        }
        return project;
    }

    private Topic getTopic(Long topicId) {
        return topicRepository.findById(topicId)
                .orElseThrow(() -> new BusinessException(ErrorCode.TOPIC_NOT_FOUND));
    }

    private String buildUserPrompt(Project project, Topic topic) {
        long memberCount = projectMemberRepository.countMembersByProjectIds(List.of(project.getId()))
                .stream().mapToLong(row -> (Long) row[1]).sum();
        if (memberCount == 0) memberCount = 1;

        List<String> skills = projectSkillRepository.findAllByProject_Id(project.getId()).stream()
                .map(ps -> ps.getSkill().getName())
                .collect(Collectors.toList());

        List<String> domains = projectDomainRepository.findByProjectId(project.getId()).stream()
                .map(pd -> pd.getDomain().getName())
                .collect(Collectors.toList());

        long expectedDurationDays = 0;
        if (project.getStartedAt() != null && project.getDueAt() != null) {
            expectedDurationDays = ChronoUnit.DAYS.between(project.getStartedAt(), project.getDueAt());
        }

        return String.format(
                "다음 정보를 바탕으로 팀에 특화된 프로젝트 기획안을 작성해주세요.\n" +
                        "[원본 주제 정보]\n제목: %s\n설명: %s\n난이도: %d\n권장 팀 규모: %d명\n권장 개발 기간: %d주\n\n" +
                        "[팀 정보]\n실제 팀원 수: %d명\n선호 기술 스택: %s\n관심 도메인: %s\n실제 개발 가용 기간: %d일\n\n" +
                        "\\n\\n요구사항:\\n1. 반드시 JSON 객체 하나만 반환하세요." +
                        "\\n2. JSON 외의 텍스트는 절대 포함하지 마세요." +
                        "\\n3. 코드블록(```)을 절대 사용하지 마세요." +
                        "\\n4. title은 순수 텍스트 문자열로 작성하세요." +
                        "\\n5. content는 마크다운 형식으로 작성하세요." +
                        "\\n6. content에는 실제 줄바꿈을 사용하세요. (\\\\n 문자열 사용 금지)" +
                        "\\n7. JSON의 key는 반드시 title, content 두 개만 사용하세요." +
                        "\\n\\n출력 형식:\\n{\\\"title\\\": \\\"string\\\", \\\"content\\\": \\\"markdown\\\"}\"\n" +
                        "}",
                topic.getTitle(), topic.getDescription(), topic.getDifficulty(), topic.getRecommendedTeamSize(), topic.getExpectedDurationWeek(),
                memberCount, String.join(", ", skills), String.join(", ", domains), expectedDurationDays
        );
    }

    private String buildMockPrompt() {
        String topicTitle = "우주 궤도 추천 시스템";
        String topicDescription = "이 프로젝트는 React와 Node.js를 활용하여 우주 궤도 추천 시스템을 개발하는 것으로," +
                " 사용자 인터페이스와 백엔드 API를 포함합니다. " +
                "MongoDB를 데이터 저장소로 사용하며, 환경 변수로 연결 정보를 관리합니다. " +
                "프론트엔드와 백엔드 모두 npm 또는 yarn으로 설치 및 실행할 수 있습니다.";
        int topicDifficulty = 2;
        int topicTeamSize = 2;
        int topicDuration = 8;

        int memberCount = 3;
        String skills = "react, spring";
        String domains = "금융업, 서비스업";
        int duration = 4;


        return String.format(
                "다음 정보를 바탕으로 팀에 특화된 프로젝트 기획안을 작성해주세요.\n" +
                        "[원본 주제 정보]\n제목: %s\n설명: %s\n난이도: %d\n권장 팀 규모: %d명\n권장 개발 기간: %d주\n\n" +
                        "[팀 정보]\n실제 팀원 수: %d명\n선호 기술 스택: %s\n관심 도메인: %s\n실제 개발 가용 기간: %d주\n\n" +
                        "\\n\\n요구사항:\\n1. 반드시 JSON 객체 하나만 반환하세요." +
                        "\\n2. JSON 외의 텍스트는 절대 포함하지 마세요." +
                        "\\n3. 코드블록(```)을 절대 사용하지 마세요." +
                        "\\n4. title은 순수 텍스트 문자열로 작성하세요." +
                        "\\n5. content는 마크다운 형식으로 작성하세요." +
                        "\\n6. content에는 실제 줄바꿈을 사용하세요. (\\\\n 문자열 사용 금지)" +
                        "\\n7. JSON의 key는 반드시 title, content 두 개만 사용하세요." +
                        "\\n\\n출력 형식:\\n{\\\"title\\\": \\\"string\\\", \\\"content\\\": \\\"markdown\\\"}\"\n" +
                        "}",
                topicTitle, topicDescription, topicDifficulty, topicTeamSize, topicDuration,
                memberCount, skills, domains, duration
        );
    }
}
