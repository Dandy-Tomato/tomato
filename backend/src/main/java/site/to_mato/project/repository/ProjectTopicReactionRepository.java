package site.to_mato.project.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.project.entity.ProjectTopicReaction;

import java.util.Optional;

public interface ProjectTopicReactionRepository extends JpaRepository<ProjectTopicReaction, Long> {

    Optional<ProjectTopicReaction> findByProjectIdAndTopicId(Long projectId, Long topicId);

    void deleteByProjectIdAndTopicId(Long projectId, Long topicId);

}
