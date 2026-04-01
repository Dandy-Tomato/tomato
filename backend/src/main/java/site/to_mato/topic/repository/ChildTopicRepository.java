package site.to_mato.topic.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.topic.entity.ChildTopic;
import java.util.List;

public interface ChildTopicRepository extends JpaRepository<ChildTopic, Long> {
    List<ChildTopic> findByTopic_IdAndProject_Id(Long topicId, Long projectId);
}
