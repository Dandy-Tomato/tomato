package site.to_mato.project.service;

import jakarta.persistence.OptimisticLockException;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.orm.ObjectOptimisticLockingFailureException;
import org.springframework.stereotype.Service;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.project.dto.request.ReactionRequest;
import site.to_mato.project.dto.response.ProjectTopicReactionResponse;
import site.to_mato.project.entity.Project;
import site.to_mato.project.entity.ProjectTopicReaction;
import site.to_mato.project.entity.enums.Reaction;
import site.to_mato.project.repository.ProjectRepository;
import site.to_mato.project.repository.ProjectTopicReactionRepository;
import site.to_mato.recommendation.entity.enums.ActionType;
import site.to_mato.recommendation.service.ActionLogService;
import site.to_mato.topic.entity.Topic;
import site.to_mato.topic.repository.TopicRepository;

import java.util.Objects;

@Service
@RequiredArgsConstructor
public class ProjectTopicReactionService {

    private final TopicRepository topicRepository;
    private final ActionLogService actionLogService;
    private final ProjectRepository projectRepository;
    private final ProjectTopicReactionRepository reactionRepository;

    @Transactional
    public ProjectTopicReactionResponse setReaction(
            Long actorUserId,
            Long projectId,
            Long topicId,
            ReactionRequest request
    ) {
        Reaction reaction = request.reaction();
        Long version = request.version();

        ProjectTopicReaction reactionEntity =
                reactionRepository
                        .findByProject_IdAndTopic_Id(projectId, topicId)
                        .orElse(null);

        try {
            if (reactionEntity == null) {
                if (version != null) {
                    throw new BusinessException(ErrorCode.REACTION_CONFLICT);
                }

                ProjectTopicReaction createdReaction = createReaction(projectId, topicId, reaction);
                createActionLog(actorUserId, projectId, topicId, reaction);

                return ProjectTopicReactionResponse.of(
                        createdReaction.getReaction().name(),
                        createdReaction.getVersion()
                );
            }

            if (!Objects.equals(reactionEntity.getVersion(), version)) {
                throw new BusinessException(ErrorCode.REACTION_CONFLICT);
            }

            if (reactionEntity.getReaction() == reaction) {
                deleteReaction(reactionEntity);
                return ProjectTopicReactionResponse.of(null, null);
            }

            reactionEntity.changeReaction(reaction);
            reactionRepository.flush();
            createActionLog(actorUserId, projectId, topicId, reaction);

            return ProjectTopicReactionResponse.of(
                    reactionEntity.getReaction().name(),
                    reactionEntity.getVersion()
            );

        } catch (ObjectOptimisticLockingFailureException | OptimisticLockException | DataIntegrityViolationException e) {
            throw new BusinessException(ErrorCode.REACTION_CONFLICT);
        }
    }

    private ProjectTopicReaction createReaction(Long projectId, Long topicId, Reaction reaction) {
        Project project = projectRepository.getReferenceById(projectId);
        Topic topic = topicRepository.getReferenceById(topicId);

        ProjectTopicReaction reactionEntity = ProjectTopicReaction.of(project, topic, reaction);
        reactionRepository.save(reactionEntity);
        reactionRepository.flush();
        return reactionEntity;
    }

    private void deleteReaction(ProjectTopicReaction reactionEntity) {
        reactionRepository.delete(reactionEntity);
        reactionRepository.flush();
    }

    private void createActionLog(Long actorUserId, Long projectId, Long topicId, Reaction reaction) {
        actionLogService.createActionLog(
                actorUserId,
                projectId,
                topicId,
                toActionType(reaction)
        );
    }

    private ActionType toActionType(Reaction reaction) {
        return switch (reaction) {
            case LIKE -> ActionType.LIKE;
            case DISLIKE -> ActionType.DISLIKE;
        };
    }
}
