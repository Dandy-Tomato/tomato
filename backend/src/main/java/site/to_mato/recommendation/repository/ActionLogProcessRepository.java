package site.to_mato.recommendation.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.recommendation.entity.ActionLogProcess;

public interface ActionLogProcessRepository extends JpaRepository<ActionLogProcess, Long> {
}
