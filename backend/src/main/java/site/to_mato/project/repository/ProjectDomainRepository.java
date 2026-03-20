package site.to_mato.project.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.project.entity.ProjectDomain;

import java.util.List;

public interface ProjectDomainRepository extends JpaRepository<ProjectDomain, Long> {

    List<ProjectDomain> findAllByProjectId(Long projectId);

    void deleteAllByProjectId(Long projectId);
}