package site.to_mato.project.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.project.entity.ProjectSkill;

import java.util.List;
import java.util.Optional;

public interface ProjectSkillRepository extends JpaRepository<ProjectSkill, Long> {

    List<ProjectSkill> findAllByProjectIdAndProjectDeletedAtIsNull(Long projectId);

    Optional<ProjectSkill> findByProjectIdAndSkillIdAndProjectDeletedAtIsNull(
            Long projectId,
            Long skillId
    );
}
