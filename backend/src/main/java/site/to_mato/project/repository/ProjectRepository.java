package site.to_mato.project.repository;

import io.lettuce.core.dynamic.annotation.Param;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import site.to_mato.project.entity.Project;

import java.util.Optional;

public interface ProjectRepository extends JpaRepository<Project, Long> {

    @Query(value = "SELECT preference_embedding::text FROM projects WHERE project_id = :projectId AND preference_embedding IS NOT NULL", nativeQuery = true)
    Optional<String> findPreferenceEmbeddingById(@Param("projectId") Long projectId);

    boolean existsByInviteCodeAndDeletedAtIsNull(String inviteCode);

    Optional<Project> findByIdAndDeletedAtIsNull(Long projectId);

    Optional<Project> findByInviteCodeAndDeletedAtIsNull(String inviteCode);
}
