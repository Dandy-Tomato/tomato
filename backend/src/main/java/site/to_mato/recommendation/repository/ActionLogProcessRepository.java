package site.to_mato.recommendation.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.recommendation.entity.ActionLogProcess;

import java.util.Optional;

public interface ActionLogProcessRepository extends JpaRepository<ActionLogProcess, Long> {

    Optional<ActionLogProcess> findByActionLogId(Long actionLogId);
}
