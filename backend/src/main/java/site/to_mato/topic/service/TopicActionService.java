package site.to_mato.topic.service;

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
import site.to_mato.topic.entity.ProjectTopicReaction;
import site.to_mato.topic.entity.Topic;
import site.to_mato.topic.entity.enums.Reaction;
import site.to_mato.topic.repository.ProjectTopicReactionRepository;
import site.to_mato.topic.repository.TopicRepository;

@Service
@RequiredArgsConstructor
public class TopicActionService {

    private final ProjectTopicReactionRepository reactionRepository;
    private final ProjectRepository projectRepository;
    private final TopicRepository topicRepository;

    @Transactional
    public void react(Long projectId, Long topicId, Reaction reaction) {

        ProjectTopicReaction reactionEntity =
                reactionRepository
                        .findByProjectIdAndTopicId(projectId, topicId)
                        .orElse(null);
        try {
            if (reactionEntity == null) {
                createReaction(projectId, topicId, reaction);
                return;
            }

            if (reactionEntity.getReaction() == reaction) {
                deleteReaction(reactionEntity);
                return;
            }
            reactionEntity.changeReaction(reaction);
            reactionRepository.flush();
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

}
