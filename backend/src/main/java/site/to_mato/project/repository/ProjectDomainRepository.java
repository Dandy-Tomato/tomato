package site.to_mato.project.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import site.to_mato.project.entity.ProjectDomain;

public interface ProjectDomainRepository extends JpaRepository<ProjectDomain, Long> {

    // project_id로 project_domain 조회
    @Query("SELECT pd FROM ProjectDomain pd JOIN FETCH pd.domain WHERE pd.project.id = :projectId")
    List<ProjectDomain> findByProjectId(@Param("projectId") Long projectId);

    List<ProjectDomain> findAllByProject_Id(Long projectId);

    Optional<ProjectDomain> findByProject_IdAndDomain_Id(Long projectId, Long domainId);
}
