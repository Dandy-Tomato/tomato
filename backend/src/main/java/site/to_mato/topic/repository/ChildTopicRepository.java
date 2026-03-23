package site.to_mato.topic.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.topic.entity.ChildTopic;

public interface ChildTopicRepository extends JpaRepository<ChildTopic, Long> {
}
