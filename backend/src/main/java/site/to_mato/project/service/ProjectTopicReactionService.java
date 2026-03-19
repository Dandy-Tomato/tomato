package site.to_mato.project.service;

import jakarta.persistence.OptimisticLockException;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.orm.ObjectOptimisticLockingFailureException;
import org.springframework.stereotype.Service;
import site.to_mato.common.exception.BusinessException;
import site.to_mato.common.exception.ErrorCode;
import site.to_mato.project.entity.Project;
import site.to_mato.project.repository.ProjectRepository;
import site.to_mato.recommendation.entity.enums.ActionType;
import site.to_mato.recommendation.service.ActionLogService;
import site.to_mato.project.entity.ProjectTopicReaction;
import site.to_mato.topic.entity.Topic;
import site.to_mato.project.entity.enums.Reaction;
import site.to_mato.project.repository.ProjectTopicReactionRepository;
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
    public void setReaction(Long actorUserId, Long projectId, Long topicId, Reaction reaction, Long version) {

        ProjectTopicReaction reactionEntity =
                reactionRepository
                        .findByProjectIdAndTopicId(projectId, topicId)
                        .orElse(null);

        try {
            if (reactionEntity == null) {
                // 기존(DB)에 데이터가 없는데 클라이언트가 버전을 보내온 경우 충돌(이미 삭제됨)
                if (version != null) {
                    throw new BusinessException(ErrorCode.REACTION_CONFLICT);
                }
                createReaction(projectId, topicId, reaction);
                createActionLog(actorUserId, projectId, topicId, reaction);
                return;
            }

            // 클라이언트에서 보낸 버전이 기존 버전(DB)과 다를 경우 충돌 발생(다른 누군가 상태 변경)
            if (!Objects.equals(reactionEntity.getVersion(), version)) {
                throw new BusinessException(ErrorCode.REACTION_CONFLICT);
            }

            if (reactionEntity.getReaction() == reaction) {
                deleteReaction(reactionEntity);
                return;
            }

            reactionEntity.changeReaction(reaction);
            reactionRepository.flush();
            createActionLog(actorUserId, projectId, topicId, reaction);

        } catch (ObjectOptimisticLockingFailureException | OptimisticLockException | DataIntegrityViolationException e) {
            throw new BusinessException(ErrorCode.REACTION_CONFLICT);
        }
    }

    private void createReaction(Long projectId, Long topicId, Reaction reaction) {
        Project project = projectRepository.getReferenceById(projectId);
        Topic topic = topicRepository.getReferenceById(topicId);

        ProjectTopicReaction reactionEntity = ProjectTopicReaction.of(project, topic, reaction);
        reactionRepository.save(reactionEntity);
        reactionRepository.flush();
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
