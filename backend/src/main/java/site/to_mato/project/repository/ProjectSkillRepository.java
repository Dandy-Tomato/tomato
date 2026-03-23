package site.to_mato.project.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.project.entity.ProjectSkill;

import java.util.List;
import java.util.Optional;

public interface ProjectSkillRepository extends JpaRepository<ProjectSkill, Long> {

    List<ProjectSkill> findAllByProject_Id(Long projectId);

    Optional<ProjectSkill> findByProject_IdAndSkill_Id(Long projectId, Long skillId);
}
