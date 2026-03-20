package site.to_mato.project.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.project.entity.ProjectMember;

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
}
