package site.to_mato.recommendation.service;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import org.springframework.transaction.annotation.Transactional;

import lombok.RequiredArgsConstructor;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.project.entity.Project;
import site.to_mato.project.entity.ProjectTopicReaction;
import site.to_mato.project.repository.ProjectDomainRepository;
import site.to_mato.project.repository.ProjectRepository;
import site.to_mato.project.repository.ProjectTopicBookmarkRepository;
import site.to_mato.project.repository.ProjectTopicReactionRepository;
import site.to_mato.recommendation.dto.request.RecommendationRequest;
import site.to_mato.recommendation.dto.response.RecommendationApiResponse;
import site.to_mato.recommendation.dto.response.RecommendationDetailResponse;
import site.to_mato.recommendation.dto.response.RecommendationResponse;
import site.to_mato.recommendation.client.RecommendationClient;
import site.to_mato.topic.dto.response.ChildTopicDetailResponse;
import site.to_mato.topic.entity.ChildTopic;
import site.to_mato.topic.repository.ChildTopicRepository;
import site.to_mato.topic.entity.Topic;
import site.to_mato.topic.repository.TopicRepository;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class RecommendationService {

    private final ProjectDomainRepository projectDomainRepository;
    private final ProjectRepository projectRepository;
    private final RecommendationClient recommendationClient;
    private final TopicRepository topicRepository;
    private final ProjectTopicBookmarkRepository projectTopicBookmarkRepository;
    private final ProjectTopicReactionRepository projectTopicReactionRepository;
    private final ChildTopicRepository childTopicRepository;

    // 프로젝트 별 추천 주제 조회
    public List<RecommendationResponse> getRecommendationsByProjectId(Long projectId) {

        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PROJECT_NOT_FOUND));

        List<Long> domainIds = projectDomainRepository.findByProjectId(projectId).stream()
                .map(projectDomain -> projectDomain.getDomain().getId())
                .toList();

        List<Float> preferenceEmbedding = null;
        Optional<String> embeddingStr = projectRepository.findPreferenceEmbeddingById(projectId);
        if (embeddingStr.isPresent()) {
            String cleaned = embeddingStr.get().replaceAll("[\\[\\]\\s]", "");
            preferenceEmbedding = Arrays.stream(cleaned.split(","))
                    .map(Float::parseFloat)
                    .collect(Collectors.toList());
        }

        RecommendationRequest request = new RecommendationRequest(
                projectId,
                domainIds,
                preferenceEmbedding
        );

        RecommendationApiResponse apiResponse = recommendationClient.getRecommendations(request);

        return apiResponse.data().stream()
                .map(item -> {
                    boolean isBookmarked = projectTopicBookmarkRepository
                            .findByProject_IdAndTopic_Id(projectId, item.topicId())
                            .isPresent();

                    return RecommendationResponse.of(
                            item.topicId(),
                            item.title(),
                            item.description(),
                            item.expectedDurationWeek(),
                            item.recommendedTeamSize(),
                            item.difficulty(),
                            item.domainId(),
                            item.domainName(),
                            item.skills(),
                            isBookmarked
                    );
                })
                .toList();
    }

    public RecommendationDetailResponse getRecommendationDetail(Long projectId, Long topicId) {
        Topic topic =  topicRepository.findByIdWithSkills(topicId).orElseThrow(() -> new BusinessException(ErrorCode.TOPIC_NOT_FOUND));
        List<Long> skillIds = topic.getTopicSkills().stream().map(ts -> ts.getSkill().getId()).toList();

        boolean isBookmarked = projectTopicBookmarkRepository.findByProject_IdAndTopic_Id(projectId, topicId).isPresent();

        Optional<ProjectTopicReaction> reactionOpt =
                projectTopicReactionRepository.findByProject_IdAndTopic_Id(projectId, topicId);

        String isReaction = reactionOpt
                .map(r -> r.getReaction().name())
                .orElse(null);

        Long reactionVersion = reactionOpt
                .map(ProjectTopicReaction::getVersion)
                .orElse(null);

        List<ChildTopic> childTopics = childTopicRepository.findByTopic_IdAndProject_Id(topicId, projectId);
        List<ChildTopicDetailResponse> childTopicInfos = childTopics.stream()
                .map(ChildTopicDetailResponse::from)
                .collect(Collectors.toList());

        return RecommendationDetailResponse.of(
                topic.getId(),
                topic.getTitle(),
                topic.getDescription(),
                topic.getExpectedDurationWeek(),
                topic.getRecommendedTeamSize(),
                topic.getDomain().getId(),
                skillIds,
                isBookmarked,
                isReaction,
                reactionVersion,
                childTopicInfos
        );
    }
}
