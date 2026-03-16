package site.to_mato.project.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.project.entity.ProjectDomain;

public interface ProjectDomainRepository extends JpaRepository<ProjectDomain, Long> {

    // project_id로 project_domain 조회
    List<ProjectDomain> findByProjectId(Long projectId);

}
