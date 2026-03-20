package site.to_mato.project.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.project.entity.ProjectSkill;

import java.util.List;

public interface ProjectSkillRepository extends JpaRepository<ProjectSkill, Long> {

    List<ProjectSkill> findAllByProjectIdOrderByWeightDescIdAsc(Long projectId);

    void deleteAllByProjectId(Long projectId);
}