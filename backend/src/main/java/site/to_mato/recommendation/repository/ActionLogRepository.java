package site.to_mato.recommendation.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.recommendation.entity.ActionLog;

public interface ActionLogRepository extends JpaRepository<ActionLog, Long> {
}
