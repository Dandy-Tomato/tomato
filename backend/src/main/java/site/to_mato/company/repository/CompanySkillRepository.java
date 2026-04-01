package site.to_mato.company.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import site.to_mato.catalog.entity.Skill;
import site.to_mato.company.entity.CompanySkill;

import java.util.List;

public interface CompanySkillRepository extends JpaRepository<CompanySkill, Long> {

    @Query("""
                select distinct cs.skill
                from CompanySkill cs
                where cs.company.id in :companyIds
                  and cs.skill is not null
            """)
    List<Skill> findDistinctSkillsByCompanyIds(@Param("companyIds") List<Long> companyIds);
}
