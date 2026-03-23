package site.to_mato.project.repository;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import site.to_mato.project.entity.ProjectMember;

import java.util.List;
import java.util.Optional;

public interface ProjectMemberRepository extends JpaRepository<ProjectMember, Long> {

    boolean existsByProjectIdAndUserIdAndProjectDeletedAtIsNullAndUserDeletedAtIsNull(
            Long projectId,
            Long userId
    );

    Optional<ProjectMember> findByProjectIdAndUserIdAndProjectDeletedAtIsNullAndUserDeletedAtIsNull(
            Long projectId,
            Long userId
    );

    @EntityGraph(attributePaths = "project")
    Page<ProjectMember> findAllByUserIdAndProjectDeletedAtIsNullAndUserDeletedAtIsNull(
            Long userId,
            Pageable pageable
    );

    @Query("""
                SELECT pm.project.id, COUNT(pm)
                FROM ProjectMember pm
                WHERE pm.project.id IN :projectIds
                  AND pm.project.deletedAt IS NULL
                  AND pm.user.deletedAt IS NULL
                GROUP BY pm.project.id
            """)
    List<Object[]> countMembersByProjectIds(List<Long> projectIds);

    @Query("""
                SELECT pm
                FROM ProjectMember pm
                JOIN FETCH pm.user
                WHERE pm.project.id = :projectId
                  AND pm.project.deletedAt IS NULL
                  AND pm.user.deletedAt IS NULL
            """)
    List<ProjectMember> findAllWithUserByProjectId(Long projectId);
}
