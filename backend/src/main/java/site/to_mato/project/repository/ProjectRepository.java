package site.to_mato.project.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

public interface ProjectRepository extends JpaRepository<Project, Long> {

    Optional<Project> findByIdAndDeletedAtIsNull(Long id);

    Optional<Project> findByInviteCodeAndDeletedAtIsNull(String inviteCode);

    boolean existsByInviteCode(String inviteCode);

    List<Project> findAllByIdInAndDeletedAtIsNull(Collection<Long> ids);
}