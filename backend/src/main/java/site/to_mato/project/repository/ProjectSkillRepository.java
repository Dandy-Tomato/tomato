package site.to_mato.project.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.project.entity.ProjectSkill;

import java.util.Optional;

public interface ProjectSkillRepository extends JpaRepository<ProjectSkill, Long> {

    Optional<ProjectSkill> findByProjectIdAndSkillIdAndProjectDeletedAtIsNull(
            Long projectId,
            Long skillId
    );
}
