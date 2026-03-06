package site.to_mato.user.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.user.entity.UserSkill;

public interface UserSkillRepository extends JpaRepository<UserSkill, Long> {
}
