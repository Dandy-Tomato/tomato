package site.to_mato.project.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.project.entity.Project;

public interface ProjectRepository extends JpaRepository<Project, Long> {
}
