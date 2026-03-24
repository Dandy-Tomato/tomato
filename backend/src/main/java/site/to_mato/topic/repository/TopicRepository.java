package site.to_mato.topic.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import site.to_mato.topic.entity.Topic;

import java.util.Optional;

public interface TopicRepository extends JpaRepository<Topic, Long> {

    @Query("SELECT t FROM Topic t " +
            "JOIN FETCH t.topicSkills ts " +
            "JOIN FETCH ts.skill " +
            "JOIN FETCH t.domain " +
            "WHERE t.id = :topicId")
    Optional<Topic> findByIdWithSkills(Long topicId);
}
