package site.to_mato.topic.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.topic.entity.Topic;

public interface TopicRepository extends JpaRepository<Topic, Long> {
}
