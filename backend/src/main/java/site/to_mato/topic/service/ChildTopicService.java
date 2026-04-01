package site.to_mato.topic.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.llm.client.OpenAiClient;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.llm.parser.ChildTopicParser;
import site.to_mato.project.entity.Project;
import site.to_mato.project.repository.ProjectDomainRepository;
import site.to_mato.project.repository.ProjectMemberRepository;
import site.to_mato.project.repository.ProjectRepository;
import site.to_mato.project.repository.ProjectSkillRepository;
import site.to_mato.llm.prompt.model.ChildTopicPromptDto;
import site.to_mato.recommendation.entity.enums.ActionType;
import site.to_mato.recommendation.service.ActionLogService;
import site.to_mato.topic.dto.response.ChildTopicDetailResponse;
import site.to_mato.topic.dto.response.RefinedTopicResponse;
import site.to_mato.topic.entity.ChildTopic;
import site.to_mato.topic.entity.Topic;
import site.to_mato.llm.prompt.assembler.ChildTopicPromptDtoAssembler;
import site.to_mato.llm.prompt.tempate.ChildTopicPromptTemplate;
import site.to_mato.llm.prompt.option.TopicOption;
import site.to_mato.topic.repository.ChildTopicRepository;
import site.to_mato.topic.repository.TopicRepository;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChildTopicService {

    private final ActionLogService actionLogService;

    private final TopicRepository topicRepository;
    private final ProjectRepository projectRepository;
    private final ChildTopicRepository childTopicRepository;
    private final ProjectMemberRepository projectMemberRepository;

    private final OpenAiClient openAiClient;
    private final ObjectMapper objectMapper;
    private final ChildTopicPromptDtoAssembler assembler;
    private final ChildTopicPromptTemplate promptTemplate;


    @Transactional
    public RefinedTopicResponse refineTopic(Long userId, Long projectId, Long topicId, TopicOption option) {
        Project project = getProjectWithAuthCheck(projectId, userId);
        Topic topic = getTopic(topicId);

        ChildTopicPromptDto childTopicPromptDto = assembler.assemble(project, topic);
        String systemPrompt = promptTemplate.getSystemPrompt();
        String userPrompt = promptTemplate.buildUserPrompt(childTopicPromptDto, option);
        String llmResponse = openAiClient.generateText(systemPrompt, userPrompt);

        String fallbackTitle = "구체화된 " + topic.getTitle();
        ChildTopicParser.ParsedTopic parsed = ChildTopicParser.parse(llmResponse, fallbackTitle, objectMapper);

        ChildTopic childTopic = ChildTopic.create(parsed.title(), parsed.content(), topic, project);
        ChildTopic savedChildTopic = childTopicRepository.save(childTopic);

        actionLogService.createActionLog(
                userId,
                projectId,
                topicId,
                ActionType.VIEW_SPECIFICATION
        );

        return RefinedTopicResponse.from(savedChildTopic);
    }

    @Transactional(readOnly = true)
    public ChildTopicDetailResponse getChildTopic(Long userId, Long projectId, Long childTopicId) {
        getProjectWithAuthCheck(projectId, userId);

        ChildTopic childTopic = childTopicRepository.findById(childTopicId)
                .orElseThrow(() -> new BusinessException(ErrorCode.CHILD_TOPIC_NOT_FOUND));

        if (!childTopic.getProject().getId().equals(projectId)) {
            throw new BusinessException(ErrorCode.PROJECT_FORBIDDEN);
        }

        return ChildTopicDetailResponse.from(childTopic);
    }

    @Transactional
    public void deleteChildTopic(Long userId, Long projectId, Long childTopicId) {
        getProjectWithAuthCheck(projectId, userId);

        ChildTopic childTopic = childTopicRepository.findById(childTopicId)
                .orElseThrow(() -> new BusinessException(ErrorCode.CHILD_TOPIC_NOT_FOUND));

        if (!childTopic.getProject().getId().equals(projectId)) {
            throw new BusinessException(ErrorCode.PROJECT_FORBIDDEN);
        }

        childTopicRepository.delete(childTopic);
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

}
