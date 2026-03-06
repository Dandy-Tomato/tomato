package site.to_mato.catalog.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import site.to_mato.catalog.entity.Skill;

public interface SkillRepository extends JpaRepository<Skill, Long> {
}
