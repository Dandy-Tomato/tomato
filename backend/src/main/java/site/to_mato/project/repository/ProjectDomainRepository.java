package site.to_mato.project.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import site.to_mato.project.entity.ProjectDomain;

public interface ProjectDomainRepository extends JpaRepository<ProjectDomain, Long> {

    // project_id로 project_domain 조회
    @Query("SELECT pd FROM ProjectDomain pd JOIN FETCH pd.domain WHERE pd.project.id = :projectId")
    List<ProjectDomain> findByProjectId(@Param("projectId") Long projectId);

}
