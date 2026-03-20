package site.to_mato.user.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.user.entity.User;
import site.to_mato.user.entity.UserSkill;

import java.util.List;

public interface UserSkillRepository extends JpaRepository<UserSkill, Long> {

    List<UserSkill> findAllByUser_IdAndUser_DeletedAtIsNull(Long userId);

    void deleteAllByUser(User user);
}
