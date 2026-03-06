package site.to_mato.user.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.user.entity.User;

import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByEmailAndDeletedAtIsNull(String email);

    boolean existsByEmail(String email);
}
