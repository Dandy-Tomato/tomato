package site.to_mato.project.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.project.entity.ProjectTopicBookmark;

import java.util.Optional;

public interface ProjectTopicBookmarkRepository extends JpaRepository<ProjectTopicBookmark, Long> {

    Optional<ProjectTopicBookmark> findByProjectIdAndTopicIdAndDeletedAtIsNull(Long projectId, Long topicId);

}
