package site.to_mato.company.entity;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import site.to_mato.catalog.entity.Skill;

@Getter
@Entity
@Table(
        name = "company_skills",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_company_skill",
                        columnNames = {"company_id", "skill_id"}
                )
        },
        indexes = {
                @Index(name = "idx_company_skill_company", columnList = "company_id"),
                @Index(name = "idx_company_skill_skill", columnList = "skill_id")
        }
)
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class CompanySkill {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "company_skill_id")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "company_id")
    private Company company;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "skill_id")
    private Skill skill;

    @Builder
    private CompanySkill(Company company, Skill skill) {
        this.company = company;
        this.skill = skill;
    }

    public static CompanySkill of(Company company, Skill skill) {
        return CompanySkill.builder()
                .company(company)
                .skill(skill)
                .build();
    }
}
