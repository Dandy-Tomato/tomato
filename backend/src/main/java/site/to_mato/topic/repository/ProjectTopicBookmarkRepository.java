package site.to_mato.topic.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.topic.entity.ProjectTopicBookmark;

public interface ProjectTopicBookmarkRepository extends JpaRepository<ProjectTopicBookmark, Long> {

    boolean existsByProjectIdAndTopicId(Long projectId, Long topicId);
    void deleteByProjectIdAndTopicId(Long projectId, Long topicId);

}
